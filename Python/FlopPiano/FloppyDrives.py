from enum import Enum
from smbus import SMBus
from .MIDI import MidiMessageListener, MIDINoteHelper
from mido import Message
import copy

class CrashMode (Enum):
    """
    A Enum to hold Floppy drive crash modes

    *  Crash mode - the two crash mode bits represent which crash mode the
    *  drive will use. Two bit combined give four possible states:
    *    MSB LSB
    *     0   0  - Crash prevention OFF
    *     0   1  - Crash prevention ON (BOW Mode)
    *     1   0  - Crash prevention ON (FLIP Mode)
    *     1   1  - Not used (results in crash prevention mode off if set)
    *     
    *     BOW mode: The drive will step until end of travel then flip
    *     direction (like a violin bow changing direction at the end of a
    *     bow stroke)
    *     
    *     FLIP mode: THe drive will flip direction after every step/pulse
    """
    OFF = 0b00
    BOW = 0b01
    FLIP = 0b10

class FloppyDrive:
    """
    A class the represents a floppy drive
    """
    #clock speed of the attiny1604
    __clk_freq__ = 20000000 
    #prescaler setting on attin1604
    __prescaler__ = 4
    #TOP = alpha/f
    #alpha = C_f/(2*N)
    #the alpha constant for frequency calculation
    __alpha__ = __clk_freq__ / (2 * __prescaler__)
    
    #init with default values of the firmware
    def __init__(self, *, address:int = 8,
                 enable:bool = False, 
                 spin:bool = False,
                 top: int = 19111,
                 crash_mode:CrashMode = CrashMode.FLIP) -> None:
        """Constructor for a FloppyDrive

            Default arguments represent the defaults state of the drive's 
            firmware.

        Args:
            address (int, optional): The I2C address for the drive. Defaults to
                8.
            enable (bool, optional): The drive's  select/enable state. Defaults
                to False.
            spin (bool, optional): The drive select/enable state. Defaults to
                False.
            top (int, optional): The TOP value of the drive. Defaults to 19111.
            crash_mode (CrashMode, optional): The crash mode of the drive. 
                Defaults to CrashMode.FLIP.
        """
        
        self.address = address
        self.top = top #Top value of the drive 
        self.enable = enable #Drive enable state
        self.spin = spin #Drive spin state
        self.crash_mode = crash_mode #Crash prevention mode

    def setFrequency(self, frequency:float) -> int:
        """A function to set the frequency of the drive by setting the drive TOP

            A valid frequency results in TOP value that is a unsigned 16 bit 
            integer [0-65535].

            TOP = round(alpha / frequency)

            where,
                alpha = C_f / (2 * N) 
                C_f is the attiny's clock speed  = 20000000
                N is the attiny's prescaler  = 4

        Args:
            frequency (float): The desired frequency of the drive

        Raises:
            ValueError: If the frequency value given results in a TOP value 
                that is not a 16bit unsigned int
            ZeroDivisionError: if frequency is zero             

        Returns:
            int: The the resultant TOP value from the desired frequency
        """


        proposed_top = round(FloppyDrive.__alpha__/frequency)

        if((proposed_top < 0) or (proposed_top > 65535)):
            raise ValueError (f'Frequency resulted in illegal TOP. '
                              f'Given frequency: {frequency}, '
                              f'Resultant TOP: {proposed_top}')
        
        self.top = proposed_top
        return int(FloppyDrive.__alpha__/proposed_top)

    def __repr__(self) -> str:
        """Returns a string representation of the FloppyDrive

        Returns:
            str: _description_
        """
                
        return ('FloppyDrive: '
                f'[Address: {self.address} | '
                f'Enable: {self.enable} | '
                f'Spin: {self.spin} | '
                f'Crash Prevent: {self.crash_mode} | '
                f'TOP: {self.top}]')

class FloppyDriveHandler():
    
    def __init__(self, drives:list[FloppyDrive]) -> None:
        self.i2c_bus:SMBus =  SMBus(1) # indicates /dev/ic2-1
        self.drives = drives
    
    #TODO: update docstring
    def updateDrive(self, drive:FloppyDrive, justCTRL:bool=True)->None:
        """
        A function to send all set CTRL Register values and TOP values a slave 
        drive, or to broadcast to the bus

        see code firmware and send(self, address:int=None, justCTRL:bool=True)
        Comments for details

        parameters: 
            address:int optional. if none the data is sent bus wide (broadcast)
                to all devices on the bus (address 0x0)
            justCTRL:bool optional. if true, just the CTRL register is sent
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
        CTRL = (drive.crash_mode.value << 2)     
        CTRL = CTRL | (drive.spin << 1)
        CTRL = CTRL | (drive.enable)

        #print("{:08b}".format(CTRL), CTRL)

        #|----------------------------------------------------------------|
        #|            The second and third bytes - TOP Value              |
        #|----------------------------------------------------------------|
        #|  The second byte is the most significant byte of the TOP value |
        #|  The third byte is the least significant byte of the TOP value |
        #|----------------------------------------------------------------|

        TOP = drive.top.to_bytes(2,'little')

        
        ########################################################################
        #                  Write the values to the address                     #
        ########################################################################



        # #are we just senting the CTRL register?
        if(justCTRL):
            self.i2c_bus.write_block_data(drive.address, CTRL, [])
        else:
            self.i2c_bus.write_block_data(drive.address, CTRL, [TOP[1], TOP[0]])

    #TODO: update docstring
    def silenceDrives(self)->None:
        for drive in self.drives:
            drive.enable = False
            drive.spin = False
            self.updateDrive(drive, justCTRL=True)

class FloppyDrivePlayer(FloppyDriveHandler, MidiMessageListener):

    def __init__(self, drives: list[FloppyDrive]) -> None:
        super().__init__(drives)
        self.available_drives = copy.copy(drives)
        self.active_notes = dict() 

    def noteOnMsg(self, message:Message):
        #This is a note_on 
        if(not (message.note <27 or message.note>127)):
            #Cant play a note if all drives are busy
            if (len(self.available_drives)==0):
                print("Can't play", message.note, "no available drives")
                print("    ", len(self.available_drives))
            else:
                #get an available drive
                next_drive:FloppyDrive = self.available_drives.pop()
                #set up the drive to play the note 
                next_drive.setFrequency(MIDINoteHelper.note2Freq(message.note))
                next_drive.enable = True

                #tell the drive to play the note
                self.updateDrive(next_drive, justCTRL=False)
                print("Playing", message.note, "on address", next_drive.address)

                #add the note to the active notes
                self.active_notes[message.note] = next_drive
        else:
            print("Can't sound:", message)

    def noteOffMsg(self, message:Message):
        #handle note off
        #note_on velocity 0 is the same as note off
        #print('Found note off',msg.note ,MIDI_LOOK_UP[msg.note])
        #Get the drive that was playing the note

        try:
            sounding_drive:FloppyDrive = self.active_notes.pop(message.note)

            #stop the drive from playing
            sounding_drive.enable = False
            self.updateDrive(sounding_drive, justCTRL=True)
            print("Stopped", message.note, "on address", sounding_drive.address)

            #add the drive back to the available drives
            self.available_drives.append(sounding_drive)
        except KeyError as ke:
            print("Commanded to stop", message.note, "but it's not playing")
        
    
    def controlChangeMsg(self, message:Message):
        pass
    
    def pitchwheelMsg(self, message:Message):
        pass
