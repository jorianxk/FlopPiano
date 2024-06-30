from jidi import bus
from enum import IntEnum
import struct

class Drive ():
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

    #init with default values of the firmware
    def __init__(
            self,
            address:int,
            enable:bool = False, 
            spin:bool = False,
            crash_mode:CrashMode = CrashMode.FLIP,
            mod_frequency:int = 0,
            frequency:float = 440.0,) -> None:

 
        self.address = address
        
        self.enable = enable #Drive enable state
        self.spin = spin #Drive spin state
        self.crash_mode = crash_mode #Crash prevention mode
        self.mod_frequency = mod_frequency # number times per second to modulate
        self.frequency = frequency

    @property
    def address(self) -> int:
        return self._address
    
    @address.setter
    def address(self, address:int) -> None:
        if not isinstance(address, int):
            raise ValueError('address must be int')
        if address<0x8 or address>0x77:
            raise ValueError(f'address must be in the range [{0x8},{0x77}]')
        self._address = address        

    @property
    def enable(self) -> bool:
        return self._enable
    
    @enable.setter
    def enable(self, enabled:bool) -> None:
        if not isinstance(enabled,bool):
            raise ValueError('enable must be a bool') 
        self._enable = enabled      

    @property
    def spin(self) -> bool:
        return self._spin
    
    @spin.setter
    def spin(self, spin:bool) -> None:
        if not isinstance(spin,bool):
            raise ValueError('spin must be a bool') 
        self._spin = spin        
    
    @property
    def crash_mode(self) -> CrashMode:
        return self._crash_mode
    
    @crash_mode.setter
    def crash_mode(self, crash_mode:int) -> None:
        if crash_mode not in Drive.CrashMode.__members__.values():
            raise ValueError('not a valid CrashMode')
        self._crash_mode = crash_mode  

    @property
    def mod_frequency(self) -> int:
        return self._mod_frequency
    
    @mod_frequency.setter
    def mod_frequency(self, frequency:int) -> None:
        if not isinstance(frequency, int):
            raise ValueError('frequency must be an int')
        if frequency<0 or frequency>15:
            raise ValueError('frequency must be in the range [0,15]')
        self._mod_frequency = frequency

    @property
    def frequency(self) -> float:
        return self._frequency
    
    @frequency.setter
    def frequency(self, frequency:float) -> None:
        if not isinstance(frequency, float):
            raise ValueError('frequency must be float')
        self._frequency = round(frequency,3)

    def update(self, just_CTRL:bool=False) -> None:

        CTRL = (self.mod_frequency << 4)
        CTRL = CTRL |(self.crash_mode << 2)     
        CTRL = CTRL | (self.spin << 1)
        CTRL = CTRL | (self.enable)

        print("CTRL: ","{:08b}".format(CTRL), CTRL)

        # convert freq into a bytearray, also round the frequency so it's only 3 
        # decimal places
   
        FREQ = struct.pack('f',self.frequency)
        #byte array to a list - always four bytes
        FREQ = list(FREQ)
        print(f'FREQ: {self.frequency:0.3f}, bytes: ', end='')
        for b in FREQ:
            print(f'{b}, ', end='')
        print(f"array length: {len(FREQ)}")       


        if just_CTRL:
            bus.write(self.address, CTRL, [])
        else:
            bus.write(self.address, CTRL, FREQ)



pp = Drive(8)



pp.update()


