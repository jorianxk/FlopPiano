import jidi.bus as bus
from jidi.voices import Voice, DriveVoice
from jidi.devices import Keyboard
from jidi.synths import KeyboardSynth
import logging
from time import sleep


class KeyboardDebugBus(bus.SMBusWrapper):
    def __init__(self) -> None:
        super().__init__(1)
        self.key = 1
        self.bit_num = 7
        self.mod = 0
        self.pitch = 0

    def write(self, address: int, register: int, data: list) -> None:
        return super().write(address, register, data)
    
    def read(self, address: int, register: int, length: int) -> list[int]:

        read_bytes:list[int] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        byte_num = ((self.key-1) // 8)

        read_bytes[byte_num] = (1 << self.bit_num)
        
        read_bytes[5] = (self.pitch >> 8)
        read_bytes[6] = (self.pitch & 0b0000000011111111)
        
        read_bytes[7] = (self.mod >> 8)
        read_bytes[8] = (self.mod & 0b0000000011111111)

        for b in read_bytes:    
            print("{:08b}".format(b))

        self.bit_num -=1
        self.key +=1

        if self.key > 40:
            self.key = 1

        if self.bit_num <0:
            self.bit_num = 7

        self.pitch +=1
        self.mod +=1
        
        if self.pitch >1023:
            self.pitch =0

        if self.mod > 1023:
            self.mod = 0        

        return read_bytes

bus.default_bus(KeyboardDebugBus())


logging.basicConfig(level=logging.DEBUG)
l = logging.getLogger(__name__)


#voices = tuple(Voice() for i in range(8,18))
voices = [DriveVoice(i) for i in range(8,18)]

synth = KeyboardSynth(voices, Keyboard(), loopback=True)


while True:
    try:

        synth.update([])
        l.info("-------------------------------------------------------------")
        sleep(0.1)
        #p = input("----------------------------------------------------------")

    except KeyboardInterrupt:
        print("Exiting....")
        synth.reset()
        break

print("Done")


# # while True:
# #     try:
        
# #         print("--------------------------------")
# #         ctrl = 0b01010101
# #         response = bus.read(0x77, ctrl, 9)

# #         for b in response:    
# #             print("{:08b}".format(b))
        
# #         sleep(0.3)
        
# #     except bus.BusException:
# #         pass
# #     except KeyboardInterrupt:
# #         print("Exiting....")
# #         break

# # print("Done")




