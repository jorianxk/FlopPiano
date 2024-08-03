from enum import IntEnum
from abc import ABC, abstractmethod
from mido import Message

import floppiano.bus  as bus
from floppiano.midi import MIDIUtil
from floppiano.synths import Synth

"""
Keyboard Registers:

-------------- Register 0: Control (CTRL) - The LED State Register ------------- 

                                 WRITE ONLY
Consists of a single byte:

  MSB 7  |    6     |     5         |      4          |    3     |       2       |       1       |   LSB 0
---------|----------|---------------|-----------------|----------|---------------|---------------|--------------
not used | not used | octave_up_led | octave_down_led | mute_led | octave number | octave_number | octave number

Bits 0-2: Represent the zero indexed octave number [0-7] and which octave LED 
will be lit.

Bits 1-4: Represent the lighting state of the corresponding LED

-------------- Register 1: The input Register ----------------------------------

                                READ ONLY

Consists of 9 bytes that represent the state of the octave up, octave down,
mute, and 35 piano keys. Additionally, the register stores the analog read 
values for the pitch wheel and modulation wheel.

Byte 0 [MSB-> LSB]: Piano Keys: [ 3,  4,  5,  6,  7,  8,  9, 10]
Byte 1 [MSB-> LSB]: Piano Keys: [11, 12, 13, 14, 15, 16, 17, 18]
Byte 2 [MSB-> LSB]: Piano Keys: [19, 20, 21, 22, 23, 24, 25, 26]
Byte 3 [MSB-> LSB]: Piano Keys: [27, 28, 29, 30, 31, 32, 33, 34]
Byte 4 [MSB-> LSB]: [piano key 35, mute, octave up, octave down, piano key 1, piano key 2, not used, not used]

If a bit in bytes 0-4 is a logical true (1) then the key is pressed, otherwise
it is unpressed.

Bytes 5 & 6: When OR'd represent a the analog read value (0-1023) of the 
pitch wheel potentiometer

Bytes 7 & 8: When OR'd represent a the analog read value (0-1023) of the 
modulation wheel potentiometer


--------------------- Register 4 - Device Type ---------------------------------

                            READ ONLY

The Device type register is an 8 bit register, in which a device type integer is
stored. Reading this register on the keyboard should always result in a value of
55.

"""


#Constants
DEVICE_TYPE = 55
CTRL_REG = 0
INPUT_REG = 1


class Keys(IntEnum):
    """
        A Enum to store key values
    """
    UNUSED      = 0
    KEY_1       = 1
    KEY_2       = 2
    KEY_3       = 3
    KEY_4       = 4
    KEY_5       = 5
    KEY_6       = 6
    KEY_7       = 7
    KEY_8       = 8
    KEY_9       = 9
    KEY_10      = 10
    KEY_11      = 11
    KEY_12      = 12
    KEY_13      = 13
    KEY_14      = 14
    KEY_15      = 15
    KEY_16      = 16
    KEY_17      = 17
    KEY_18      = 18
    KEY_19      = 19
    KEY_20      = 20
    KEY_21      = 21
    KEY_22      = 22
    KEY_23      = 23
    KEY_24      = 24
    KEY_25      = 25
    KEY_26      = 26
    KEY_27      = 27
    KEY_28      = 28
    KEY_29      = 29
    KEY_30      = 30
    KEY_31      = 31
    KEY_32      = 32
    KEY_33      = 33
    KEY_34      = 34
    KEY_35      = 35
    MUTE        = 36
    OCTAVE_UP   = 37
    OCTAVE_DOWN = 38

