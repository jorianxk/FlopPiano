from jidi import bus
from enum import IntEnum
import struct
import time

class Drive ():

    """
    A class that represents a floppy drive
    """

    #init with default values of the firmware
    def __init__(
            self,
            address:int,
            enable:bool = False, 
            spin:bool = False,
            flip:bool = True,
            mod_frequency:int = 0,
            mod_rate:int = 0,
            frequency:float = 440.0) -> None:

 
        self.address = address
        
        self.enable = enable #Drive enable state
        self.spin = spin #Drive spin state
        self.flip = flip #Crash prevention mode
        self.mod_frequency = mod_frequency # number times per second to modulate
        self.mod_rate = mod_rate
        self.frequency = frequency #the frequency to be played

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
    def flip(self) -> bool:
        return self._crash_mode
    
    @flip.setter
    def flip(self, flip:bool) -> None:
        #true = Flip, False = BOW
        if not isinstance(flip,bool):
            raise ValueError('crash_mode must be a bool') 
        self._crash_mode = flip  

    @property
    def mod_rate(self) -> int:
        return self._mod_rate
    
    @mod_rate.setter
    def mod_rate(self, mod_rate:int):
        if not isinstance(mod_rate, int):
            raise ValueError('mod_rate must be an int')
        if mod_rate<0 or mod_rate>3:
            raise ValueError('mod_rate must be in the range [0,3]')
        self._mod_rate = mod_rate
    
    
    @property
    def mod_frequency(self) -> int:
        return self._mod_frequency
    
    @mod_frequency.setter
    def mod_frequency(self, frequency:int) -> None:
        if not isinstance(frequency, int):
            raise ValueError('frequency must be an int')
        if frequency<0 or frequency>7:
            raise ValueError('frequency must be in the range [0,15]')
        self._mod_frequency = frequency

    @property
    def frequency(self) -> float:
        return self._frequency
    
    @frequency.setter
    def frequency(self, frequency) -> None:
        self._frequency = round(float(frequency),3)

    def update(self, just_CTRL:bool=False) -> None:
        
        CTRL = (self.mod_rate << 6)
        CTRL = CTRL | (self.mod_frequency << 3)
        CTRL = CTRL | (self.flip << 2)     
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


        # if just_CTRL:
        #     bus.write(self.address, CTRL, [])
        # else:
        #     bus.write(self.address, CTRL, FREQ)


pp = Drive(8)

pp.enable = pp.spin = pp.flip = True

pp.mod_rate = 3
pp.mod_frequency = 0


pp.update()



exit(0)



pp = Drive(8)
try:
    pp.enable = True
    pp.mod_frequency = 0
    pp.frequency = 440.0
    pp.update(just_CTRL=False)
    print("no mod")
    time.sleep(2)

    # pp.frequency = 466.0
    # pp.update(just_CTRL=False)
    # print("no mod")
    # time.sleep(2)


    # pp.frequency = 493.0
    # pp.update(just_CTRL=False)
    # print("no mod")
    # time.sleep(2)


    # pp.frequency = 523.0
    # pp.update(just_CTRL=False)
    # print("no mod")
    # time.sleep(2)



    # pp.mod_frequency = 2
    # pp.update(False)
    # print("mod 2")
    # time.sleep(1)
    for i in range(1,16):
        print('mod', i)
        pp.mod_frequency = i
        pp.update(just_CTRL=True)
        time.sleep(5)

    pp.mod_frequency =0
    pp.update(just_CTRL=True)
    print("no mod")
    time.sleep(5)

except KeyboardInterrupt:
    pass
finally:
    pp.enable =False
    pp.mod_frequency = 0
    pp.frequency = 440.0
    pp.update(False)


