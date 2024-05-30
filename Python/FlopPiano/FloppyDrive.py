from enum import Enum

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