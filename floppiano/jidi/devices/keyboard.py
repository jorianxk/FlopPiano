from enum import IntEnum
from .device import Device
from .. import bus
from ..midi import MIDIUtil

class Keys(IntEnum):
        KEY_1       = 0
        KEY_2       = 1
        KEY_3       = 2
        KEY_4       = 3
        KEY_5       = 4
        KEY_6       = 5
        KEY_7       = 6
        KEY_8       = 7
        KEY_9       = 8
        KEY_10      = 9
        KEY_11      = 10
        KEY_12      = 11
        KEY_13      = 12
        KEY_14      = 13
        KEY_15      = 14
        KEY_16      = 15
        KEY_17      = 16
        KEY_18      = 17
        KEY_19      = 18
        KEY_20      = 19
        KEY_21      = 20
        KEY_22      = 21
        KEY_23      = 22
        KEY_24      = 23
        KEY_25      = 24
        KEY_26      = 25
        KEY_27      = 26
        KEY_28      = 27
        KEY_29      = 28
        KEY_30      = 29
        KEY_31      = 30
        KEY_32      = 31
        KEY_33      = 32
        MUTE        = 33
        OCTAVE_UP   = 34
        OCTAVE_DOWN = 35
        UNUSED      = 36

class KeyboardListener():

    def __init__(self) -> None:
        pass
    
    def _key_changed(self, key:Keys, pressed:bool) -> None:
        match key:
            case Keys.MUTE:
               self._mute_key(pressed)
            case Keys.OCTAVE_UP:
                self._octave_up_key(pressed)
            case Keys.OCTAVE_DOWN:
                self._octave_down_key(pressed)
            case Keys.UNUSED:
                pass
            case _:
                self._piano_key(key, pressed)        
    
    def _mute_key(self, pressed:bool) -> None:
        pass

    def _octave_up_key(self, pressed:bool) -> None:
        pass

    def _octave_down_key(self, pressed:bool) -> None:
        pass

    def _piano_key(self, key:Keys, pressed:bool) -> None:
        pass

    def _pitch_spin(self, pitch:int) -> None:
        pass

    def _modulation_spin(self, modulation:int) -> None:
        pass

class Keyboard(Device):
    KEY_BYTE_MAP = (
        (
            Keys.KEY_1, 
            Keys.KEY_2, 
            Keys.KEY_3, 
            Keys.KEY_4, 
            Keys.KEY_5, 
            Keys.KEY_6,
            Keys.KEY_7,
            Keys.KEY_8,
        ),
        (
            Keys.KEY_9, 
            Keys.KEY_10, 
            Keys.KEY_11, 
            Keys.KEY_12, 
            Keys.KEY_13, 
            Keys.KEY_14,
            Keys.KEY_15,
            Keys.KEY_16,
        ),
        (
            Keys.KEY_17, 
            Keys.KEY_18, 
            Keys.KEY_19, 
            Keys.KEY_20, 
            Keys.KEY_21, 
            Keys.KEY_22,
            Keys.KEY_23,
            Keys.KEY_24,
        ),
        (
            Keys.KEY_25, 
            Keys.KEY_26, 
            Keys.KEY_27, 
            Keys.KEY_28, 
            Keys.KEY_29, 
            Keys.KEY_30,
            Keys.KEY_31,
            Keys.KEY_32,
        ),
        (
            Keys.KEY_33, 
            Keys.MUTE, 
            Keys.OCTAVE_UP, 
            Keys.OCTAVE_DOWN, 
            Keys.UNUSED, 
            Keys.UNUSED,
            Keys.UNUSED,
            Keys.UNUSED,
        )
    )

    #The intended starting MIDI note (KEY_1) of the keyboard
    START_NOTE = 11

    def __init__(
            self,
            listener:KeyboardListener=None,
            address:int = 0x77,
            mute_led:bool = False,
            octave_up_led:bool = False,
            octave_down_led:bool = False,
            octave:int = 2) -> None:        
        
        self.listener = listener
        self.address = address
        self.mute_led = mute_led
        self.octave_up_led = octave_up_led
        self.octave_down_led = octave_down_led
        
        self.octave = octave

        self._last_state:list[int] = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    def update(self) -> None:
        # Update the ctrl register 
        ctrl = (self.mute_led << 5)
        ctrl = ctrl | (self.octave_up_led << 4)
        ctrl = ctrl | (self.octave_down_led << 3)
        ctrl = ctrl | self.octave

        # Update the ctrl register and read the states from the nano
        new_state = bus.read(self.address, ctrl, 9)

        # for b in new_state:    
        #     print("{:08b}".format(b))

        new_key_states   = new_state[0:5]
        new_pitch_states = new_state[5:7]
        new_mod_states   = new_state[7:]

        #Have the key states changed?
        if (self._last_state[0:5] != new_key_states):
            self._key(new_key_states)
        
        #Has the pitch wheel changed?
        if (self._last_state[5:7] != new_pitch_states):
            self._pitch(new_pitch_states)

        #Has the mod wheel changed?
        if (self._last_state[7:] != new_mod_states):
            self._mod(new_mod_states)
        
        #update the last state
        self._last_state = new_state

    def _key(self, new_key_states:list[int]) -> None:
        #loop through each byte in the new key states(item in list)
        for byte_index, bite in enumerate(new_key_states):
            #XORing with the old state gives us only the bits which have
            #changed since the last state
            changed_bits = bite ^ self._last_state[byte_index]

            #Using the key byte map we can figure out which key was changed
            #then update the listener to that change
            for key_index, key in enumerate(Keyboard.KEY_BYTE_MAP[byte_index]):
                #A key's position in the key byte map determines its mask 
                key_mask = 2 ** abs(7 - key_index)
                #The key at key_index was changed
                if (key_mask & changed_bits):
                    #Was the key pressed or released? 
                    # pressed = True if the change was a press,
                    # pressed = False if the change was a release
                    pressed = bool(key_mask & bite) 
                    #Now tell the listener what happened
                    if (self.listener is not None):
                        self.listener._key_changed(key, pressed)
                
    def _pitch(self, new_pitch_states:list[int]) -> None:
        # combine the pitch Upper and lower bytes
        pitch = (new_pitch_states[0] << 8 ) | new_pitch_states[1]
        #map the pitch to a valid midi pitch range
        # from arduino analog read (10 bit) range
        pitch = MIDIUtil.integer_map_range(
            pitch,
            0,
            1023,
            -8192,
            8191
        )  

        #update the listener
        if self.listener is not None:
            self.listener._pitch_spin(pitch)
        
    def _mod(self, new_mod_states:list[int]) -> None:
        # combine the modulation upper and lower bytes
        mod = (new_mod_states[0] << 8) | new_mod_states[1]
        
        #map the mod to a valid control change value range 
        # from arduino analog read (10 bit) range
        mod = MIDIUtil.integer_map_range(
            mod,
            0,
            1023,
            0,
            127
        )

        if self.listener is not None:
            self.listener._modulation_spin(mod)
    
    @property 
    def octave(self):
        return self._octave
    
    @octave.setter
    def octave(self, octave:int):
        if (octave<0 or octave>7):
            raise ValueError(f'{octave} is not a valid octave')
        self._octave = octave


