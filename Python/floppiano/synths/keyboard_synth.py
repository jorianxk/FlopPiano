from mido import Message

from Python.floppiano.devices.keyboard import Keys

from .synth import Synth
from ..bus import BusException
from ..voices import Voice
from ..devices.keyboard import Keyboard, KeyboardListener

class KeyboardSynth(Synth, KeyboardListener):

    START_NOTE = 11 #MIDI note 11 B -1

    def __init__(
        self, 
        voices: tuple[Voice],
        keyboard:Keyboard = None,
        do_keyboard = True,
        loopback = True,
        **kwargs) -> None:
        super().__init__(voices, **kwargs)

        self.do_keyboard = do_keyboard
        self.loopback = loopback
        self.keyboard = keyboard
        self.keyboard_octave = 0 #TODO replace this with keyboard.getoctave()

    #TODO: is this name accurate?
    def keyboard_messages(self) ->list[Message]:
        messages = []
        if self.do_keyboard:
            try: 
                #always do the read to maintain consistent-ish timing
                #TODO set all keyboard states before calling update!
                self.keyboard.update()
                #if loopback is off then wipe the messages
                if not self.loopback: messages = []

            except BusException as be:
                #This is normal just log it
                self.logger.debug("Error reading keyboard state - skipping")

        return messages

    #------------------Overrides from KeyboardListener-------------------------#
    def key_changed(self, key: Keys, pressed: bool) -> None:
        pass

    def pitch_changed(self, pitch: int) -> None:
        pass

    def modulation_changed(self, modulation: int) -> None:
        pass
    
    def _key_to_message(self, key:int, pressed)->Message:
        #TODO how do we know the sysex command or control #?
        match key:
            case Keys.MUTE:
                print("Mute", pressed) #gen mute message
            case Keys.OCTAVE_UP:
                return Message(
                    'sysex',
                    data = [self.sysex_id, 4, self.keyboard_octave + 1]
                )
            case Keys.OCTAVE_DOWN:
                return Message(
                    'sysex',
                    data = [self.sysex_id, 4, self.keyboard_octave - 1]
                )          
            case Keys.UNUSED:
                pass #do nothing how was an unused key pressed?
            case _:
                # key was pressed -> Note on
                if pressed:
                    return Message(
                        'note_on',
                        note = 12 * self.keyboard_octave + Keyboard.START_NOTE,
                        velocity = 1,
                        channel = self.input_channel
                    )
                #Key was released -> note off
                return Message(
                    'note_off',
                    note = 12 * self.keyboard_octave + Keyboard.START_NOTE,
                    channel = self.input_channel                  
                )


    #------------------------------Properties----------------------------------#
    @property
    def do_keyboard(self) -> bool:
        return self._do_keyboard
    
    @do_keyboard.setter
    def do_keyboard(self, do_keyboard:bool) -> None:
        self._do_keyboard = do_keyboard
    
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

        if self.keyboard is None:
            #We don't have a keyboard so don't attempt to r/w its states
            self.do_keyboard = False
            return

        self.keyboard.listener = self

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
