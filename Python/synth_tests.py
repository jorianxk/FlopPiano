import jidi.bus as bus
from jidi.voices import Voice, DriveVoice
from jidi.synths import Synth, KeyboardSynth
from jidi.devices import Keyboard
import logging
from mido import Message

class DebugBus(bus.Bus):
    def __init__(self) -> None:
        super().__init__()
    def write(self, address: int, register: int, data: list) -> None:
        raise bus.BusException("poop")
    def read(self, address: int, register: int, length: int) -> list[int]:
        pass
bus.default_bus(DebugBus())


logging.basicConfig(level=logging.INFO)
l = logging.getLogger(__name__)




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


voices = tuple(DriveVoice(8) for i in range(8,18))

# synth = Synth(voices)
synth = KeyboardSynth(voices, Keyboard())

synth.update([
    Message(
        'note_on',
        note = 69
    )
])
#print(len(PitchBendRange))
#test_control_change(synth)

test_sysex(synth)


