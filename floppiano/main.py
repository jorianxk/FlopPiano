import sys
import floppiano.bus as bus
from floppiano import VERSION, FlopPianoApp
from floppiano.devices.drives import Drives, DEVICE_TYPE, DEVICE_TYPE_REG
from floppiano.synths import DriveSynth
from floppiano.UI.tabs import Tab, TabHeader
from asciimatics.screen import Screen
import mido
from mido.ports import BaseInput, BaseOutput


# def _find_assets(self):
#     self.logger.debug(f"Verifying asset directory: '{self._asset_dir}'")
#     if not os.path.isdir(self._asset_dir):
#         self.logger.critical(
#             f"Asset directory '{self._asset_dir} not'found. exiting...")
#         raise RuntimeError("Could not find assets")
#     self.logger.debug(f"Found asset directory: '{self._asset_dir}'")


def find_devices() -> tuple[list[int], int]:
    # ping all i2c devices from from 0x8 to 0x77 and get their device type, 
    # if the type is correct add it to the list
    print('Detecting Devices...')
    print("    [If this takes a bus issue is likely]")
    drive_addresses  = []
    piano_keys = None
    for address in range(0x8, 0x77+1):
        try:
            response = bus.read(address, DEVICE_TYPE_REG, 1)[0]
            if response == DEVICE_TYPE: 
                drive_addresses.append(address)
                print(f'    Found floppy drive at address: {address}')
            if response == 55: #TODO fix this 
                keyboard = address
                print(f'    Found keyboard at address: {address}')
        except Exception:
            print(f'    No device at address: {address}')
    
    if len(drive_addresses) == 0:
        try:
            print("WARNING: No drives were found")
            print("Press enter to continue or ctrl+c to quit")
            input('')
        except KeyboardInterrupt:
            exit(0)

    if piano_keys is None:
        try:
            print("WARNING: No keyboard was detected")
            print("Press enter to continue or ctrl+c to quit")
            input('')
        except KeyboardInterrupt:
            exit(0)

    return (drive_addresses, piano_keys)


def find_ports() -> tuple[BaseInput, BaseOutput]:
    print("Detecting MIDI interfaces...")
    input_port = None
    output_port = None

    for option in mido.get_input_names():
        if option.startswith("USB"):
            print(f'    Found input interface {option}')
            input_port = mido.open_input(option)
            break
    
    for option in mido.get_output_names():
        if option.startswith("USB"):
            print(f'    Found output interface {option}')
            output_port = mido.open_output(option)
            break
    
    if input_port is None:
        print("CRITICAL: No input port was found")
        input("Press enter to exit")
        exit(0)

    if output_port is None:
        print("CRITICAL: No output port was found")
        input("Press enter to exit")
        exit(0)    

    return (input_port, output_port)


if __name__ == '__main__':  

    # Do we have arguments?
    if len(sys.argv)>1 and sys.argv[1]!= '':
        #Remove white space and split
        args = sys.argv[1].strip().split('-')
        #remove and duplicates
        args = set(args)
        for arg in args:
            if not arg.isspace():
                if arg == "debug":        
                    bus.default_bus(bus.DebugBus())                
                    TabHeader._FRAME_RATE_DEBUG = True
                if arg =="altpage":
                    # Available bc of Jorian's windows PC
                    Tab.NEXT_TAB_KEY = Screen.KEY_F2
                    Tab.PRIOR_TAB_KEY = Screen.KEY_F1
    
    print(f'------------- FlopPiano (v{VERSION}) --------------')
    input_port, output_port = find_ports()
    drive_addrs, keyboard_addr =  find_devices()

    FlopPianoApp(
        DriveSynth(drive_addrs),
        #keyboard= None, # TODO Keyboard(keyboard_addr)
        input_port = input_port,
        output_port = output_port,
        theme='default',
        splash_start=False, 
        screen_timeout=30,
        asset_dir='./assets').run()