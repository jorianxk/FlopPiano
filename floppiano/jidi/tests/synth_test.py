import jidi.bus as bus
from jidi.voices import Voice, DriveVoice
from jidi.synths import Synth, KeyboardSynth, DriveSynth
from jidi.devices import Keyboard
import logging
from mido import Message

class DebugBus(bus.Bus):
    def __init__(self) -> None:
        super().__init__()
        self.key = 1
        self.bit_num = 7
        self.mod = 0
        self.pitch = 0

    def write(self, address: int, register: int, data: list) -> None:
        pass #raise bus.BusException("DebugBus write")

    
    def read(self, address: int, register: int, length: int) -> list[int]:

        read_bytes:list[int] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        # byte_num = ((self.key-1) // 8)

        # read_bytes[byte_num] = (1 << self.bit_num)
        
        # read_bytes[5] = (self.pitch >> 8)
        # read_bytes[6] = (self.pitch & 0b0000000011111111)
        
        # read_bytes[7] = (self.mod >> 8)
        # read_bytes[8] = (self.mod & 0b0000000011111111)

        # # for b in read_bytes:    
        # #     print("{:08b}".format(b))

        # self.bit_num -=1
        # self.key +=1

        # if self.key > 40:
        #     self.key = 1

        # if self.bit_num <0:
        #     self.bit_num = 7

        # self.pitch +=1
        # self.mod +=1
        
        # if self.pitch >1023:
        #     self.pitch =0

        # if self.mod > 1023:
        #     self.mod = 0        

        return read_bytes

def test_control_change(synth:Synth):
    cc_map = synth.control_change_map   
    for cc_code in cc_map.codes():       
        print(
            f'------------------------------------------------------------------'
            f' Control Change: {cc_map.name(cc_code)}')
        
        for i in range(-1, 129):
            msg = Message(
                'control_change', 
                channel = synth.input_channel,
                control= cc_code,
                value = i,
                skip_checks=True)
            synth.update([msg])


def test_sysex(synth:Synth):
    sysex_map = synth.sysex_map  
    for sysex_code in sysex_map.codes():       
        print(
            f'------------------------------------------------------------------'
            f' Sysex: {sysex_map.name(sysex_code)}')
        
        for i in range(-1, 129):
            msg = Message(
                'sysex',
                data=[synth.sysex_id,sysex_code,i],
                skip_checks=True)
            synth.update([msg])
        
        if sysex_code ==3:
            synth.loopback = False
            synth.update([])

bus.default_bus(DebugBus())
logging.basicConfig(level=logging.INFO)



voices = tuple(Voice() for i in range(8,18))
#voices = tuple(DriveVoice(i) for i in range(8,18))


synth = Synth(voices)
#synth = KeyboardSynth(voices, Keyboard(), loopback=False)
#synth = DriveSynth(voices)

# synth.update([
#     Message(
#         'note_on',
#         note = 69
#     )
# ])

test_control_change(synth)
#test_sysex(synth)


