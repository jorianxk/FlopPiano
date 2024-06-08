from collections.abc import Callable
from threading import Thread, Event
from queue import Queue
from configparser import ConfigParser
from FlopPiano.Conductor import Conductor, Note, OutputMode
import logging
import time





class ConductorService(Thread):

    def __init__(self, config_file:str=None):
        
        if(config_file is None):
            #get the default config
            pass
        else:
            #attempt to read the file
            pass

        

        
        Thread.__init__(self)  



        self.stop_event = Event()
        self.incoming = Queue()
        self.outgoing = Queue()

    def run(self):
        while True:
            if self.stop_event.is_set(): break

            print("Service:", "loop")
            time.sleep(0.5)
        
    def quit(self):
        self.stop_event.set()


    def readConfig(self, config_file):
        config = ConfigParser()
        
        with open(config_file) as f:
            config.read_file(f)

        try:

            #Read the server configuration--------------------------------------
            #TODO: We need to validate this!
            usb_input = config['Server'].get('usb_input')
            if usb_input is None:
                raise ValueError('[Server]: usb_input not given')

            #TODO: We need to validate this!
            usb_output = config['Server'].get('usb_output')
            if usb_output is None:
                raise ValueError('[Server]: usb_output not given')

            #TODO: dont' do logging if logfile is none!
            log_file = config['Server'].get('log_file')
            
            log_level = config['Server'].get('log_level',"INFO").upper()
            if (log_level not in logging.getLevelNamesMapping().keys()):
                raise ValueError('[Server]: log_level not '
                                f'{list(logging.getLevelNamesMapping().keys())}')

            #Read the Conductor configuration-----------------------------------

            keyboard_address = config['Conductor'].getint('keyboard_address', 0x77)
            if keyboard_address < 0x8 or keyboard_address > 0x77:
                raise ValueError(f'[Conductor]: keyboard_address not [{0x8}-{0x77}]')
            
            loopback = config['Conductor'].getboolean('loopback', True)
            
            output_channel = config['Conductor'].getint('output_channel', 0)
            if output_channel < 0 or output_channel > 15:
                raise ValueError(f'[Conductor]: output_channel not [0-15]')
            
            input_channel = config['Conductor'].getint('input_channel', 0)
            if output_channel < 0 or output_channel > 16:
                raise ValueError(f'[Conductor]: output_channel not [0-16]')
            
            output_mode = config['Conductor'].get('output_mode', 'rollover').upper()
            if output_mode not in OutputMode._member_names_:
                raise ValueError('[Conductor]: output_mode not '
                                f'{OutputMode._member_names_}')
            
            output_mode = OutputMode._member_map_[output_mode]

            #Read the drive configurations--------------------------------------

            #TODO remember to init notes correctly
            notes:list[Note] = [] 

            for section in config.sections():
                
                if section.upper().startswith("DRIVE"):
                    address = config[section].getint("address")

                    if address is None:
                        raise ValueError(f'[{section}]: address not given')
                    elif address<0x8 or address >0x77:
                        raise ValueError(f'[Conductor]: address not [{0x8}-{0x77}]')
                    
                    #TODO handle tuning here!
                    note = Note(None,address)
                    notes.append(note)

        except KeyError as ke:
            raise ValueError(f'Could not find section {ke}')
        except ValueError as ve:
            raise ValueError(f'Bad value/wrong type {ve}')




cs = ConductorService(None)
cs.start()



try:    

    while True: 
        time.sleep(1)
        print("Main:", "loop")

except KeyboardInterrupt as ke:
    print("Main:"," KeyboardInterrupt doing exit...")
finally:
    print("Main:","Issuing thread quit()")
    cs.quit()
    print("Main","Waiting for thread join()")
    cs.join()


    print("Main","Done.")



