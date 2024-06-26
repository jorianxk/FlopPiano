from enum import Enum, IntEnum
from ..midi import MIDIUtil

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


class Voice():
    """
        An Voice is:
            -Monophonic (sounds one note at a time)
            -Plays MIDI a midi note
            -Its note can be pitch bent 
            -Its note can be modulated 
    """
    def __init__(self) -> None:
        
        self._note = None
        self._sounding = False
    
    
    @property
    def sounding(self) -> bool:
        return self._sounding   
    
    @property    
    def note(self) -> int:
        return self._note
    
    @note.setter
    def note(self, note:int) -> None:
        if not MIDIUtil.isValidNote(note):
            raise ValueError(f'{note} is not a valid MIDI note')
        self._note = note

    def pitch_bend(self, pitch:int, pitch_bend_range:PitchBendRange) -> None:
        if not MIDIUtil.isValidPitch(pitch):
            raise ValueError(f'{pitch} is not a valid MIDI pitch')

    def modulate(self, modulation:int, modulation_wave:ModulationWave) -> None:
        if not MIDIUtil.isValidModulation(modulation):
            raise ValueError(f'{modulation} is not a valid MIDI modulation')

    def sound(self):
        self._sounding = True

    def silence(self):
        self._sounding = False


