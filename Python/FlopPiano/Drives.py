
import time
from enum import Enum
from smbus import SMBus
from .MIDI import *


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

class Drive:
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
    
    #minimum frequency that can be sounded
    __min_frequency__ = 38.891

    #maximum frequency that can be sounded
    __max_frequency__ = 12543.854

    #init with default values of the firmware
    def __init__(self, *,
                 i2c_bus:SMBus, 
                 address:int = 8,
                 enable:bool = False, 
                 spin:bool = False,
                 top: int = 19111,
                 crash_mode:CrashMode = CrashMode.FLIP) -> None:
        """Constructor for a FloppyDrive

            Default arguments represent the defaults state of the drive's 
            firmware.

        Args:
            i2c_bus (SMBus): the I2C buss object to use 
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
        self.i2c_bus = i2c_bus
        self.address = address
        self.top = top #Top value of the drive 
        self.enable = enable #Drive enable state
        self.spin = spin #Drive spin state
        self.crash_mode = crash_mode #Crash prevention mode

    #TODO: update docstring
    def update(self, justCTRL:bool=False)->None:
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
        CTRL = (self.crash_mode.value << 2)     
        CTRL = CTRL | (self.spin << 1)
        CTRL = CTRL | (self.enable)

        #print("{:08b}".format(CTRL), CTRL)

        #|----------------------------------------------------------------|
        #|            The second and third bytes - TOP Value              |
        #|----------------------------------------------------------------|
        #|  The second byte is the most significant byte of the TOP value |
        #|  The third byte is the least significant byte of the TOP value |
        #|----------------------------------------------------------------|

        TOP = self.top.to_bytes(2,'little')

        
        ########################################################################
        #                  Write the values to the address                     #
        ########################################################################



        # #are we just sending the CTRL register?
        if(justCTRL):
            self.i2c_bus.write_block_data(self.address, CTRL, [])
        else:
            self.i2c_bus.write_block_data(self.address, CTRL, [TOP[1], TOP[0]])

    #TODO: update docstring
    def silence(self)->None:
        self.enable = False
        self.update()

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
        #if the frequency cant be sounded, dont change anything
        if (frequency >= Drive.__min_frequency__ and 
            frequency<= Drive.__max_frequency__):

            proposed_top = round(Drive.__alpha__/frequency)

            if((proposed_top < 0) or (proposed_top > 65535)):
                raise ValueError (f'Frequency resulted in illegal TOP. '
                                  f'Given frequency: {frequency}, '
                                  f'Resultant TOP: {proposed_top}')
            
            self.top = proposed_top
            return int(Drive.__alpha__/proposed_top)
    
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

class PitchBendMode(Enum):
    #Number indicates steps. 1/2 steps = 1 note
    HALF     = 0.5 #  1 note(s) or   1/2 step(s)
    WHOLE    =   1 #  2 note(s) or     1 step(s)
    MINOR3RD = 1.5 #  3 note(s) or 1 1/2 step(s)
    MAJOR3RD =   2 #  4 note(s) or     2 step(s)
    FOURTH   = 2.5 #  5 note(s) or 2 1/2 step(s)
    FIFTH    = 3.5 #  7 note(s) or 3 1/2 step(s)
    OCTAVE   =   6 # 12 note(s) or     6 step(s)

class Note(Drive):

    def __init__(self, i2c_bus:SMBus, address:int) -> None:
        super().__init__(i2c_bus=i2c_bus, address=address)
        
 
    def setOriginal(self, original:float)->None:
        self._original = original
        self.setCenter(original)

    def setCenter(self, center:float):
        self._center = center
        self.setFrequency(center)

    def bend(self, bendAmount:int, mode:PitchBendMode):
        if bendAmount == 0:
            self.setCenter(self._original)
            return
        else:
            old_n = MIDIUtil.freq2n(self._original)
            n_mod = map_range(bendAmount,-8192,8192,-mode.value, mode.value)
            self.setCenter(MIDIUtil.n2freq(old_n+n_mod))
            
    def modulate(self, modAmount:int):
        if modAmount ==0:
            return
        else:
            #Play with 2, and 16 below for differing effects
            omega = map_range(modAmount,1,127,2,16) * math.pi
            self.setFrequency(self._center+math.sin(omega * time.time()))

    def play(self):
        self.enable = True
        self.update()
