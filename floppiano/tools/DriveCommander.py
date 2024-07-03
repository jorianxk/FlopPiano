"""
DriveCommander Utility - I2C communication with FlopPiano Drives

Version 1.1
 
2024-05-21
Jacob Brooks, Jorian Khan

This module is a utiliy to talk with FlopPiano floppy drive controllers via I2C
on a raspberry pi. Using /dev/ic2-1 
    Pins: 
        GPIO2 (Pin 3) as SDA 
        GPIO3 (Pin 5) as SDA

        Example:
    $ python DriveCommader.py


Requires: 
    smbus python module


                              Notes and Change-log
Version 1.1

-Added changes to support Version 1.1 of the Flop drive controller firmware
    -Matched default drive state to firmware drive state
     added support for the new crash modes
-Added a <state> function to print the current drive state
-<scale> function is now cleaner 
    -Now based on log scale
    -Plays as many of the 108 Piano keys as possible log scale
    -Prints MIDI number and musical notation when playing notes
    -see: https://en.wikipedia.org/wiki/Piano_key_frequencies
-Setting a frequency is no longer clamped by math.ceil. Insted round is used.
hopfully this will result in more accurate sounding

                                        - Jorian

Version 1.0

Some code is amateurish (like input validation could have been seperated), but
this utility is supposed to be a quick down-and-dirty way to test/control
drives. SO, I didn't spend to too much time making everything pythonic or super
clean. However, I did comment througout. 

                                        - Jorian    




                     **Notes on Raspberry pi envirionment**

- Pi's I2C bus MUST be enabled. you can enable it via raspi-config tool 
- The smbus python module must be installed
    -We can install it via apt "sudo apt install python3-smbus" BUT
     It's probably best to use a python virtual environmnet becuse we will need
     to install other python packages that are not in apt repos. (becaus the
     pi does no allow system wide module installs from pip)
     SEE:

     https://learn.adafruit.com/python-virtual-environment-usage-on-raspberry-pi/basic-venv-usage
    
    to learn how to setup a python virtual environment. Once it's setup 
    (and activated) use pip to install smbus. (we can also use this environmnet
    to install asciimatics, keyboard, and/or MIDI libraries that are not in apt 
    repos later) 

Useful I2C tools via linux command line:

- install i2c-tools for i2cdetect
	"sudo apt-get install i2c-tools"
    use: i2cdetect -y 1 
    to see all connected devices on the I2C bus    

"""


import sys
import cmd
import time
import math
from smbus2 import SMBus

class DriveState:
    """
        A sloppy class to hold the state of a drive
    """
    #clock speed of the attiny1604
    __clk_freq__ = 20000000 
    #prescaler setting on attin1604
    __prescaler__ = 4
    #TOP = alpha/f
    #alpha = C_f/(2*N)
    #the alpha constant for frequency calculation
    __alpha__ = __clk_freq__ / (2 * __prescaler__)

    def __init__(self, fromState = None) -> None:
        """
        Class constructor

        Optional Parameters 
            fromstate: Creates a new DriveState with all the properties of
                fromState DriveState object 
        """
        #If a state is passed then copy it, this is supper sloppy but was
        # a quick way to get started
        if(fromState is not None):
            self.top = fromState.top #Top value of the drive 
            self.enable = fromState.enable #Drive enable state
            self.spin = fromState.spin #Drive spin state
            self.crash_prevent = fromState.crash_prevent #Crash prevention mode
        else:
            #Use the drive's default firmware states to init object 
            self.top = 19111  #Drive firmware default state
            self.enable = 0
            self.spin = 0
            self.crash_prevent = 2 #Drive firmware default state
    
    def setFrequency(self, frequency:float) -> int:
        """
        A function to set the frequency of the drive by setting the drive TOP.

        A valid frequency results in TOP value that is a unsigned 16 bit integer 
        [0-65535]

        TOP = ROUND[alpha / frequency and alpha = C_f / (2 * N)]

        where, 
            C_f is the attiny's clock speed  = 20000000
            N is the attiny's prescaler  = 2
        
        therefore, alpha = 5000000

        parameters: 
            frequency:int the desired frequency of the drive
        returns:
            The the actual frequency set ie. alpha/TOP
        raises: 
            ValueError: If the frequency value given results in a TOP value 
                that is not a 16bit unsigned int
            ZeroDivisionError: if frequency is zero            
        """
        proposed_top = round(DriveState.__alpha__/frequency)

        if((proposed_top < 0) or (proposed_top > 65535)):
            raise ValueError (f'Frequency resulted in illegal TOP. '
                              f'Given frequency: {frequency}, '
                              f'Resultant TOP: {proposed_top}')
        
        self.top = proposed_top
        return int(DriveState.__alpha__/proposed_top)
    
    def __eq__(self, value: object) -> bool:
        """A sloppy function to test the equality of DriveState objects"""
        #This is super sloppy don't judge me
        equals = False
        if (self.top == value.top and
            self.enable == value.drive_enable and 
            self.spin == value.drive_spin and
            self.crash_prevent == value.crash_prevent):
            
            equals = True
        
        return equals
    
    def __str__(self) -> str:
        """Returns a string representation of the DriveState"""
        return (f'[ Enable:{self.enable} | '
                f'Spin:{self.spin} | '
                f'Crash Prevent:{self.crash_prevent} | '
                f'TOP:{self.top} ]')

