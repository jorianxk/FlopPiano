from mido import Message
from .synth import Synth


class DriveSynth(Synth):

    def __init__(
        self,
        #voices: tuple[DriveVoice],
        bow:bool = False,
        spin:bool = False,        
        **kwargs) -> None:

        super().__init__(**kwargs)
        
        # Add support for crash mode and spin
        if 'bow' not in self.control_change_map:
            self.control_change_map['bow'] = 70
        
        if 'spin' not in self.control_change_map:
            self.control_change_map['spin'] = 75

        self.bow = bow
        self.spin = spin


    #-------------------------Overrides from Synth-----------------------------#


    def note_on(self, msg: Message, source) -> Message:
        return None
 
    def note_off(self, msg: Message, source) -> Message:
        return None

    def reset(self) -> None:
        pass
  
    def sound(self) -> None:
        pass


    #------------------------------Properties----------------------------------#

    @property
    def bow(self)-> bool:
        return self._bow
    
    @bow.setter
    def bow(self, bow:bool) -> None:
        self._bow = bool(bow)

    @property
    def spin(self):
        return self._spin

    @spin.setter
    def spin(self, spin:bool):
        self._spin = bool(spin)

  