class KeyboardListener(ABC):
    """
        An abstract class who's methods are called by a Keyboard object
        when keys are pressed/released.
    """

    def __init__(self) -> None:
        pass
    
    def _key_changed(self, key:Keys, pressed:bool) -> None:
        """
            Called when any key is pressed or released. invokes all other key 
            methods via a switch statement
        Args:
            key (Keys): The key that was pressed or released
            pressed (bool):  True if the key was pressed, false if the key was
            released
        """
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
    
    @abstractmethod
    def _mute_key(self, pressed:bool) -> None:
        """
            Called when the mute key is pressed or released
        Args:
            pressed (bool): True if the key was pressed, false if the key was
            released
        """
        pass
    
    @abstractmethod
    def _octave_up_key(self, pressed:bool) -> None:
        """
            Called when the octave up key is pressed or released
        Args:
            pressed (bool): True if the key was pressed, false if the key was
            released
        """
        pass
    
    @abstractmethod
    def _octave_down_key(self, pressed:bool) -> None:
        """
            Called when the octave down key is pressed or released
        Args:
            pressed (bool): True if the key was pressed, false if the key was
            released
        """
        pass
    
    @abstractmethod
    def _piano_key(self, key:Keys, pressed:bool) -> None:
        """
            Called when a piano key is pressed or released
        Args:
            key (Keys): The piano key that was pressed or released
            pressed (bool): True if the key was pressed, false if the key was
            released
        """

        pass
    
    @abstractmethod
    def _pitch_spin(self, pitch:int) -> None:
        """
            Called when the pitch wheel is changed
        Args:
            pitch (int): An integer in the range [0-1023] representing the 
            pitch
        """
        pass
    
    @abstractmethod
    def _modulation_spin(self, modulation:int) -> None:
        """
            Called when the modulation wheel wheel is changed
        Args:
            modulation (int): An integer in the range [0-1023] representing the 
            modulation value
        """
        pass

class Keyboard():
    """
         A class/object to read and write keyboard states (via I2C). Invokes
         key change callbacks in a Keyboard listener on an update() call.
    """
    # A map to sort out what bit in the incoming bytes represents each key
    KEY_BYTE_MAP = (
        (
            Keys.KEY_3, 
            Keys.KEY_4, 
            Keys.KEY_5, 
            Keys.KEY_6, 
            Keys.KEY_7, 
            Keys.KEY_8,
            Keys.KEY_9,
            Keys.KEY_10,
        ),
        (
            Keys.KEY_11, 
            Keys.KEY_12, 
            Keys.KEY_13, 
            Keys.KEY_14, 
            Keys.KEY_15, 
            Keys.KEY_16,
            Keys.KEY_17,
            Keys.KEY_18,
        ),
        (
            Keys.KEY_19, 
            Keys.KEY_20, 
            Keys.KEY_21, 
            Keys.KEY_22, 
            Keys.KEY_23, 
            Keys.KEY_24,
            Keys.KEY_25,
            Keys.KEY_26,
        ),
        (
            Keys.KEY_27, 
            Keys.KEY_28, 
            Keys.KEY_29, 
            Keys.KEY_30, 
            Keys.KEY_31, 
            Keys.KEY_32,
            Keys.KEY_33,
            Keys.KEY_34,
        ),
        (
            Keys.KEY_35, 
            Keys.MUTE, 
            Keys.OCTAVE_UP, 
            Keys.OCTAVE_DOWN, 
            Keys.KEY_1, 
            Keys.KEY_2,
            Keys.UNUSED,
            Keys.UNUSED,
        )
    )

    def __init__(
        self,
        listener:KeyboardListener=None,
        address:int = 0x77,
        mute_led:bool = False,
        octave_up_led:bool = False,
        octave_down_led:bool = False,
        octave:int = 2) -> None:
        """
            Constructs a Keyboard object.
        Args:
            listener (KeyboardListener, optional): The KeyboardListener
                to invoke callbacks in. Defaults to None.
            address (int, optional): The I2C Address of the keyboard. Defaults 
                to 0x77.
            mute_led (bool, optional): The starting state of the mute led.
                Defaults to False (off).
            octave_up_led (bool, optional): The starting state of the octave up
                led. Defaults to False (off).
            octave_down_led (bool, optional): The starting state of the octave 
                up led. Defaults to False (off).
            octave (int, optional): The starting octave led. Defaults to 2.
        """

        self.listener = listener
        self.address = address
        self.mute_led = mute_led
        self.octave_up_led = octave_up_led
        self.octave_down_led = octave_down_led
        self.octave = octave

        # Array/List of the last read key states 
        self._last_state:list[int] = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    def update(self) -> None:
        """
            Immediately writes all LED states to the Keyboard then reads all key
            states from the keyboard. If a key state has changed since the last
            update() call, the appropriate call back in the KeyboardListener 
            will be invoked.
        """
        # Update the ctrl register 
        ctrl = (self.octave_up_led << 5)
        ctrl = ctrl | (self.octave_down_led << 4)
        ctrl = ctrl | (self.mute_led << 3)
        ctrl = ctrl | self.octave
        bus.write(self.address, CTRL_REG, [ctrl])

        # Update the ctrl register and read the states from the nano
        new_state = bus.read(self.address, INPUT_REG, 9)

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
        #update the listener
        if self.listener is not None:
            self.listener._pitch_spin(pitch)
        
    def _mod(self, new_mod_states:list[int]) -> None:
        # combine the modulation upper and lower bytes
        mod = (new_mod_states[0] << 8) | new_mod_states[1]
        
        # TODO Mod analog read int-wraps when in lowest wheel position
        if mod > 1023: mod = 0

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

