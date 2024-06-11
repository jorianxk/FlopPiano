from threading import Thread, Event
from queue import Queue


from configparser import ConfigParser
from .Conductor import Conductor, Note, OutputMode

from mido.ports import BaseInput, BaseOutput, BasePort
from mido import Message
import mido

import logging
import time

"""
Application

1) read .ini using with open()
2) pass to Configuration() -> Service()
3) Service.start()
4) Do display stuff, push messages to service

"""

class Configuration():

    @staticmethod
    def default() -> ConfigParser:
        config = ConfigParser()
        config['Service'] = {
            '#type'     : "['physical', 'virtual']",
            'type'      : 'physical',    # ['physical', 'virtual']
            '#input'    : 'If physical -> USB interface name hints, if virtual -> port #',
            'input'     : 'some string', # If physical -> USB interface name hints, if virtual -> port #
            '#output'   : '# If physical -> USB interface name hints, if virtual -> port #',
            'output'    : 'some string', # If physical -> USB interface name hints, if virtual -> port #
            '#log_file' : 'Any file path',
            'log_file'  : 'some path',   # Any file path
            '#log_level': "['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']",
            'log_level' : 'INFO'         # ['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
        }

        config['Conductor'] = {
            '#keyboard_address': '[0x8-0x77]',
            'keyboard_address' : 0x77,      # [0x8-0x77]
            '#loopback'        : '[True, False]',
            'loopback'         : False,     # [True, False]
            '#input_channel'   : '[0-16]',
            'input_channel'    : -1,        # [0-16]
            '#output_channel'  : '[0-15]',
            'output_channel'   : 0,        # [0-15]
            '#output_mode'     : "['rollover', 'keys', 'off']",
            'output_mode'      : 'rollover' # ['rollover', 'keys', 'off']
        }


        for drive_num in range(1,11):
            config[f'Drive {drive_num}']={
                '#address':'[0x8-0x77]',
                'address' : drive_num+7,  # [0x8-0x77]
                #'#tuning' : '[[0-9],[0-9],[0-9],[0-9],[0-9],[0-9]]'
                #'tuning'  : '1,2,3,4,5,6' # TODO: depends on how we handle tuning
            }

        return config

    @staticmethod
    def read(config_file_path:str):
        
        config = ConfigParser()
        with open(config_file_path, 'r') as config_file:
            config.read(config_file_path)

        try:
            #Read the server configuration--------------------------------------
            serviceconfigs = Configuration._service_configs(config)

            #Read the Conductor configuration-----------------------------------

            conductorconfigs = Configuration._conductor_configs(config)

            #Read the drive/Note configurations---------------------------------

            noteconfigs =  Configuration._note_configs(config)

        except KeyError as ke:
            raise ValueError(f'Could not find section {ke}') from ke
        except ValueError as ve:
            raise ValueError(f'Bad value: {ve}') from ve

           
    @staticmethod
    def _service_configs(config:ConfigParser):

        service_type = config['Service'].get('type')
        if service_type is None:
            raise ValueError('[Service]: type not given')
        if service_type != 'physical' and service_type != 'virtual':
            print(service_type)
            raise ValueError("[Service]: type not ['physical', 'virtual']")

        #TODO: We need to validate this!
        input = config['Service'].get('input')
        if input is None:
            raise ValueError('[Service]: usb_input not given')

        #TODO: We need to validate this!
        output = config['Service'].get('output')
        if output is None:
            raise ValueError('[Service]: usb_output not given')

        #TODO: dont' do logging if logfile is none!
        log_file = config['Service'].get('log_file')

        log_level = config['Service'].get('log_level',"INFO").upper()
        if (log_level not in logging.getLevelNamesMapping().keys()):
            raise ValueError('[Service]: log_level not '
                            f'{list(logging.getLevelNamesMapping().keys())}')
        log_level = logging.getLevelNamesMapping()[log_level]

        return (service_type, input, output, log_file, log_level)
        
    @staticmethod
    def _conductor_configs(config:ConfigParser):
        
        keyboard_address = config['Conductor'].getint('keyboard_address', 0x77)
        if keyboard_address < 0x8 or keyboard_address > 0x77:
            raise ValueError(f'[Conductor]: keyboard_address not [{0x8}-{0x77}]')
        
        loopback = config['Conductor'].getboolean('loopback', True)
        
        input_channel = config['Conductor'].getint('input_channel', 0)
        if input_channel < -1 or input_channel > 16:
            raise ValueError(f'[Conductor]: input_channel not [0-16]')

        output_channel = config['Conductor'].getint('output_channel', 0)
        if output_channel < 0 or output_channel > 15:
            raise ValueError(f'[Conductor]: output_channel not [0-15]')
        
        output_mode = config['Conductor'].get('output_mode', 'rollover').upper()
        if output_mode not in OutputMode._member_names_:
            raise ValueError('[Conductor]: output_mode not '
                            f'{OutputMode._member_names_}')
        
        output_mode = OutputMode._member_map_[output_mode]

        return (keyboard_address, loopback, output_channel, input_channel, output_mode)

    @staticmethod
    def _note_configs(config:ConfigParser):
        #TODO remember to init notes correctly
        drive_configs:dict[int, str] = {}
        for section in config.sections():
            
            if section.upper().startswith("DRIVE"):
                address = config[section].getint("address")

                if address is None:
                    raise ValueError(f'[{section}]: address not given')
                elif address<0x8 or address >0x77:
                    raise ValueError(f'[Drive]: address not [{0x8}-{0x77}]')
                
                #TODO handle tuning here!
                tuning = config[section].get("tuning")
                if tuning is None:
                    pass #raise ValueError(f'[Drive]: tuning not VALUES HERE')
                
                drive_configs[address] = tuning

        return drive_configs






class Service(Thread):

    def __init__(
        self,
        conductor:Conductor = None, 
        service_type:str = 'physical', 
        input_hint:str = "USB", 
        output_hint:str = "USB", 
        log_file:str = None, 
        log_level:int = logging.INFO):

        """_summary_

        Raises:
            ValueError: _description_
            NotImplementedError: _description_
        """
        
        # Setup Conductor
        self._conductor = conductor
        if self._conductor is None:
            self._conductor = Conductor()

        # Get the service type
        if service_type != 'physical' and service_type!='virtual':
            raise ValueError("Service type must be 'physical' or 'virtual'")
        #TODO: add virtual support
        if service_type == 'virtual': raise NotImplementedError('virtual service not implemented')

        # Set up ports
        self._input:BaseInput = mido.open_input(
            Service._find_port(input_hint, mido.get_input_names())
        )

        self._output:BaseOutput = mido.open_output(
            Service._find_port(output_hint, mido.get_output_names())
        )

        # Set up logger
        if log_file is not None:
            pass #TODO: set up logging to a file        
        
        self._logger = logging.getLogger(__name__)

        self._stop_event = Event()
        self._incoming = Queue()
        self._outgoing = Queue()

        #All above went well, so we're good to start
        Thread.__init__(self)

    def run(self):
        while True:
            if self._stop_event.is_set(): break

            print("Service:", "loop")
            time.sleep(0.5)
        
    def quit(self):
        self._stop_event.set()

    @staticmethod
    def _find_port(hint:str, options:list[str])->str:
        for option in options:
            if option.startswith(hint.upper()):
                return option

        raise ValueError(f'Could not find port with hint: {hint.upper()}')






