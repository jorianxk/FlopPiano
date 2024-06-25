from mido import Message
from jidi.bus import BusException
from jidi.devices import Drive, Keyboard
from jidi.voices import Voice , DriveVoice
from jidi.synths import KeyboardSynth

class FlopPianoSynth(KeyboardSynth):
    """_summary_
        A Keyboard Synth and DriveSynth combined
    """

    def __init__(
        self,
        voices: tuple[DriveVoice],
        keyboard:Keyboard,
        crash_mode:DriveVoice.CrashMode = DriveVoice.CrashMode.FLIP,
        spin:bool = False,        
        **kwargs) -> None:

        super().__init__(voices, keyboard, **kwargs)
        
        self.logger.name = "DriveSynth"
        # Add support for crash mode and spin
        if 'crash_mode' not in self.control_change_map:
            self.control_change_map['crash_mode'] = 70
        
        if 'spin' not in self.control_change_map:
            self.control_change_map['spin'] = 75

        self.crash_mode = crash_mode
        self.spin = spin


    #-------------------------Overrides from Synth-----------------------------#
    #overridden to change log message
    def _voice_on(
            self, 
            msg:Message, 
            source:str,
            active_stack:dict[int, Voice]) -> None:
        try:
            #get an available voice and remove it from the pool
            nextVoice:DriveVoice = self._available_voices.pop()

            #Modify the note to match the incoming message
            nextVoice.note = msg.note

            #add the note to the active voice, so that it will be played
            active_stack[msg.note] = nextVoice

            self.logger.debug(
                f'added: {msg.note} to {source} stack [{nextVoice.address}]')

        except IndexError as ie: #There are no available voices. 
            self.logger.debug(
                f'could not add: {msg.note} to {source} stack, '
                'no available voices - rolled')
            #We can't play it so pass it along
            self._output.append(msg)
    
    def _voice_off(
            self,
            msg:Message,
            source:str, 
            active_stack:dict[int, Voice]) -> None:
        try:
            #get the active Voice
            playedVoice:DriveVoice = active_stack.pop(msg.note)

            #stop the note playing
            playedVoice.update(make_noise=False)
            self.logger.debug(
                f'removed: {msg.note} from {source} active stack [{playedVoice.address}]')          

            #add the drive back to the available voice pool
            self._available_voices.append(playedVoice)

        except KeyError as ke:
            self.logger.debug(
                f'could not remove: {msg.note} from {source} stack, '
                f"it's not playing [rolled?]") 
            #if we're not playing that note pass it along
            self._output.append(msg)
        except BusException as be:
            self.logger.warning(
                f'could not remove: {msg.note} from {source} active stack,'
                ' there was was a problem silencing the voice') 


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
