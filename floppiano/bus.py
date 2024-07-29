#Try to import smbus for The SMBusWrapper (default bus) class
try:
    from smbus2 import SMBus
except ModuleNotFoundError:
    # Ignore, let the default_bus() call handle setting things up
    pass

import logging

class BusException(Exception):
    pass

class Bus():
    """
        A base class for a Bus. 
    """
    
    def __init__(self) -> None:
        pass

    def read(self, address:int, register:int, length:int)->list[int]:
        #i2c_bus.read_i2c_block_data(address, register, length)
        raise Exception(
            'The default I2C implementation was not found. Please install '
            'smbus2 or set\nthe I2C manually by calling: '
            'floppiano.bus.default_bus()'
            )

    def write(self, address:int, register:int, data:list)->None:
        #i2c_bus.write_i2c_block_data(address, register, data)
        raise Exception(
            'The default I2C implementation was not found. Please install '
            'smbus2 or set\nthe I2C manually by calling: '
            'floppiano.bus.default_bus()'
            )

class DebugBus(Bus):
    """
        A class to write all I2C reads/writes to a logger. Does not 
        actually read/write to the bus.
    """
    
    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def read(self, address:int, register:int, length:int)->list[int]:
        self._logger.debug(f'read from address: {address} register: {register}'
                           f' length: {length}')
        return [0]*length

    def write(self, address:int, register:int, data:list)->None:
        self._logger.debug(f'write to address: {address} register: {register}'
                           f' data: {data}')


class SMBusWrapper(Bus):
    """_summary_
        A wrapper class for smbus. We only implement the things
        we care about. (reading and writing via I2C)
    """
    def __init__(self, bus_number:int) -> None:
        super().__init__()
        self._bus = SMBus(bus_number) 
    
    def read(self, address: int, register: int, length: int) -> list[int]:
        """
            Reads a specified number of bytes from a specific register at the 
            specified I2C address. 
        Args:
            address (int): The I2C address to be read from.
            register (int): The register to read from.
            length (int): The number of bytes to read.

        Raises:
            BusException: If the read could not be completed

        Returns:
            list[int]: The bytes read from the register
        """
        try:
            return self._bus.read_i2c_block_data(address, register, length)
        except OSError as oe:
            raise BusException("Error reading from the I2C SMbus") from oe
    
    def write(self, address: int, register: int, data:list[int]) -> None:
        """
            Writes the specified bytes to the specified register at the 
            specified I2C address.
        Args:
            address (int): The I2C address to be write to.
            register (int): The register to write to.
            data (list): The list of bytes to write.

        Raises:
            BusException: If the write could not be completed
        """
        try:
            self._bus.write_block_data(address, register, data) #<- this does though
            #self._bus.write_i2c_block_data(address, register, data) <- does not work right
        except OSError as oe:
            raise BusException("Error writing to the I2C SMbus") from oe

def default_bus(bus_object:Bus = None):
    """_summary_
        Sets the default Bus handler.
    Args:
        bus_object (Bus, optional): An instance of Bus that implements read
        and write functions. Defaults to None.
    """
    #similar to mido's __init__.py
    #https://github.com/mido/mido/blob/main/mido/__init__.py
    glob = globals()

    if isinstance(bus_object, Bus):
        bus = bus_object
    else:
        try:
            bus = SMBusWrapper(bus_number=22) # 1 indicates /dev/ic2-1 for RPi's
        except Exception as e:
            # Could not set up the bus, use the fallback
            bus = Bus()
    
    for attr_name in dir(bus):
        # Make the read()/ write() functions available in the 'bus' namespace
        if attr_name.split('_')[0] in ['read', 'write']:
            glob[attr_name] = getattr(bus,attr_name)


# On import of floppiano.bus ensure that the bus is set to the default bus
default_bus()
