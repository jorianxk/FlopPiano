from mido import Message


from .synth import OutputModes
from .keyboard_synth import KeyboardSynth
from ..voices import DriveVoice

class DriveSynth(KeyboardSynth):


    DEFAULT_CONTROL_CHANGE_MAP ={
        1  : 'modulation',
        70 : 'crash_mode',
        75 : 'spin',
        76 : 'pitch_bend_range',
        120: 'silence',
        123: 'muted'
    }

    DEFAULT_SYSEX_MAP = {
        0: 'input_channel',
        1: 'output_channel',
        2: 'output_mode',
        3: 'loopback',
        4: 'keyboard_octave'
    }


    def __init__(
        self,
        voices: tuple[DriveVoice],
        crash_mode:DriveVoice.CrashMode = DriveVoice.CrashMode.FLIP,
        spin:bool = False,        
        **kwargs) -> None:

        super().__init__(voices, **kwargs)

 
        self.crash_mode = crash_mode
        self.spin = spin



        self._available_voices:list[DriveVoice] = list(voices)
        self._active_incoming_voices:dict[int, DriveVoice] = {}
        self._active_keyboard_voices:dict[int, DriveVoice] = {}

        self._output:list[Message] = []


    def update(self, messages: list[Message]) -> list[Message]:
        #get keyboard messages if any, then parse them
        key_msgs = self.keyboard_messages()
        for msg in key_msgs: self._parse(msg, source='keyboard')
        
        #Now process all the messages from the message parameter
        for msg in messages: self._parse(msg,source='incoming')

        #Makes sounds
        all_active_voices = list(self._active_incoming_voices.values())
        all_active_voices.extend(list(self._active_keyboard_voices.values()))
        for voice in all_active_voices:
            voice.pitch_bend(self.pitch_bend, self.pitch_bend_range)
            voice.modulate(self.modulation, self.modulation_wave)
            voice.update((not self._muted))

        #Ready the output
        output_buffer:list[Message] = []        
        match self.output_mode:
            case OutputModes.OFF:
                #output buffer is already empty
                pass
            case OutputModes.ROLLOVER:
                output_buffer = self._output
            case OutputModes.KEYS:
                output_buffer = key_msgs
            case _: pass
        
        #clear the the output
        self._output = []
        #Return the output
        return output_buffer


    def reset(self) -> None:
        #silence all voices using super().reset()
        super().reset()
        
        #Add the active incoming DriveVoices back to the available voices stack
        self._available_voices.extend(
            list(self._active_incoming_voices.values()))
        #Clear the active incoming DriveVoices Stack
        self._active_incoming_voices = {}

        #Add the active keyboard DriveVoices back to the available voices stack
        self._available_voices.extend(
            list(self._active_keyboard_voices.values()))        
        #Clear the active keyboard DriveVoices Stack
        self._active_keyboard_voices = {}
        
    



    ##----------------Overrides from MIDIListener------------------------------#

        


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

  
