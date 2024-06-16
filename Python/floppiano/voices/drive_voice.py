import math
import time

from .voice import PitchBendRange, ModulationWave, Voice
from ..devices.drive import Drive
from ..midi import MIDIUtil

class DriveVoice(Drive, Voice):

    def __init__(self, address: int, **kwargs) -> None:
        super().__init__(address,**kwargs)
  
    @Voice.note.setter
    def note(self, note:int) -> None:
        self._note = note
        self.frequency = MIDIUtil.MIDI2Freq(note)

    @property
    def frequency(self) -> float:
        return self._frequency
    
    @frequency.setter
    def frequency(self, frequency:float) -> None:
        self._frequency = frequency
        self.top = frequency

    def pitch_bend(self, amount: int, pitch_bend_range:PitchBendRange) -> None:
        #call super().pitch_bend to validate amount
        super().pitch_bend(amount, pitch_bend_range)
        if amount == 0:
            self.frequency = MIDIUtil.MIDI2Freq(self.note)
            return
        else:
            old_n = MIDIUtil.freq2n(MIDIUtil.MIDI2Freq(self.note))
            n_mod = MIDIUtil.integer_map_range(
                amount,
                Voice._MIN_PITCH_BEND,
                Voice._MAX_PITCH_BEND,
                -pitch_bend_range.value, 
                pitch_bend_range.value)
            
            self.frequency = MIDIUtil.n2freq(old_n+n_mod) 

    def modulate(self, amount: int, modulation_wave:ModulationWave) -> None:
        #call super().modulate to validate amount 
        super().modulate(amount, modulation_wave)    
        if amount ==0:
            return
        else:
            #TODO Handle wave forms here
            #Play with 2, and 16 below for differing effects
            omega = MIDIUtil.integer_map_range(
                amount,
                Voice._MIN_MODULATION,
                Voice._MAX_MODULATION,
                2,
                16) * math.pi
            
            self.top = (self.frequency+math.sin(omega * time.time()))

    def update(self, make_noise:bool) -> None:
        self.enable = make_noise
        Drive.update(self, just_CTRL=False)
