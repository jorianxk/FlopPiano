import time
import argparse
import textwrap
import mido
from mido.ports import BaseInput, BaseOutput

import floppiano.bus as bus
from floppiano import VERSION, FlopPianoApp
from floppiano.devices import DeviceDiscovery
from floppiano.synths import DriveSynth

from asciimatics.screen import Screen, ManagedScreen
from asciimatics.widgets.utilities import THEMES
from asciimatics.event import KeyboardEvent
import logging

class Startup():
    """
    A class to create FlopPianoApp with appropriate settings from command-
    line arguments.
    """
    def __init__(self) -> None:
        # An asciimatics screen to draw with    
        self._screen:Screen = None
        # Current y position to print at
        self._line = 0

    def get_app(self) -> FlopPianoApp:
        """
            Returns a FlopPianoApp with appropriate startup settings. Prompts
            for user input when there is an error, finds I2C Devices, finds MIDI
            interfaces, and configures settings.
        """
        # Parse cli arguments
        args = self.parse_args()

        # Create a screen to draw with
        with ManagedScreen() as screen:
            self._screen = screen    
            self.print(f'------------- FlopPiano Startup -------------',
                       Screen.COLOUR_GREEN,
                       True)

            drive_addresses = []
            keyboard_address = None
            input_port = None
            output_port = None

            # Are we using the normal I2C bus?
            if not args.debugbus:
                # Try to find the devices
                drive_addresses, keyboard_address = self.find_devices()
                self.print(f'Found keyboard: {str(keyboard_address)}')
                self.print(f'Found drives: {drive_addresses}')
                #No keyboard found and we intended to use a keyboard
                if keyboard_address is None and not args.nokeyboard:
                    self.print('No keyboard was detected.', Screen.COLOUR_RED)
                    self.prompt_for_exit()
                    self.print('Continuing without keyboard.')
                    # Don't use the keyboard
                    args.nokeyboard = True

                #No drives found
                if len(drive_addresses) == 0:
                    self.print('No drives were detected.',
                                Screen.COLOUR_RED)
                    self.prompt_for_exit()
                    self.print('Continuing with the debus bus.')
                    # Use the debug bus
                    args.debugbus = True

            
            self.print('-' * self._screen.width)

            # Check that the debug bus flag was not changed from the above
            if args.debugbus:
                # Use the debug bus
                bus.default_bus(bus.DebugBus())
                # Arbitrary dummy drive addresses
                drive_addresses = [i for i in range(8, 18)]
                # Arbitrary dummy keyboard address
                keyboard_address = 119
            
            # Should MIDI interfaces be used?
            if not args.noports: 
                # Find them
                input_port, output_port = self.find_ports()
                self.print('-' * self._screen.width)
            
            self.print(f'Starting FlopPiano v{VERSION}...', 
                       Screen.COLOUR_GREEN,
                       True)
            time.sleep(1)

       
        if args.logfile is not None:
            # disable all other loggers
            for name in logging.root.manager.loggerDict:
                logging.getLogger(name).disabled = True
            # set up logging
            logging.basicConfig(filename=args.logfile, level = args.loglevel, filemode='w+')

        return FlopPianoApp(
            DriveSynth(drive_addresses),
            #keyboard= None, # TODO Keyboard(keyboard_addr)
            input_port = input_port,
            output_port = output_port,
            theme = args.theme,
            splash_start = args.nosplash, 
            screen_timeout = args.screentimeout)
    
    def parse_args(self) -> argparse.Namespace:
        """
            Returns the parsed command line arguments
        """ 
        parser = argparse.ArgumentParser()
        parser.add_argument('-nk',
                            '--nokeyboard', 
                            help = "Disables the piano keys", 
                            action = 'store_true')

        parser.add_argument('-db',
                            '--debugbus', 
                            help = 'Use the dummy (debug) I2C bus', 
                            action = 'store_true')

        parser.add_argument('-np',
                            '--noports', 
                            help = 'Disables MIDI interfaces', 
                            action = 'store_true')

        parser.add_argument('-t',
                            '--theme', 
                            help = 'Specifies the UI theme', 
                            action = 'store',
                            choices = THEMES.keys(),
                            default = 'default')

        parser.add_argument('-ns',
                            '--nosplash', 
                            help='Disables the splash screen', 
                            action='store_false')

        parser.add_argument('-st',
                            '--screentimeout', 
                            help = 'Specifies screensaver timeout in seconds. 0=off', 
                            type = int,
                            metavar = 'TIME',
                            default = 300)
        
        parser.add_argument('-lf',
                    '--logfile', 
                    help = 'Specifies a logfile to use',                     
                    metavar = 'FILE')
       
        parser.add_argument('-ll',
            '--loglevel', 
            help = 'Specifies a loglevel to use (effective only if -lf is given).',                     
            metavar = 'LEVEL',
            choices= logging._nameToLevel.keys(),
            default = 'INFO')

        # parse the args
        args = parser.parse_args()

        # Force the screentimeout to be positive or None (disabled)
        args.screentimeout = abs(args.screentimeout)
        if args.screentimeout == 0: args.screentimeout = None

        return args

    def find_devices(self) -> tuple[list[int], int]:
        """
           Finds drives and the keyboard on I2C bus using another thread.
           (so that the UI may be updated)
        Returns:
            tuple[list[int], int]: A list of drive I2C addresses and the 
            keyboard I2C address
        """
        self.print('Detecting devices...', bold=True)
        self.print('(If this takes a while a bus issue is likely)')
        self.print('Press any key to abort')
        self.print('    Scanning I2C bus...') 

        # A time to update the UI
        elapsed = time.time()

        # A special Thread object to find devices
        discovery = DeviceDiscovery()
        discovery.start() # Start the thread

        # While the thread is working...
        while discovery.is_alive():
            # Print something so the user knows something is happening
            if time.time() - elapsed > 2:
                self.print('    Scanning I2C bus...') 
                elapsed = time.time()

            # Handle the abort
            if self.key_pressed() is not None:
                self.print('    Aborting...')
                discovery.quit()
                discovery.join()
                break
        
        self.print("Done.")

        return (discovery.get_devices())

    def find_ports(self) -> tuple[BaseInput, BaseOutput]:
        """
            Finds the MIDI USB interfaces for input and output
        Returns:
            tuple[BaseInput, BaseOutput]: The MIDI input and output ports
        """
        self.print('Detecting MIDI interfaces...', bold=True)
        input_port = None
        output_port = None

        for option in mido.get_input_names():
            if option.startswith('USB'):
                input_port = mido.open_input(option)
                self.print(f'Found input: {option}')
                break
        
        for option in mido.get_output_names():
            if option.startswith('USB'):
                output_port = mido.open_output(option)
                self.print(f'Found output: {option}')
                break
        
        if input_port is None:
            self.print('No MIDI input interface was detected.'
                       , color = Screen.COLOUR_RED)
            self.prompt_for_exit()
            self.print('Continuing without input interface.')
            

        if output_port is None:
            self.print("No MIDI output interface was detected."
                       , color = Screen.COLOUR_RED)
            self.prompt_for_exit()
            self.print('Continuing without output interface.')

        self.print("Done.")
        return (input_port, output_port)

    def key_pressed(self) -> KeyboardEvent:
        """
            Checks for (computer) keyboard presses
        Returns:
            KeyboardEvent: Returns the Keyboard event or None if no key was 
            pressed 
        """
        event = self._screen.get_event()
        if isinstance(event, KeyboardEvent): return event
        return None

    def wait_for_key(self, key) -> bool:
        """
            Waits until any key is pressed. 
        Args:
            key (_type_): The key to test for i.e ord('f')

        Returns:
            bool: True, if the key specified was pressed. False otherwise
        """
        event = None
        while True: 
            event = self.key_pressed()
            if event is not None: break
        
        if event.key_code == key: return True

        return False

    def prompt_for_exit(self):
        """
            Asks the user to press <enter> to continue. If any other key is
            pressed the program is ended immediately 
        """
        self.print('Press <enter> to continue or any other key to quit:',
                   color= Screen.COLOUR_YELLOW)
        if not self.wait_for_key(ord('\n')): exit(0)

    def print(self, obj, color:int = 7, bold = False):
        """
            Prints text to the console
        Args:
            obj (_type_): The thing to be printed str(obj)
            color (int, optional): The color to use Defaults to 7 (asciimatics
            default).
            bold (bool, optional): If the text should be bold. 
            Defaults to False.
        """
        string = str(obj)
        # Handle text wrapping
        if len(string) > self._screen.width:
            wrapped = textwrap.wrap(string, self._screen.width)
            for line in wrapped:
                self.print(line, color, bold)
            return

        if self._line >= self._screen.height:
            self._screen.scroll()  
        
        self._screen.print_at(string, 0, self._line, colour=color, attr = bold) 
        self._line +=1       
        self._screen.refresh()

if __name__ == '__main__': 
    #Remove this theme.. it does not work on Raspberry Pi (headless)
    THEMES.pop('tlj256')
    Startup().get_app().run()

# TODO: Find assets?
# def _find_assets(self):
#     self.logger.debug(f"Verifying asset directory: '{self._asset_dir}'")
#     if not os.path.isdir(self._asset_dir):
#         self.logger.critical(
#             f"Asset directory '{self._asset_dir} not'found. exiting...")
#         raise RuntimeError("Could not find assets")
#     self.logger.debug(f"Found asset directory: '{self._asset_dir}'")
