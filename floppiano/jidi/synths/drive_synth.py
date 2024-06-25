from mido import Message

from .synth import Synth
from ..voices import Voice, DriveVoice
from ..bus import BusException


class DriveSynth(Synth):

    def __init__(
        self,
        voices: tuple[DriveVoice],
        crash_mode:DriveVoice.CrashMode = DriveVoice.CrashMode.FLIP,
        spin:bool = False,        
        **kwargs) -> None:

        super().__init__(voices, **kwargs)
        
        self.logger.name = "DriveSynth"
        # Add support for crash mode and spin
        if 'crash_mode' not in self.control_change_map:
            self.control_change_map['crash_mode'] = 70
        
        if 'spin' not in self.control_change_map:
            self.control_change_map['spin'] = 75

        self.crash_mode = crash_mode
        self.spin = spin


    #-------------------------Overrides from Synth-----------------------------#

    # overridden to update drive spin and crash modes
    def _sound(self) -> None:
        for voice in self._active_voices.values():
            voice.crash_mode = self.crash_mode
            voice.spin = self.spin
            voice.pitch_bend(self.pitch_bend, self.pitch_bend_range)
            voice.modulate(self.modulation, self.modulation_wave)
            voice.update((not self._muted))


    #------------------------------Properties----------------------------------#

    @property
    def crash_mode(self)->DriveVoice.CrashMode:
        return self._crash_mode
    
    @crash_mode.setter
    def crash_mode(self, crash_mode:int) -> None:
        if crash_mode not in DriveVoice.CrashMode.__members__.values():
            raise ValueError('Not a valid CrashMode')
        self._crash_mode = crash_mode    


    @property
    def spin(self):
        return self._spin

    @spin.setter
    def spin(self, spin:bool):
        self._spin = bool(spin)

  
