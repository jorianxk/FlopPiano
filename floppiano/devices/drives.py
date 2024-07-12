import floppiano.bus as bus
import struct

#TODO: Doc strings

# Register #  = 0, 0, 0, 0, 0, 0, 0, 0 = register number

# Registers     
# 0 -> CTRL = 0, bow_mask, spin mask, enable_mask, 0, bow, spin, enable

# 1 -> Frequency =  {
#   (0, 0, 0, 0, 0, 0, 0, 0)
#   (0, 0, 0, 0, 0, 0, 0, 0)
#   (0, 0, 0, 0, 0, 0, 0, 0)
#   (0, 0, 0, 0, 0, 0, 0, 0)
# } i.e. 4 bytes representing a float

# 2 -> Modulation_rate = {
#   (0, 0, 0, 0, 0, 0, 0, 0) -> rate if rate ==0: modulation off
# 3 -> Modulation_frequency = {
#   (0, 0, 0, 0, 0, 0, 0, 0) -> freq?

# 4 -> Device type


#Constants

DEVICE_TYPE = 69

CTRL_REG        = 0
FREQ_REG        = 1
MOD_RATE_REG    = 2
MOD_FREQ_REG    = 3
DEVICE_TYPE_REG = 4

#Number of bits to shift
CTRL_EN   = 0 #0b00000001
CTRL_SPIN = 1 #0b00000010 
CTRL_BOW  = 2 #0b00000100

CTRL_EN_MASK   = 0b00010000
CTRL_SPIN_MASK = 0b00100000 
CTRL_BOW_MASK  = 0b01000000

class Drives():

    """
        A collection of functions to set values in a drive's registers
    """
    @staticmethod
    def find() -> list[int]:
        # ping all i2c devices from from 0x8 to 0x77 and get their device type, 
        # if the type is correct add it to the list
        drive_addresses  = []
        for address in range(0x8, 0x77+1):
            try:
                response = bus.read(address, DEVICE_TYPE_REG, 1)[0]

                if response == DEVICE_TYPE: drive_addresses.append(address)
            except bus.BusException:
                pass
            except IndexError:
                pass

        return drive_addresses
    
    @staticmethod
    def _check_address(address:int) -> None:
        address = int(address)
        if address != 0:
            if address<0x8 or address>0x77:
                raise ValueError(
                    f'Invalid drive address: {address}. '
                    f'address must be 0 or the range [{0x8},{0x77}]')

    @staticmethod
    def ctrl(
        address:int, 
        bow:bool = None, 
        spin:bool = None, 
        enable:bool = None) -> None:

        Drives._check_address(address)
        CTRL = 0

        if bow is not None:
            CTRL = CTRL | CTRL_BOW_MASK
            bow = bool(bow) << CTRL_BOW
            CTRL = CTRL | bow
        if spin is not None:
            CTRL = CTRL | CTRL_SPIN_MASK
            spin = bool(spin) << CTRL_SPIN
            CTRL = CTRL | spin
        if enable is not None:
            CTRL = CTRL | CTRL_EN_MASK
            enable = bool(enable) << CTRL_EN 
            CTRL = CTRL | enable

        #print("CTRL: ","{:08b}".format(CTRL), CTRL)

        if CTRL != 0: 
            bus.write(address, CTRL_REG, [CTRL])

    @staticmethod
    def enable(address:int, enable:bool) -> None:
        Drives.ctrl(address, enable=enable)
    
    @staticmethod
    def spin(address:int, spin:bool) -> None:
        Drives.ctrl(address, spin=spin)
    
    @staticmethod
    def bow(address:int, bow:bool) -> None:
        Drives.ctrl(address, bow=bow)

    @staticmethod
    def frequency(address:int, frequency:float) -> None:
        Drives._check_address(address)

        #round the frequency so it's only 3 decimal places       
        frequency = round(float(frequency),3)
 
        # convert frequency into a bytearray   
        frequency = struct.pack('f', frequency)
        #byte array to a list - always four bytes
        frequency = list(frequency)

        bus.write(address, FREQ_REG, frequency)

    @staticmethod
    def modulation_rate(address:int, rate:int) -> None:
        Drives._check_address(address)
        if not isinstance(rate, int):
            raise ValueError('modulation_rate must be an int')
        if rate<=0 or rate>255:
            raise ValueError('modulation_rate must be in the range [0,255]')
        bus.write(address, MOD_RATE_REG, [rate])
        
    
    @staticmethod
    def modulation_frequency(address:int, frequency:int) -> None:
        Drives._check_address(address)
        if not isinstance(frequency, int):
            raise ValueError('modulation_frequency must be an int')
        if frequency<0 or frequency>255:
            raise ValueError(
                'modulation_frequency must be in the range [0,255]')
        bus.write(address, MOD_FREQ_REG, [frequency])
