from enum import Enum, IntEnum
from mido import Message

from .devices import Drive

from .midi import MIDIUtil
import math
import time

def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

class PitchBendRange(Enum):
    __order__ = 'HALF WHOLE MINOR3RD MAJOR3RD FOURTH FIFTH OCTAVE'
    #Number indicates steps. 1/2 steps = 1 note
    HALF     = 0.5 #  1 note(s) or   1/2 step(s)
    WHOLE    =   1 #  2 note(s) or     1 step(s)
    MINOR3RD = 1.5 #  3 note(s) or 1 1/2 step(s)
    MAJOR3RD =   2 #  4 note(s) or     2 step(s)
    FOURTH   = 2.5 #  5 note(s) or 2 1/2 step(s)
    FIFTH    = 3.5 #  7 note(s) or 3 1/2 step(s)
    OCTAVE   =   6 # 12 note(s) or     6 step(s)

class ModulationWave(IntEnum):
    __order__ = 'SINE SQUARE SAW'
    SINE = 0
    SQUARE = 1
    SAW = 2


class Instrument():
    """
    An instrument is:
    -Monophonic (sounds one note at a time)
    -Plays MIDI a midi note
    -Its note can be pitch bent (via midi message pitchwheel, and takes a valid midi pitch)
    -Its note can be modulated (via midi modulate control change message, and takes a valid midi control value )
    """
    _MIN_PITCH_BEND = -8192
    _MAX_PITCH_BEND = 8191
    _MIN_MODULATION = 0
    _MAX_MODULATION = 127
    _MIN_NOTE = 0
    _MAX_NOTE = 127

    def __init__(self) -> None:
        pass
    
    @property    
    def note(self) -> int:
        return self._note
    
    @note.setter
    def note(self, note:int) -> None:
        if (note <Instrument._MIN_NOTE or note >Instrument._MAX_NOTE):
            raise ValueError(f'{note} is not a valid MIDI note')
        self._note = note

    def pitch_bend(self, amount:int, pitch_bend_range:PitchBendRange) -> None:
        if amount<Instrument._MIN_PITCH_BEND or Instrument._MAX_PITCH_BEND:
            raise ValueError(f'{amount} is not a valid MIDI pitch')

    def modulate(self, amount:int, modulation_wave:ModulationWave) -> None:
        if amount<Instrument._MIN_MODULATION or Instrument._MAX_MODULATION:
            raise ValueError(f'{amount} is not a valid MIDI modulation value')

    def play(self) -> None:
        pass

class DriveInstrument(Drive, Instrument):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
  
    @Instrument.note.setter
    def note(self, note:int) -> None:
        print("note setter called")
        self._note = note
        self.frequency = MIDIUtil.MIDI2Freq(note)

    @property
    def frequency(self) -> float:
        return self._frequency
    
    @frequency.setter
    def frequency(self, frequency:float) -> None:
        print("frequency setter called")
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
            n_mod = map_range(
                amount,
                Instrument._MIN_PITCH_BEND,
                Instrument._MAX_PITCH_BEND,
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
            omega = map_range(
                amount,
                Instrument._MIN_MODULATE,
                Instrument._MAX_MODULATE,
                2,
                16) * math.pi
            
            self.top = (self.frequency+math.sin(omega * time.time()))

    def play(self) -> None:
        self.enable = True
        self.update()