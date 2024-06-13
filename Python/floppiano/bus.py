#Try to import smbus for The SMBusWrapper (default bus) class
try:
    from smbus import SMBus
except ModuleNotFoundError:
    pass

class BusException(Exception):
    pass

#abstract bus class
class Bus():
    
    def __init__(self) -> None:
        pass

    def read(self, address:int, register:int, length:int)->list[int]:
        #i2c_bus.read_i2c_block_data(address, register, length)
        raise Exception(
                'The default I2C implementation was not found. Please install '
                'smbus or set\nthe I2C manually by calling: '
                'floppiano.bus.default_bus()'
                )



    def write(self, address:int, register:int, data:list)->None:
        #i2c_bus.write_i2c_block_data(address, register, data)
        raise Exception(
        'The default I2C implementation was not found. Please install '
        'smbus or set\nthe I2C manually by calling: '
        'floppiano.bus.default_bus()'
        )




#TODO: Docstrings
class SMBusWrapper(Bus):
    """_summary_
        A wrapper class for smbus. We only implement the things
        we care about. (reading and writing via I2C)
    """
    def __init__(self, bus_number:int) -> None:
        super().__init__()
        self._bus = SMBus(bus_number) 
    
    def read(self, address: int, register: int, length: int) -> list[int]:
        try:
            return self._bus.read_i2c_block_data(address, register, length)
        except OSError as oe:
            raise BusException("Error reading from the I2C SMbus") from oe
    
    def write(self, address: int, register: int, data: list) -> None:
        try:
            self._bus.write_block_data(address, register, data) #<- this does though
            #self._bus.write_i2c_block_data(address, register, data) <- does not work right
        except OSError as oe:
            raise BusException("Error writing to the I2C SMbus") from oe





def default_bus(bus_object:Bus = None):
    #similar to mido's __init__.py
    #https://github.com/mido/mido/blob/main/mido/__init__.py
    glob = globals()

    if isinstance(bus_object, Bus):
        bus = bus_object
    else:
        try:
            bus = SMBusWrapper(bus_number=1) # 1 indicates /dev/ic2-1 for RPi's
        except NameError as ne:
            bus = Bus()
    
    for attr_name in dir(bus):
        #"write_i2c_block_data"
        #"read_i2c_block_data",
        if attr_name.split('_')[0] in ['read', 'write']:
            glob[attr_name] = getattr(bus,attr_name)


default_bus()
