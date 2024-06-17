import floppiano.bus as bus
from floppiano.voices import Voice
from floppiano.synths import Synth, KeyboardSynth
from floppiano.devices import Keyboard
import logging
from mido import Message

logging.basicConfig(level=logging.DEBUG)
l = logging.getLogger(__name__)

# class DebugBus(bus.Bus):
#     def __init__(self) -> None:
#         super().__init__()

#     def write(self, address: int, register: int, data: list) -> None:
#         pass
#         # global l
#         # l.debug(f'Bus: tried to write to adress: {address}')
    
#     def read(self, address: int, register: int, length: int) -> list[int]:
#         # global l
#         # l.debug(f'Bus: tried to read from address: {address}')
#         return []

# bus.default_bus(DebugBus())

def test_control_change(synth:Synth):
    cc_map = synth.control_change_map   
    for cc_num, cc_action in cc_map.items():       
        print(f'------------------------------------------Testing: {cc_action}')
        for i in range(-1, 129):
            msg = Message(
                'control_change', 
                channel = synth.input_channel,
                control= cc_num,
                value = i,
                skip_checks=True)
            synth.update([msg])

def test_sysex(synth:Synth):
    sysex_map = synth.sysex_map  
    for sysex_num, sysex_action in sysex_map.items():       
        print(f'------------------------------------------Testing: {sysex_action}')
        for i in range(-1, 129):
            msg = Message(
                'sysex',
                data=[synth.sysex_id,sysex_num,i],
                skip_checks=True)
            synth.update([msg])


voices = tuple(Voice() for i in range(8,18))

synth = KeyboardSynth(voices, Keyboard())

#print(len(PitchBendRange))
#test_control_change(synth)

test_sysex(synth)


