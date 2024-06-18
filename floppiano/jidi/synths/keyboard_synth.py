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

        # add support for 'keys' output mode if we don't already have it
        if 'keys' not in self.output_modes:
            self.output_modes.append('keys')
        
        # add support setting loopback mode and keyboard octave via sysex msg
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


    #------------------------------Methods-------------------------------------#

    def reset_keyboard_voices(self) -> None:
        #quiet any active sounding keyboard voices
        #we need to do this before clearing the active keyboard stack
        for voice in self._active_keyboard_voices.values():
            #this could cause a BusException
            voice.update(make_noise=False)

        self.logger.info("keyboard voices silenced") 

        #clear the active keyboard stack
        self._available_voices.extend(
            list(self._active_keyboard_voices.values()))        
        self._active_keyboard_voices = {}
        self.logger.info("keyboard active stack cleared")
   
    def _sound_keyboard_voices(self) -> None:
        for voice in self._active_keyboard_voices.values():
            voice.pitch_bend(self.pitch_bend, self.pitch_bend_range)
            voice.modulate(self.modulation, self.modulation_wave)
            #This could cause a BusException
            voice.update((not self._muted))


    #-------------------------Overrides from Synth-----------------------------#

    def update(self, messages: list[Message]) -> list[Message]:
        #overridden to process keyboard input

        #update keyboard 
        try: 
            # We always do the read to maintain consistent-ish timing                
            # update the keyboard states before calling update()
            self.keyboard.octave_down_led = True
            self.keyboard.octave_down_led = True
            self.keyboard.mute_led = self.muted
            self.keyboard.octave = self.keyboard_octave
            # This invoke KeyboardListener methods - in turn they will add 
            # messages to self._keyboard_messages
            self.keyboard.update() 
        except BusException as be:
            #This is normal just log it
            self.logger.debug(
                f'on update() keyboard (bus): {be} - skipping')
        except Exception as e:
            self.logger.error(
                f'on update() keyboard: {e} - skipping')

        #parse all the keyboard messages
        try:
            for msg in self._keyboard_messages: 
                self._parse(msg, source='keyboard')
        except Exception as e:
            self.logger.error(
                f'on update() could not parse keyboard messages - {e}')
        
        #sound keyboard voices
        try:
            self._sound_keyboard_voices()
        except Exception as e:
            self.logger.error(
                f'on update() could not sound keyboard voices - {e}')            

        #let the Parent class handle its voices. 
        return Synth.update(self, messages)   
    
    def reset(self) -> None:
        # Clear active stack and silence ALL voices
        Synth.reset(self)
        # Clear the keyboard active stack
        self.reset_keyboard_voices() 

    def _flush_output(self) -> list[Message]:
        #overridden to add support for 'keys' output type
        #Ready the output
        output_buffer:list[Message] = []        
        match self.output_mode:
            case 0: #self.output_modes.index('off') -> off 
                #output buffer is already empty, nothing to do
                pass
            case 1: #self.output_modes.index('rollover') -> rollover 
                output_buffer = self._output
            case 2: #self.output_modes.index('keys') -> keys
                output_buffer = self._keyboard_messages
            case _:
                #a new output mode has probably been added - we don't know
                # what to do with it so don't do anything
                pass

        #clear the keyboard messages
        self._keyboard_messages = []
        #clear the the output
        self._output = []       
        return output_buffer

    def _note_on(self, msg: Message, source) -> None:
        # Overridden to redirect keyboard input messages to keyboard active 
        # stack
        if source == 'keyboard':
            self._voice_on(msg, source, self._active_keyboard_voices)
        else:
            Synth._note_on(self, msg, source)
    
    def _note_off(self, msg: Message, source) -> None:
        # Overridden to redirect keyboard input messages to keyboard active 
        # stack
        if source == 'keyboard':
            self._voice_off(msg, source, self._active_keyboard_voices)
        else:
            Synth._note_off(self, msg, source)


    #---------Overrides from KeyboardListener handles Keyboard events----------#

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
            new_octave = self.keyboard_octave + 1 # go up an octave
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
            new_octave = self.keyboard_octave - 1 # go down an octave
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

    @property
    def keyboard_octave(self) -> int:
        return self._keyboard_octave
    
    @keyboard_octave.setter
    def keyboard_octave(self, octave:int) -> None:
        if (octave<0 or octave>7):
            raise ValueError('Not a valid octave')

        # could cause a BusException 
        self.reset_keyboard_voices()
        self._keyboard_octave = octave

    @property
    def keyboard(self) -> Keyboard:
        return self._keyboard
    
    @keyboard.setter
    def keyboard(self, keyboard:Keyboard) -> None:
        self._keyboard = keyboard
        # set up the keyboard to invoke our event handlers and to match our 
        # states
        self.keyboard.listener = self
        self.keyboard.mute_led = self.muted
        self.keyboard.octave_up_led = True
        self.keyboard.octave_down_led = True
        self.keyboard.octave = self.keyboard_octave