class MIDIKeyboard(KeyboardListener):
    """
        A class to generate MIDI from a Keyboard key presses
    """

    #The intended starting MIDI note (KEY_1) of the keyboard
    START_NOTE = 11
    
    def __init__(self, address:int=119, synth:Synth = None) -> None:
        """
            Construct a MIDIKeyboard. If synth is not specified MIDI will
            be generated on MIDI Channel 0.
        Args:
            address (int, optional): The I2C address of the Keyboard. 
                Defaults to 119.
            synth (Synth, optional): The Synth that will receive the generated
                MIDI. Defaults to None. If specified the MIDIKeyboard will 
                always match the mute state and input channel of the synth. 
                (via synth property observer). Additionally, the MIDIKeyboard
                will generate MIDI messages that match the synth's command maps.
        """
        
        if synth is None:
            # Set defaults
            self._muted = False
            self._channel = 0
            self._mute_cc = 120
            self._reset_cc = 121
            self._modulation_cc = 1
        else:
            # Set up an observer on the synth muted property, so that when
            # it is changed, the MIDIKeyboard will match the Synth's muted state
            synth.attach_observer('muted', self._mute)
            # Initial state
            self._muted = synth.muted
            # Set up an observer on the synth input_channel property, so that 
            # when it is changed, the MIDIKeyboard will match the Synth's
            synth.attach_observer('input_channel', self._input_channel)
            # initial state
            self._channel = synth.input_channel
            # Match the cc numbers to the synth's
            self._mute_cc = synth.control_change_map.code('mute')
            self._reset_cc = synth.control_change_map.code('reset')
            self._modulation_cc = synth.control_change_map.code('modulation')
        
        #Create a keyboard
        self._keyboard = Keyboard(
            listener = None,
            address = address, 
            mute_led = self._muted,
            octave_up_led = True,
            octave_down_led = True,
            octave=2)
        # Update once to initialize the LEDs
        self._keyboard.update()
        # Set the keyboard's listener to self (after update so that update does
        # not trigger key callbacks when initializing the LEDs)
        self._keyboard.listener = self

        # A list of all the MIDI messages created on an update() call
        self._output:list[Message] = []

        self._last_pitch = 510 # The Nominal middle value on the pitch wheel

    def update(self) -> list[Message]:
        """
            Should be called at the regularly and at the rate in which the
            keyboard should be polled. Produces a list of MIDI Messages as a 
            result of keyboard key presses. 
        Returns:
            list[Message]: The list of MIDI messages produced by the 
                MIDIKeyboard
        """
        # Call the keyboard update to pump all key/state callbacks and to set 
        # the LED states
        self._keyboard.update()

        # Clear/Flush the output
        output_buffer = self._output
        self._output = []

        return output_buffer

    def _mute(self, muted:bool):
        # Force the Mute LED and mute property to match muted param.
        # This method will be called by the synth (if set) when it's mute
        # state changes.
        self._keyboard.mute_led = self._muted = muted
    
    def _input_channel(self, input_channel:int):
        # This method will be called by the synth (if set) when it's input 
        # channel changes.
        self._channel = input_channel

    def _mute_key(self, pressed: bool) -> None:
        # Toggle between 'mute' and 'reset' MIDI Messages on a mute key press 
        if pressed:
            msg = None
            if self._muted:
                msg = Message(
                    type='control_change',
                    control = self._reset_cc,
                    value = 0,
                    channel = self._channel)
            else:
               msg = Message(
                    type='control_change',
                    control = self._mute_cc,
                    value = 0,
                    channel = self._channel)
            # Write the message to the output              
            self._output.append(msg)
    
    def _piano_key(self, key:Keys, pressed:bool) -> None:
        # Generate the appropriate 'note on' or 'note off' with the correct
        # MIDI Note on a Piano key press
        note = (self._keyboard.octave * 12 ) + (key-1) + MIDIKeyboard.START_NOTE

        if MIDIUtil.isValidNote(note):
            msg = None
            if pressed:
                # A key was pressed so send a note on
                msg = Message(
                    type = 'note_on',
                    note = note,
                    velocity = 1, #Velocity but be >1 to be a note on
                    channel = self._channel)
            else:
                # A key was released so send a note off
                msg = Message(
                    type = 'note_off',
                    note = note,
                    channel = self._channel)            
            self._output.append(msg)
        else:
            # TODO EasterEggs
            raise NotImplementedError("You pressed the secret buttons")
   
    
    def _octave_up_key(self, pressed: bool) -> None:
        # On an octave up press shift octave up
        if pressed:
            if self._keyboard.octave == 7:
                # Wrap the octave back to 0
                self._keyboard.octave = 0
            else: 
                self._keyboard.octave += 1
            # Send a reset to kill all active notes in the previous octave
            self._output.append(Message(
                type='control_change',
                control = self._reset_cc,
                value = 0,
                channel = self._channel)
            )
            
    
    def _octave_down_key(self, pressed: bool) -> None:
        # On an octave down move the octave down
        if pressed:
            if self._keyboard.octave == 0:
                # Wrap around
                self._keyboard.octave = 7
            else: 
                self._keyboard.octave -= 1
            # Send a reset to kill all active notes in the previous octave
            self._output.append(Message(
                type='control_change',
                control = self._reset_cc,
                value = 0,
                channel = self._channel)
            )
    
    def _pitch_spin(self, pitch: int) -> None:
        # map the pitch to a valid midi pitch range
        # from arduino analog read (10 bit) range
        pitch = MIDIUtil.integer_map_range(
            pitch,
            0,
            1023,
            -8192,
            8191
        )

        # Enforce the wheel dead zone (It's done in firmware but it's done here
        # to ensure that the dead zone sticks if the potentiometer drifts)
        if pitch>= -10 and pitch<= 10:
            pitch  = 0
         
        self._output.append(Message(
            type='pitchwheel',
            pitch = pitch,
            channel = self._channel
        ))
    
    def _modulation_spin(self, modulation: int) -> None:
        # map the mod to a valid control change value range 
        # from arduino analog read (10 bit) range
        mod = MIDIUtil.integer_map_range(
            modulation,
            0,
            1023,
            0,
            127
        )
        
        self._output.append(Message(
            type='control_change',
            control = self._modulation_cc,
            value = mod,
            channel = self._channel
        ))