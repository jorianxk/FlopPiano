import floppiano.bus as bus
import struct

"""
                          Floppy Drive Registers:     

A floppy drive (or drive) is controlled via the I2C bus by setting various
register values to manipulate sound behavior. Below is a description of each
register, its bytes, and the effect each register has on drive sound. 

An important note: It is possible to manipulate all drives' registers at the
same time by writing/reading from I2C address 0.

-------------- Register 0 (Zero) - The Control (CTRL) Register ----------------- 

                                 WRITE ONLY
Consists of a single byte:

  MSB 7  |    6     |     5     |      4      |    3     |  2  |   1  | LSB 0
---------|----------|-----------|-------------|----------|-----|------|---------
not used | bow_mask | spin_mask | enable_mask | not used | bow | spin | enable


Bit 6-4: Masks

Bits 6-4 are masks that tell the drive to accept the corresponding control bit. 
That is, in order for a drive to read a control bit, the control bit's mask must
be set. For example, when setting the enable control bit (the LSB bit, bit 0), 
the enable_mask (bit 4) must be set to 1 or True. 

Ex. Setting only the enable bit ON consists of sending the following byte to 
the CTRL Register: 00010001. Similarly, setting the enable bit OFF: 00010000

Control bit masking allows the setting of specific control bits on all drives
simultaneously (via address 0) without influencing or setting other control bits
For example, disabling all drives, but not changing their individual spin states

Bit 2: bow

The bow control bit controls the crash avoidance behavior of the drives. When
True the bow bit instructs the drive to flip the direction of it's head at the
end of travel. When false the drive's head oscillates in place (Also known as 
flip)

Bit 1: spin

The spin control bit instructs the drive to spin its disc platter. When True
the platter will spin (if a disc is inserted in the drive)

Bit 0: enable

This enable control bit tells the drive to actually produce sound. When False
the drive's head will not vibrate.

------------------------- Register 1 - Frequency -------------------------------

                              WRITE ONLY

The Frequency register is a four byte register that represents a floating point
(float) corresponding the frequency in Hz that the drive should sound
                        (0, 0, 0, 0, 0, 0, 0, 0)
                        (0, 0, 0, 0, 0, 0, 0, 0)
                        (0, 0, 0, 0, 0, 0, 0, 0)
                        (0, 0, 0, 0, 0, 0, 0, 0)
                        4 bytes representing a float
See the frequency(address:int, frequency:float) function below for details

-------------------- Register 2 - Modulation Rate/Attack -----------------------

                              WRITE ONLY

The Modulation Rate Register is a single byte that represents an integer value
in Hz [0, 255]

                         (0, 0, 0, 0, 0, 0, 0, 0)
                       if rate ==0: modulation off

Modulation is a regular change in a drive's frequency. Drives modulate using a 
triangular wave with frequency set by the Modulation Frequency Register 
(Register 3). The amount of change (rate A.K.A) is set by Modulation Rate 
Register.

-------------------- Register 3 - Modulation Frequency -------------------------                       

                            WRITE ONLY                       

The Modulation Frequency Register is a single byte that represents an integer
value in Hz [0,255]
                            
                       (0, 0, 0, 0, 0, 0, 0, 0)

Modulation is a regular change in a drive's frequency. Drives modulate using a 
triangular wave with frequency set by the Modulation Frequency Register 
(Register 3). The amount of change (rate A.K.A) is set by Modulation Rate 
Register.

--------------------- Register 4 - Device Type ---------------------------------

                            READ ONLY

The Device type register is an 8 bit register, in which a device type integer is
stored. Reading this register on a drive should always result in a value of
69.

"""



#Constants
DEVICE_TYPE = 69

CTRL_REG        = 0
FREQ_REG        = 1
MOD_RATE_REG    = 2
MOD_FREQ_REG    = 3

#Number of bits to shift
CTRL_EN   = 0 #0b00000001
CTRL_SPIN = 1 #0b00000010 
CTRL_BOW  = 2 #0b00000100

CTRL_EN_MASK   = 0b00010000
CTRL_SPIN_MASK = 0b00100000 
CTRL_BOW_MASK  = 0b01000000

