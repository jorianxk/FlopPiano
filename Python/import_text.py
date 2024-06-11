import FlopPiano.bus as bus
from time import sleep

bus.default_bus(bus.Bus())

while True:
    print(bus.read(0x77,0,7))



# bus.write()
# b.read("","","")








#FlopPiano.read(None,None, None)