class DriveCommander:
    """
        A super class for the Drive commander application
        Basically hold application settings and does sending via i2c
    """
    __version__ = 1.0

    def __init__(self)->None:
        #Set class settings
        self.i2cbus = SMBus(22) # indicates /dev/ic2-1
        self.slave_address = 0x8
        self.driveState = DriveState()
        self.send_on_execute = False
    

    def send(self, address:int=None, justCTRL:bool=True)->None:
        """
        A function to send all set CTRL Register values and TOP values a slave 
        drive, or to broadcast to the bus

        see code firmware and send(self, address:int=None, justCTRL:bool=True)
        Comments for details

        parameters: 
            address:int optional. if none the data is sent bus wide (broadcast)
                to all devices on the bus (address 0x0)
            justCTRL:bool optiona. if true, just the CTRL register is sent
                if false, CTRL plus the TOP value is sent to the address

        raises: 
            Idk some error: If the I2C bus cant sent the message for whatever
            reason          
        """

        # |------------------------------------------------------------------|
        # |                   The 'FIRST Byte' - CTRL byte                   |
        # |------------------------------------------------------------------|
        # |   0000   |     0      |       0      |      0     |      0       |
        # |----------|------------|--------------|---------------------------|
        # | Not used | Crash Mode |  Crash Mode  | Drive Spin | Drive Enable |
        # |------------------------------------------------------------------| 
        # 
        #  Crash mode - the two crash mode bits represent which crash mode the
        #  drive will use. Two bit combined give four possible states:
        #    MSB LSB
        #     0   0  - Crash prevention OFF
        #     0   1  - Crash prevention ON (BOW Mode)
        #     1   0  - Crash prevention ON (FLIP Mode)
        #     1   1  - Not used (results in crash prevention mode off if set)
        #     
        #     BOW mode: The drive will step until end of travel then flip
        #     direction (like a violin bow changing direction at the end of a
        #     bow stroke)
        #     
        #     FLIP mode: THe drive will flip direction after every step/pulse
        #  
        #  Drive Spin - if the bit is 1, the SPIN_PIN is pulled HIGH. 0 
        #  SPIN_PIN is pulled LOW. This is to turn on/off disc spin.
        #  
        #  Drive Enable - if the bit is high then the drive select/enable 
        #  (ENABLE_PIN) pin is pulled LOW (because the drives are active low) 
        #  and the drive is selected/enabled. If 0, then then the ENABLE_PIN
        #  is pulled HIGH and the drive is de-selected/disabled.

        #Prepare the CTRL Register 
        CTRL = (self.driveState.crash_prevent << 2)     
        CTRL = CTRL | (self.driveState.spin << 1)
        CTRL = CTRL | (self.driveState.enable)

        #print("{:08b}".format(CTRL), CTRL)

        #|----------------------------------------------------------------|
        #|            The second and third bytes - TOP Value              |
        #|----------------------------------------------------------------|
        #|  The second byte is the most significant byte of the TOP value |
        #|  The third byte is the least significant byte of the TOP value |
        #|----------------------------------------------------------------|

        TOP = self.driveState.top.to_bytes(2,'little')

        
        ########################################################################
        #                  Write the values to the address                     #
        ########################################################################

        #If the address arg is not set, just use the current set slave_addres 
        if(address is None): address = self.slave_address

        # #are we just senting the CTRL register?
        if(justCTRL):
            self.i2cbus.write_block_data(address, CTRL, [])
        else:
            self.i2cbus.write_block_data(address, CTRL, [TOP[1], TOP[0]])

