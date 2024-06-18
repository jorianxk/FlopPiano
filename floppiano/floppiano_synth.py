from jidi.bus import BusException
from jidi.devices import Drive, Keyboard
from jidi.voices import DriveVoice
from jidi.synths import KeyboardSynth

class FlopPianoSynth(KeyboardSynth):
    """_summary_
        A Keyboard Synth and DriveSynth combined
    """

    def __init__(
            self,
            voices: tuple[DriveVoice],
            keyboard: Keyboard, 
            crash_mode:DriveVoice.CrashMode = DriveVoice.CrashMode.FLIP,
            spin:bool = False,        
            **kwargs) -> None:

        super().__init__(voices, keyboard, **kwargs)

        self.logger.name = "FlopPianoSynth"
        # Add support for crash mode and spin
        if 'crash_mode' not in self.control_change_map:
            self.control_change_map['crash_mode'] = 70
        
        if 'spin' not in self.control_change_map:
            self.control_change_map['spin'] = 75

        self.crash_mode = crash_mode
        self.spin = spin



    # overridden to update drive spin and crash modes
    def _sound(self) -> None:
        try:
            for voice in self._active_voices.values():
                voice.crash_mode = self.crash_mode
                voice.spin = self.spin
                voice.pitch_bend(self.pitch_bend, self.pitch_bend_range)
                voice.modulate(self.modulation, self.modulation_wave)
                voice.update((not self._muted))
        except BusException as be:
            self.logger.warning("voices failed to update")   
    

    #------------------Getters/Setters-----------------------------------------#

    @property
    def crash_mode(self)->DriveVoice.CrashMode:
        return self._crash_mode
    
    @crash_mode.setter
    def crash_mode(self, crash_mode:int) -> None:
        if crash_mode not in DriveVoice.CrashMode.__members__.values():
            self.logger.warning(
                f"crash_mode NOT set: {crash_mode} is not a valid mode")
            return
        self._crash_mode = crash_mode    
        self.logger.info(
            'crash_mode set: '
            f'{DriveVoice.CrashMode._member_names_[crash_mode]}')

    @property
    def spin(self):
        return self._spin

    @spin.setter
    def spin(self, spin:bool):
        self._spin = bool(spin)
        self.logger.info(f'spin set: {self.spin}')

