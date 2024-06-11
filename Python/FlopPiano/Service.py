from threading import Thread, Event
from queue import Queue, Empty


from configparser import ConfigParser
from .Conductor import Conductor, Note, OutputMode

from mido.ports import BaseInput, BaseOutput, BasePort
from mido import Message
import mido

import logging


class Configuration():

    @staticmethod
    def default() -> ConfigParser:
        # '#' entries are just comments in the configuration file.
        config = ConfigParser()
        config['Service'] = {
            '#service_type': "['physical', 'virtual']",
            'service_type' : 'physical',    # ['physical', 'virtual']
            '#input_hint'  : 'If physical -> USB interface name hints, if virtual -> port #',
            'input_hint'   : 'some string', # If physical -> USB interface name hints, if virtual -> port #
            '#output_hint' : '# If physical -> USB interface name hints, if virtual -> port #',
            'output_hint'  : 'some string', # If physical -> USB interface name hints, if virtual -> port #
            '#log_file'    : 'Any file path',
            'log_file'     : 'some path',   # Any file path
            '#log_level'   : "['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']",
            'log_level'    : 'INFO'         # ['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
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
        #TODO, what do we do with the config
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
        input_hint = config['Service'].get('input_hint')
        if input_hint is None:
            raise ValueError('[Service]: input_hint not given')

        #TODO: We need to validate this!
        output_hint = config['Service'].get('output_hint')
        if output_hint is None:
            raise ValueError('[Service]: output_hint not given')

        #TODO: dont' do logging if logfile is none!
        log_file = config['Service'].get('log_file')

        log_level = config['Service'].get('log_level',"INFO").upper()
        if (log_level not in logging.getLevelNamesMapping().keys()):
            raise ValueError('[Service]: log_level not '
                            f'{list(logging.getLevelNamesMapping().keys())}')
        log_level = logging.getLevelNamesMapping()[log_level]

        return (service_type, input_hint, output_hint, log_file, log_level)
        
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

         
        # Setup Conductor
        self._conductor = conductor
        if self._conductor is None:
            #TODO: remember to do loopback by default
            self._conductor = Conductor(loopback=False)
            #self._conductor = Conductor()

        # Get the service type
        if service_type != 'physical' and service_type!='virtual':
            raise ValueError("Service type must be 'physical' or 'virtual'")
        #TODO: add virtual support
        if service_type == 'virtual': 
            raise NotImplementedError('virtual service not implemented')

        # Set up ports
        self._midi_input:BaseInput = mido.open_input(
            Service._find_port(input_hint, mido.get_input_names())
        )

        self._midi_output:BaseOutput = mido.open_output(
            Service._find_port(output_hint, mido.get_output_names())
        )

        # Set up logger
        if log_file is not None:
            pass #TODO: set up logging to a file        
        
        self._logger = logging.getLogger(__name__)

        self._stop_event = Event()

        #TODO max sizes for queues is arbitrary and only really needed for the
        #outgoing queue. We don't know if the user will consume outgoing 
        #messages but incoming messages we consume incoming messages as 
        #soon as possible.        
        self._incoming_q = Queue(100)
        self._outgoing_q = Queue(100)

        #All above went well, so we're good to start
        Thread.__init__(self)

    def run(self):
        self._logger.info("Started.")
        while True:
            if (self._stop_event.is_set()): break

            incoming_msgs:list[Message] = []
            outgoing_msgs:list[Message] = []

            #get any incoming messages from the application
            try: incoming_msgs.extend(self._incoming_q.get_nowait())
            except Empty: pass

            #Get the messages from the input
            if(not self._midi_input.closed):
                input_msg = self._midi_input.receive(block=False)
                if input_msg is not None:
                    incoming_msgs.append(input_msg)

            outgoing_msgs = self._conductor.conduct(incoming_msgs)
   
            #try to write the outgoing messages to the output
            if (not self._midi_output.closed and len(outgoing_msgs)>0):
                for msg in outgoing_msgs:
                    self._midi_output.send(msg)

        #Clean up before stopping
        #When quitting make sure the conductor shuts up
        self._logger.info("Cleaning up...")
        self._conductor.silence()
        self._logger.info("Exited.")
        
    def quit(self):
        """_summary_
            Stop the Service Thread
        """
        self._stop_event.set()

    def get(self, **kwargs)->list[Message]:
        """_summary_
            Get the output from the Conductor
            **kwargs are passed to Queue.get() see:
            https://docs.python.org/3/library/queue.html
        Returns:
            list[Message]: The output from the conductor
        """
        self._logger.debug(f'Returning messages from the outgoing queue')
        return self._outgoing_q.get(**kwargs)

    def put(self, messages:list[Message] ,**kwargs):
        """_summary_
            Send Midi messages to the Conductor
            **kwargs are passed to Queue.put() see:
            https://docs.python.org/3/library/queue.html

        Args:
            messages (list[Message]): A list of messages to send to the 
                Conductor
        """
        self._logger.debug(f'Put {len(messages)} messages into incoming queue')
        self._incoming_q.put(messages,**kwargs)

    @staticmethod
    def _find_port(hint:str, options:list[str])->str:
        for option in options:
            if option.startswith(hint.upper()):
                return option

        raise ValueError(f'Could not find port with hint: {hint.upper()}')