class Drives():
    """
        A collection of functions to set/get values in a drive's registers
    """
    
    @staticmethod
    def _check_address(address:int) -> None:
        """
            Checks the given I2C address
        Args:
            address (int): The I2C address to check

        Raises:
            ValueError: If the drive address is not valid/in the range:
            [0x8, 0x77] or 0
        """
        address = int(address)
        # Address 0 is valid because using address zero will update ALL Drives
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
        """
            Sets/sends all bits in the CTRL register of the Drive. If a bit/
            argument is set to 'None' the corresponding mask bit will NOT be
            set.
        Args:
            address (int): The drive's I2C address
            bow (bool, optional): The 'bow' bit True = Bow on. Defaults to None.
            spin (bool, optional): The 'spin' bit True = Spin on. 
                Defaults to None.
            enable (bool, optional):The 'enable' bit True = on.
                Defaults to None.
        """
        # Ensure the address is valid
        Drives._check_address(address)

        # Empty CTRL Register
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

        if CTRL != 0: 
            # Write the states only when there is something to update
            bus.write(address, CTRL_REG, [CTRL])

    @staticmethod
    def enable(address:int, enable:bool) -> None:
        """
            Convenience method for setting/sending the enable bit in a drive's
            CTRL register. When the enable state is true, the drive will sound/
            voice its current frequency.
        Args:
            address (int): The drive's I2C address
            enable (bool): The desired enable state.
        """
        # Set only the enable bit in the control register
        Drives.ctrl(address, enable=enable)
    
    @staticmethod
    def spin(address:int, spin:bool) -> None:
        """
            Convenience method for setting/sending the spin bit in a drive's
            CTRL register. When a drives spin state is true the drive's platter
            will spin. (If a disc is inserted into the drive)
        Args:
            address (int): The drive's I2C address
            enable (bool): The desired spin state.
        """
        # Set only the spin bit in the control register
        Drives.ctrl(address, spin=spin)
    
    @staticmethod
    def bow(address:int, bow:bool) -> None:
        """
            Convenience method for setting/sending the bow bit in a drive's
            CTRL register. When a drive's bow state is true the drive will move
            the head to the end of travel then reverse direction when sounding 
            a frequency. If the bow state is false, the drive will flip its head
            direction rapidly to produce sound.
        Args:
            address (int): The drive's I2C address
            enable (bool): The desired bow state.
        """
        # Set only the bow bit in the control register
        Drives.ctrl(address, bow=bow)

    @staticmethod
    def frequency(address:int, frequency:float) -> None:
        """
            Sets/sends the desired frequency (in Hz) of a drive. 
            Notes:
                - If the desired frequency cannot be played by a drive it will
                  be ignored. (See drive firmware)
                - If the drive is not enabled the no sound will be produced but
                  the frequency will be set.
        Args:
            address (int): The drive's I2C address
            frequency (float): The desired frequency
        """
        
        Drives._check_address(address)

        #round the frequency so it's only 3 decimal places       
        frequency = round(float(frequency),3)
 
        # convert frequency into a bytearray   
        frequency = struct.pack('f', frequency)
        # byte array to a list - always four bytes
        frequency = list(frequency)
        # write
        bus.write(address, FREQ_REG, frequency)

    @staticmethod
    def modulation_rate(address:int, rate:int) -> None:
        """
            Sets/sends the desired modulation rate or attack of a drive. 
            The modulation rate/attack is an amount (in Hz) that will be added
            then subsequently removed of the a drives frequency when modulating.
            If the attack is set to zero effectively no modulation will occur.
            Notes:
                - Modulation is a regular change in a drive's frequency. Drives
                  modulate using a triangular wave with frequency set by 
                  modulation_frequency(). The amount of change (rate A.K.A 
                  attack) is set by modulation_rate()
        Args:
            address (int): The drive's I2C address
            rate (int): The amount in Hz to be added to the drives frequency 
            when modulating.

        Raises:
            ValueError: If the rate is not an integer or not in the range 
                [0,255]
        """
        Drives._check_address(address)
        if not isinstance(rate, int):
            raise ValueError('modulation_rate must be an int')
        if rate<0 or rate>255:
            raise ValueError('modulation_rate must be in the range [1,255]')
        bus.write(address, MOD_RATE_REG, [rate])
        
    
    @staticmethod
    def modulation_frequency(address:int, frequency:int) -> None:
        """
            Sets/sends the desired modulation frequency (in Hz) of a drive. 
            Notes:
                - Modulation is a regular change in a drive's frequency. Drives
                  modulate using a triangular wave with frequency set by 
                  modulation_frequency(). The amount of change (rate A.K.A 
                  attack) is set by modulation_rate()
        Args:
            address (int): The drive's I2C address
            frequency (int): The desired frequency (in Hz) of modulation

        Raises:
            ValueError: If the frequency is not an integer or not in the range 
                [0,255]
        """
        Drives._check_address(address)
        if not isinstance(frequency, int):
            raise ValueError('modulation_frequency must be an int')
        if frequency<0 or frequency>255:
            raise ValueError(
                'modulation_frequency must be in the range [0,255]')
        bus.write(address, MOD_FREQ_REG, [frequency])