class DriveCommanderCLI (DriveCommander, cmd.Cmd):
    """
    The (sloppy) Command line interface version of Drive Commander
    inherits from cmd.Cmd which handles the control simpe loop for cli 
    applications.

    see:https://docs.python.org/3/library/cmd.html#cmd-objects

    inherits DriveCommander for application states and i2c sending
    """
    #Intro for cli startup
    intro = ("Drive Commander: A utility for commanding FlopPiano floppy drives"
             "\nType <help> or <?> to list commands.\n")
    #prompt prefix for input
    prompt = ">> "
    #ruling for help menu
    ruler = '-'
    
    def __init__(self)->None:
       DriveCommander.__init__(self) #Set default applictions states
       cmd.Cmd.__init__(self) #Setup cmd.Cmd for application control structure

    ####################### Documented program commands ########################

    #Handle <exit> command
    def do_exit(self, arg):
        'Usage: <exit>\nQuits Drive Commander'
        return True #returning true ends the program
    
    #Handle <info> command
    def do_info(self, arg):
        'Usage: <info>\n displays information about frequency and this program'

        print("                           notes:                              ")
        print("When setting the frequency, we're actually setting the TOP the ")
        print("attiny1604 counts up to. TOP is calculated by:              \n ")
        print("                       TOP = C_f/(2*N*f)                    \n ")
        print(" where,                                                        ")
        print("  C_f is the attiny's clock speed"
              f"({DriveState.__clk_freq__} Hz)")
        print("  N is the attiny's prescalor setting"
              f"({DriveState.__prescaler__})")
        print("  f is the desired drive frequency                            ")
        print("However, f must be in the range [6-65535] AKA 16 bits This    ")
        print("program uses the above calculation to get a TOP value. TOP is ")
        print("calculated then CEIL()'d to be an integer. If TOP is not in   ")
        print("the above range then an error message is given.               ")

    #<state> Prints the current drive state and address
    def do_state(self, arg):
        'Usage: <stae>\nPrints the curent drive state and address'
        print(f"Address: {self.slave_address}\n"
              f"State: {self.driveState}")
    
    #<addr> Set the target I2C slave address
    def do_addr(self, arg):
        ('Usage: <addr> [0-255]\n'
         'Sets the I2C address of the drive being controlled.')
        
        #Make sure we have an argument - if not error and return
        if (len(arg)<1): 
            print("*** No I2C address specified! See help topic <addr>")
            return

        proposed_addr = 0 #A value to parse

        try:
            proposed_addr = int(arg) # Try to force the argument to be an int
        except:
            print("*** Argument must be an integer!") #Error if not an int
            return
        
        #Make sure the int is in the value address range - no? error
        if(proposed_addr<0 or proposed_addr>255):
            print("*** Invalid address. See help topic <addr>")
            return
        
        #Set the slave address 
        self.slave_address = proposed_addr
        print(f"Set slave address to {self.slave_address}")

    #<soe> Set send-on-execute mode
    def do_soe(self, arg):
        ('Usage: <soe> [0|1]\n'
         'Enables send-on-execute mode. Sends all updates to the drive\n'
         'immediately after executing a Drive Commander command.\n'
         '1 = ON, 0 = OFF.')
        
        #check for argument
        if (len(arg)<1): 
            print("*** Please specify a valid send-on-execute state. See help topic <soe>")
            return
        
        proposed_soe = 0
        
        #force int
        try:
            proposed_soe = int(arg)
        except:
            print("*** Argument must be an integer!")
            return
        
        #check vaild range
        if(not(proposed_soe==0 or proposed_soe==1)):
            print("*** Invalid send-on-execute state.  See help topic <soe>")
            return
        
        #set state
        self.send_on_execute = bool(proposed_soe)
        print(f"send-on-execute set to {self.send_on_execute}")

    #<enable> Handle drive select/enable
    def do_enable(self, arg):
        'Usage: <enable> [0|1]\nEnables the drive. 1 = Enabled, 0 = Disabled.'

        #chack for arg
        if (len(arg)<1): 
            print("*** Please specify a valid enable state. See help topic <enable>")
            return
        
        proposed_enable = 0
        
        #force int
        try:
            proposed_enable = int(arg)
        except:
            print("*** Argument must be an integer!")
            return
        
        #check valid range
        if(not(proposed_enable==0 or proposed_enable==1)):
            print("*** Invalid enable state.  See help topic <enable>")
            return
        
        #set state
        self.driveState.enable = proposed_enable
        print(f"enable set to {self.driveState.enable}")

    #<spin> set drive spin state
    def do_spin(self, arg):
        ('Usage: <spin> [0|1]\n'
         'Sets the drive spin to on or off 1 = Enabled, 0 = Disabled.')
        
        #check for arg
        if (len(arg)<1): 
            print("*** Please specify a valid spin state. See help topic <enable>")
            return
        
        proposed_spin = 0
        
        #force int
        try:
            proposed_spin = int(arg)
        except:
            print("*** Argument must be an integer!")
            return
        
        #check range
        if(not(proposed_spin==0 or proposed_spin==1)):
            print("*** Invalid spin state.  See help topic <spin>")
            return
        
        #set state
        self.driveState.spin = proposed_spin
        print(f"spin set to {self.driveState.spin}")

    #<crash> set crash prevention mode
    def do_crash(self, arg):
        ('Usage: <crash> [0|1|2]\n'
         'Enables drive crash prevention, 0 = Disabled., 1=BOW, 2 = flip')
        #check for arg
        if (len(arg)<1): 
            print("*** Please specify a valid crash state. See help topic <crash>")
            return
        
        proposed_crash = 0
        
        #force int
        try:
            proposed_crash = int(arg)
        except:
            print("** Argument must be an integer!")
            return
        
        #check range
        if(not(proposed_crash==0 or proposed_crash==1 or proposed_crash==2)):
            print("*** Invalid crash state.  See help topic <crash>")
            return
        
        #set state
        self.driveState.crash_prevent = proposed_crash
        print(f"Crash set to {self.driveState.crash_prevent}")
    
    #<freq> se the drive frequency
    def do_freq(self, arg):
        ('Usage: <freq> [~77 Hz- ~900000]\n'
         'Sets the drive frequency. See: <info>')
        
        #check for arg
        if (len(arg)<1): 
            print("*** Please specify a valid frequency. See help topic <freq>")
            return
        
        proposed_freq = 0
        
        #force float
        try:
            #set frequency
            proposed_freq = self.driveState.setFrequency(float(arg))
        except Exception as e:
            print("*** Error setting frequency: See <help> or <notes>\n",e)
            return
        
        print(f"Frequency set to {proposed_freq} (TOP:{self.driveState.top})")

    #<send> Handle the send command
    def do_send(self, arg):
        ('Usage: <send> ["all" | "broadcast"]\n'
         'Sends all of the set drive parameters. If no argument is give only\n' 
         'the CTRL byte is sent to the address. If [all] is used the CTRL and\n'
         'the TOP bytes are sent. If [broadcast] is specified then just the\n'
         'CTRL byte is sent to all drives on the bus')
        #all wrapped in try to catch and sending errors
        try:
            #check for arg
            if (len(arg)>1):
                arg = arg.split(" ")
                if (arg[0].upper() =="ALL"): #We want to sent CTRL and TOP
                    self.send(justCTRL=False)
                    print(f'Sent {self.driveState} to address',
                          self.slave_address)                    
                elif (arg[0].upper() == "BROADCAST"): # We want to broadcast CTRL
                    self.send(address=None, justCTRL=True)
                    print('Sent '
                          f'[ Enable:{self.driveState.enable} | '
                          f'Spin:{self.driveState.spin} | '
                          f'Crash Prevent:{self.driveState.crash_prevent} ] '
                          f'to all drives')                      
                else:
                    print("*** Invalid send argument.  See help topic <send>")
                    
            else: # no arg, just sent CTRL to current slave
                self.send(justCTRL=True)
                print('Sent '
                        f'[ Enable:{self.driveState.enable} | '
                        f'Spin:{self.driveState.spin} | '
                        f'Crash Prevent:{self.driveState.crash_prevent} ] '
                        f'to address {self.slave_address}')            
        except Exception as e:
            print("*** Error sending: ", e)

    #<scale> play a scale, crude version, sloppy 
    def do_scale(self,arg):
        'Usage: <scale>\nPlays a scale on a drive'

        n_lookup = {-8:"C0 Double Pedal C", -7:"C♯0/D♭0", -6:"D0", -5:"D♯0/E♭0",
                    -4:"E0", -3:"F0", -2:"F♯0/G♭0", -1:"G0", 0:"G♯0/A♭0",
                    1:"A0", 2:"A♯0/B♭0", 3:"B0", 4:"C1 Pedal C", 5:"C♯1/D♭1",
                    6:"D1", 7:"D♯1/E♭1", 8:"E1", 9:"F1", 10:"F♯1/G♭1", 11:"G1",
                    12:"G♯1/A♭1", 13:"A1", 14:"A♯1/B♭1", 15:"B1",
                    16:"C2 Deep C", 17:"C♯2/D♭2", 18:"D2", 19:"D♯2/E♭2",
                    20:"E2", 21:"F2", 22:"F♯2/G♭2", 23:"G2", 24:"G♯2/A♭2",
                    25:"A2", 26:"A♯2/B♭2", 27:"B2", 28:"C3", 29:"C♯3/D♭3",
                    30:"D3", 31:"D♯3/E♭3", 32:"E3", 33:"F3", 34:"F♯3/G♭3",
                    35:"G3", 36:"G♯3/A♭3", 37:"A3", 38:"A♯3/B♭3", 39:"B3",
                    40:"C4 Middle C", 41:"C♯4/D♭4", 42:"D4", 43:"D♯4/E♭4",
                    44:"E4", 45:"F4", 46:"F♯4/G♭4", 47:"G4", 48:"G♯4/A♭4",
                    49:"A4 A440", 50:"A♯4/B♭4", 51:"B4", 52:"C5 Tenor C",
                    53:"C♯5/D♭5", 54:"D5", 55:"D♯5/E♭5", 56:"E5", 57:"F5",
                    58:"F♯5/G♭5", 59:"G5", 60:"G♯5/A♭5", 61:"A5", 62:"A♯5/B♭5",
                    63:"B5", 64:"C6 Soprano C (High C)", 65:"C♯6/D♭6", 66:"D6",
                    67:"D♯6/E♭6", 68:"E6", 69:"F6", 70:"F♯6/G♭6", 71:"G6",
                    72:"G♯6/A♭6", 73:"A6", 74:"A♯6/B♭6", 75:"B6",
                    76:"C7 Double high C", 77:"C♯7/D♭7", 78:"D7", 79:"D♯7/E♭7",
                    80:"E7", 81:"F7", 82:"F♯7/G♭7", 83:"G7", 84:"G♯7/A♭7",
                    85:"A7", 86:"A♯7/B♭7", 87:"B7", 88:"C8 Eighth octave",
                    89:"C♯8/D♭8", 90:"D8", 91:"D♯8/E♭8", 92:"E8", 93:"F8",
                    94:"F♯8/G♭8", 95:"G8", 96:"G♯8/A♭8", 97:"A8", 98:"A♯8/B♭8",
                    99:"B8"}
    

        oldState = self.driveState
        self.driveState = DriveState(oldState)
        self.driveState.enable = 1
 
        sleepTime = 0.25

        #https://en.wikipedia.org/wiki/Piano_key_frequencies
        try:
            print("Playing log scale...")
            for n in range(7, 100):
                f = math.pow(2,((n-49)/12)) *440
                self.driveState.setFrequency(f)
                self.send(justCTRL=False)
                print(f"n:{n:03} | "
                      f"f:{f:0>8.3f} (Hz)| "
                      f"Midi#:{n+20:03} | "
                      f"Octive notation:{n_lookup[n]}")
                time.sleep(sleepTime)
            
            self.driveState = oldState
            self.send(justCTRL=False)
            print("Done.")
        except Exception as e:
            print("*** Error sending scale: ", e)
        pass


    #After a command is executed this function is called.
    def postcmd(self, stop: bool, line: str) -> bool:
        if(stop): return True #if the command was <exit> then stop will be true.
        #we should just eixt by returning True

        #if we are in send-on-execute 
        if(self.send_on_execute):
            #don't send anthing when setting the send-on-execute mode
            if(not (line.startswith("soe 1") or line.startswith("soe 0"))):
                #Executing any other command besides <soe> should trigger a send
                self.onecmd("send all")

#Handle main
if __name__ == '__main__':
    #If we have command line arguments
    if(len(sys.argv) > 1):
        #if the first argument is to enter GUI mode 
        # we could create a "GUI" for Drive commander in acciimatics later
        if(sys.argv[1].upper() == "GUI"):
            print("Drive Commander: acciimatics mode not implemented!")
        else:
            print("Drive Commander: Unknown argument!")
    else:
        # No command line arguments start the 'gui' or acii version
        DriveCommanderCLI().cmdloop()