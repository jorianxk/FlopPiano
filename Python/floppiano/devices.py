from enum import IntEnum
from . import bus
from mido import Message



class Drive:
    class CrashMode (IntEnum):
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
        __order__ = 'OFF BOW FLIP'
        OFF = 0#0b00
        BOW = 1#0b01
        FLIP = 2#0b10

    """
    A class that represents a floppy drive
    """
    #clock speed of the attiny1604
    CLK_FREQ = 20000000 
    #prescaler setting on attiny1604
    PRESCALAR = 4
    #TOP = alpha/f
    #alpha = C_f/(2*N)
    #the alpha constant for frequency calculation
    ALPHA = CLK_FREQ / (2 * PRESCALAR)
    
    #minimum frequency that can be sounded
    MIN_FREQUENCY = 38.891

    #maximum frequency that can be sounded
    MAX_FREQUENCY = 12543.854

    #init with default values of the firmware
    def __init__(self,
                 address:int,
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
        self._top = top #Top value of the drive 
        self.enable = enable #Drive enable state
        self.spin = spin #Drive spin state
        self.crash_mode = crash_mode #Crash prevention mode

    #TODO: update docstring
    def update(self, just_CTRL:bool=False)->None:
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
            OSError: If the I2C bus cant sent the message for whatever
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
        CTRL = (self.crash_mode << 2)     
        CTRL = CTRL | (self.spin << 1)
        CTRL = CTRL | (self.enable)

        #print("{:08b}".format(CTRL), CTRL)

        #|----------------------------------------------------------------|
        #|            The second and third bytes - TOP Value              |
        #|----------------------------------------------------------------|
        #|  The second byte is the most significant byte of the TOP value |
        #|  The third byte is the least significant byte of the TOP value |
        #|----------------------------------------------------------------|

        TOP = self._top.to_bytes(2,'little')

        
        ########################################################################
        #                  Write the values to the address                     #
        ########################################################################



        # #are we just sending the CTRL register?
        if just_CTRL:
            bus.write(self.address, CTRL, [])
        else:
            bus.write(self.address, CTRL, [TOP[1], TOP[0]])

    @property
    def top(self)->int:
        return self._top
    
    @top.setter
    def top(self, frequency:float):# -> int:
        """_summary_
            A function to set the frequency of the drive by setting the drive 
            TOP

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
        #TODO: DO we really need the max/min freq check?
        #if the frequency cant be sounded, dont change anything
        if (frequency >= Drive.MIN_FREQUENCY and 
            frequency<= Drive.MAX_FREQUENCY):

            proposed_top = round(Drive.ALPHA/frequency)

            if((proposed_top < 0) or (proposed_top > 65535)):
                raise ValueError (f'Frequency resulted in illegal TOP. '
                                  f'Given frequency: {frequency}, '
                                  f'Resultant TOP: {proposed_top}')
            
            self._top = proposed_top
            #return int(Drive.ALPHA/proposed_top)
    
    def __repr__(self) -> str:
        """_summary_
            Returns a string representation of the Drive
        Returns:
            str: A string representation of the Drive
        """
                
        return ('Drive: '
                f'[Address: {self.address} | '
                f'Enable: {self.enable} | '
                f'Spin: {self.spin} | '
                f'Crash Prevent: {self.crash_mode} | '
                f'TOP: {self._top}]')


class Keyboard():

    def __init__(self, address = 0x77, start_key_note = 35, output_channel=0) -> None:        
        self.output_channel = output_channel
    
    @property
    def output_channel(self) -> int:
        return self._output_channel
    
    @output_channel.setter
    def output_channel(self, channel:int) -> None:
        if (channel <0 or channel>15):
            raise ValueError("Channel must be [0-15]") 
        self._output_channel = channel

    def read(self) -> list[Message]:
        return [
            Message(
                'note_on',
                note = 69,
                channel=self.output_channel)
        ]
    