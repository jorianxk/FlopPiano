from mido import Message

from .synth import Synth
from ..bus import BusException
from ..voices import Voice
from ..devices.keyboard import Keys, Keyboard, KeyboardListener

class KeyboardSynth(Synth, KeyboardListener):

    SYSEX_LOOPBACK = 3
    SYSEX_KEYBOARD_OCTAVE = 4

    def __init__(
        self, 
        voices: tuple[Voice],
        keyboard:Keyboard,
        loopback = True,
        keyboard_octave = 2,
        **kwargs) -> None:

        #add support for key output mode
        self.OUTPUT_MODES.append('keys')
        
        #add support setting loopback mode and keyboard octave via sysex msg
        self.DEFAULT_SYSEX_MAP[KeyboardSynth.SYSEX_LOOPBACK] = 'loopback'
        self.DEFAULT_SYSEX_MAP[KeyboardSynth.SYSEX_KEYBOARD_OCTAVE] = \
            'keyboard_octave'

        super().__init__(voices, **kwargs)

        self.loopback = loopback
        self.keyboard_octave = keyboard_octave
        self.keyboard = keyboard


        self._keyboard_messages:list[Message] = []
        self._active_keyboard_voices:list[Voice] = []


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
            self.logger.debug("Error reading keyboard states - skipping")


        for msg in self._keyboard_messages: self._parse(msg, source='keyboard')
        
        
        return super().update(messages)
    
    
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
                self._keyboard_messages = []
            case _:
                #should never happen output mode setter prevents this
                raise ValueError("Can not ready output - invalid output mode")
            
        #clear the the output
        self._output = []       
        return output_buffer


    #------------------Overrides from KeyboardListener-------------------------#
    def _key_changed(self, key: Keys, pressed: bool) -> None:
        if self.loopback:
            key_msg = self._key2message(key,pressed)
            if key_msg is not None: self._keyboard_messages.append(key_msg)

    def _pitch_changed(self, pitch: int) -> None:
        if self.loopback:
            self._keyboard_messages.append(
                Message(
                    'pitchwheel',
                    pitch = pitch,
                    channel = self.input_channel)
            )

    def _modulation_changed(self, modulation: int) -> None:
        if self.loopback:
            self._keyboard_messages.append(
                Message(
                    'control_change',
                    control = 1,
                    value = modulation,
                    channel = self.input_channel)
            )
    
    def _key2message(self, key:int, pressed)->Message:
        match key:
            case Keys.MUTE:
                return Message(
                    'sysex',
                    data = [
                        self.sysex_id,
                        123, #TODO: how do we know this?
                        not self.muted #Flop the mute state
                    ]
                )
            case Keys.OCTAVE_UP:
                return Message(
                    'sysex',
                    data = [
                        self.sysex_id, 
                        KeyboardSynth.SYSEX_KEYBOARD_OCTAVE, 
                        self.keyboard_octave + 1]
                )
            case Keys.OCTAVE_DOWN:
                return Message(
                    'sysex',
                    data = [
                        self.sysex_id, 
                        KeyboardSynth.SYSEX_KEYBOARD_OCTAVE, 
                        self.keyboard_octave - 1]
                )          
            case Keys.UNUSED:
                return None
            case _:
                # key was pressed -> Note on
                note = (12 * self.keyboard_octave + Keyboard.START_NOTE) + key
                if pressed:
                    return Message(
                        'note_on',
                        note = note,
                        velocity = 1,
                        channel = self.input_channel
                    )
                #Key was released -> note off
                return Message(
                    'note_off',
                    note = note,
                    channel = self.input_channel                  
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
    def keyboard(self) -> Keyboard:
        return self._keyboard
    
    @keyboard.setter
    def keyboard(self, keyboard:Keyboard) -> None:
        self._keyboard = keyboard
        #set up the keyboard to match self
        self.keyboard.listener = self
        self.keyboard.octave = self.keyboard_octave

    @property
    def keyboard_octave(self) -> int:
        return self._keyboard_octave
    
    @keyboard_octave.setter
    def keyboard_octave(self, octave:int) -> None:
        if (octave<0 or octave>7):
            self.logger.info(
                'keyboard_octave NOT set: '
                f'{self.keyboard_octave} is not valid'
            )
            return
        self._keyboard_octave = octave
        #TODO reset keyboard voices 
        self.logger.info(f'keyboard_octave set: {self.keyboard_octave}')
