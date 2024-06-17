from enum import Enum, IntEnum
from mido import Message

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
        if (note <Voice._MIN_NOTE or note >Voice._MAX_NOTE):
            raise ValueError(f'{note} is not a valid MIDI note')
        self._note = note

    def pitch_bend(self, amount:int, pitch_bend_range:PitchBendRange) -> None:
        if amount<Voice._MIN_PITCH_BEND or amount>Voice._MAX_PITCH_BEND:
            raise ValueError(f'{amount} is not a valid MIDI pitch')

    def modulate(self, amount:int, modulation_wave:ModulationWave) -> None:
        if amount<Voice._MIN_MODULATION or amount>Voice._MAX_MODULATION:
            raise ValueError(f'{amount} is not a valid MIDI modulation value')

    def update(self, make_noise:bool) -> None:
        pass


