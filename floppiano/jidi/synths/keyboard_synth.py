import traceback
from mido import Message

from .synth import Synth
from ..bus import BusException
from ..voices import Voice
from ..devices.keyboard import Keys, Keyboard, KeyboardListener

class KeyboardSynth(Synth, KeyboardListener):

    def __init__(
        self, 
        voices: tuple[Voice],
        keyboard:Keyboard,
        loopback = True,
        keyboard_octave = 2,
        **kwargs) -> None:

        Synth.__init__(self, voices, **kwargs)

        self.logger.name = "KeyboardSynth"

        #add support for key output mode if we don't already have it
        if 'keys' not in self.output_modes:
            self.output_modes.append('keys')
        
        #add support setting loopback mode and keyboard octave via sysex msg
        # if not already added
        if 'loopback' not in self.sysex_map:
            self.sysex_map['loopback'] = 3
        if 'keyboard_octave' not in self.sysex_map:
            self.sysex_map['keyboard_octave'] = 4   

        self._keyboard_messages:list[Message] = []
        self._active_keyboard_voices:dict[int, Voice] = {}

        self.loopback = loopback
        self.keyboard_octave = keyboard_octave
        self.keyboard = keyboard

    #-----------------------------Overrides from Synth-------------------------#

    def update(self, messages: list[Message]) -> list[Message]:
        #overridden to process keyboard input
        try: 
            #We always do the read to maintain consistent-ish timing                
            #update the keyboard states before updating
            self.keyboard.octave_down_led = True
            self.keyboard.octave_down_led = True
            self.keyboard.mute_led = self.muted
            self.keyboard.octave = self.keyboard_octave
            self.keyboard.update()
        except BusException as be:
            #This is normal just log it
            self.logger.debug(
                "BusException while updating keyboard states - skipping")
        except Exception as e:
            self.logger.debug(
                f'Exception while updating keyboard states - skipping'
                f'\n{traceback.format_exc()}')

        for msg in self._keyboard_messages: self._parse(msg, source='keyboard')
        
        #sound keyboard voices
        self._sound_keyboard_voices()

        return Synth.update(self, messages)   
    
    def reset(self) -> None:
        Synth.reset(self)
        self.reset_keyboard_voices()   

    def reset_keyboard_voices(self) -> None:
        try:        
            #quite any active sounding voices
            for voice in self._active_keyboard_voices.values():
                voice.update(make_noise=False)

            self.logger.info("keyboard voices silenced") 

        except BusException as be:
            self.logger.warning(
                "keyboard voices failed to silence")         

        #clear the active stack
        self._available_voices.extend(
            list(self._active_keyboard_voices.values()))        
        self._active_keyboard_voices = {}
        self.logger.info("keyboard stack cleared")
    
    def _sound_keyboard_voices(self) -> None:
        try:
            for voice in self._active_keyboard_voices.values():
                voice.pitch_bend(self.pitch_bend, self.pitch_bend_range)
                voice.modulate(self.modulation, self.modulation_wave)
                voice.update((not self._muted))
        except BusException as be:
            self.logger.warning(
                "keyboard voices failed to update")

    def _flush_output(self) -> list[Message]:
        #overridden to add support for keys output type
        #Ready the output
        output_buffer:list[Message] = []        
        match self.output_mode:
            case 0: #output mode off
                #output buffer is already empty
                pass
            case 1: #rollover mode
                output_buffer = self._output
            case 2: #key mode
                output_buffer = self._keyboard_messages
            case _:
                #should never happen output mode setter prevents this
                raise ValueError("Can not ready output - invalid output mode")

        #clear the keyboard message buffer
        self._keyboard_messages = []
        #clear the the output
        self._output = []       
        return output_buffer

    def _note_on(self, msg: Message, source) -> None:
        if source == 'keyboard':
            self._voice_on(msg, source, self._active_keyboard_voices)
        else:
            Synth._note_on(self, msg, source)
    
    def _note_off(self, msg: Message, source) -> None:
        if source == 'keyboard':
            self._voice_off(msg, source, self._active_keyboard_voices)
        else:
            Synth._note_off(self, msg, source)

    #------------------Overrides from KeyboardListener-------------------------#
    def _mute_key(self, pressed:bool) -> None:
        if pressed:
            self._keyboard_messages.append(
                Message(
                    'control_change',
                    control = self.control_change_map.code('muted'),
                    channel = self.input_channel,
                    value = (not self.muted) #toggle mute                
                )
            )

    def _octave_up_key(self, pressed:bool) -> None:
        if pressed:
            new_octave = self.keyboard_octave + 1
             #TODO more elegant way to check octave?
            if new_octave>=0 and new_octave<=127:
                self._keyboard_messages.append(
                    Message(
                        'sysex',
                        data = [
                            self.sysex_id, 
                            self.sysex_map.code('keyboard_octave'), 
                            new_octave]
                    )
                )

    def _octave_down_key(self, pressed:bool) -> None:
        if pressed:
            new_octave = self.keyboard_octave - 1
             #TODO more elegant way to check octave?
            if new_octave>=0 and new_octave<=127:
                self._keyboard_messages.append(
                    Message(
                        'sysex',
                        data = [
                            self.sysex_id, 
                            self.sysex_map.code('keyboard_octave'), 
                            new_octave]
                    )
                )

    def _piano_key(self, key:Keys, pressed:bool) -> None:
        if self.loopback:
            msg = None
            note = (12 * self.keyboard_octave + Keyboard.START_NOTE) + key
            if pressed:# Key was pressed -> Note on
                msg =  Message(
                    'note_on',
                    note = note,
                    velocity = 1,
                    channel = self.input_channel
                )
            else: # Key was released -> note off
                msg = Message(
                    'note_off',
                    note = note,
                    channel = self.input_channel                  
                )        
            self._keyboard_messages.append(msg)

    def _pitch_spin(self, pitch:int) -> None:
        if self.loopback:
            self._keyboard_messages.append(
                Message(
                    'pitchwheel',
                    pitch = pitch,
                    channel = self.input_channel)
            )

    def _modulation_spin(self, modulation:int) -> None:
        if self.loopback:
            self._keyboard_messages.append(
                Message(
                    'control_change',
                    control = 1,
                    value = modulation,
                    channel = self.input_channel)
            )
    

    #------------------------------Properties----------------------------------#
    @property
    def loopback(self) -> bool:
        return self._loopback

    @loopback.setter
    def loopback(self, loopback:int) -> None:
        self._loopback = bool(loopback)
        self.logger.info(f'loopback set: {self.loopback}')

    @property
    def keyboard_octave(self) -> int:
        return self._keyboard_octave
    
    @keyboard_octave.setter
    def keyboard_octave(self, octave:int) -> None:
        if (octave<0 or octave>7):
            self.logger.info(
                'keyboard_octave NOT set: '
                f'{octave} is not valid'
            )
            return
        
        self.reset_keyboard_voices()
        self._keyboard_octave = octave        
        self.logger.info(f'keyboard_octave set: {self.keyboard_octave}')

    @property
    def keyboard(self) -> Keyboard:
        return self._keyboard
    
    @keyboard.setter
    def keyboard(self, keyboard:Keyboard) -> None:
        self._keyboard = keyboard
        #set up the keyboard to match self
        self.keyboard.listener = self
        self.keyboard.octave = self.keyboard_octave
