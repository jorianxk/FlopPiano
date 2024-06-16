from enum import IntEnum, Enum
from mido import Message
import floppiano.bus as bus
from floppiano.midi import MIDIUtil



# Led states
# mute, Octave up, octave down, Octave #,



class Keyboard():
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


#TODO: fix byte masks
    def __init__(
            self,
            address:int = 0x77,
            output_channel:int=0,
            start_note:int = 35, #MIDI note 35 -> B1
            octave:int = 0) -> None:        
        
        self.address = address
        self.output_channel = output_channel
        self.start_note = start_note
        self.octave = octave

        
        #octave up led
        #octave down led
        #mute led



        self._last_state:list[int] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self._ctrl:int = 0



    def update(self) -> list[Message]:
        #TODO: where does ctrl update happen? led states in ctrl 
        messages = []
        
        # Get the states from the nano
        new_state = bus.read(self.address, self._ctrl, 9)
        print("Bytes")
        for b in new_state:    
            print("{:08b}".format(b))
        
        new_key_states   = new_state[0:5]
        new_pitch_states = new_state[5:7]
        new_mod_states   = new_state[7:]

        #Have the key states changed?
        if (self._last_state[0:5] != new_key_states):
            self._key_states_changed(new_key_states)
        
        #Has the pitch wheel changed?
        if (self._last_state[5:7] != new_pitch_states):
            pass #print("pitch changed!")

        #Has the mod wheel changed?
        if (self._last_state[7:] != new_mod_states):
            pass #print("mod changed!")
        
        #update the last state
        self._last_state = new_state

        #TODO return messages
        return []

    def _key_states_changed(self, new_key_states:list[int])-> list[Message]:
        messages = []
        #loop through each byte in the new key states(item in list)
        for byte_index, bite in enumerate(new_key_states):
            #XORing with the old state gives us only the bits which have
            #changed since the last state
            changed_bits = bite ^ self._last_state[byte_index]

            #Using the key byte map we can figure out which key was changed
            #and generate a mido message for that change
            for key_index, key in enumerate(Keyboard.KEY_BYTE_MAP[byte_index]):
                #A key's position in the key byte map determines its mask 
                key_mask = 2 ** abs(7 - key_index)

                #The key at key_index was changed
                if (key_mask & changed_bits):
                    #Was the key pressed or released? 
                    # pressed = True if the change was a press,
                    #  False if the change was a  release
                    pressed = bool(key_mask & bite) 
                    #Now generate the message
                    messages.append(self._key_to_message(key,pressed))
                
                #print(key_index,"{:08b}".format(key_mask), key_mask)
    

    def _key_to_message(self, key:int, pressed)->Message:
        match key:
            case Keyboard.Keys.MUTE:
                print("Mute", pressed) #gen mute message
            case Keyboard.Keys.OCTAVE_UP:
                print("Octave up", pressed) #gen octave up
            case Keyboard.Keys.OCTAVE_DOWN:
                print("Octave down", pressed)  #gen octave down
            case Keyboard.Keys.UNUSED:
                print("UNUSED", pressed)  #pass #do nothing
            case _:
                #this is a normal key press do the note, on off
                print(Keyboard.Keys._member_names_[key], pressed)

    
    @property
    def output_channel(self) -> int:
        return self._output_channel
    
    @output_channel.setter
    def output_channel(self, channel:int) -> None:
        if (channel <0 or channel>15):
            raise ValueError("Channel must be [0-15]") 
        self._output_channel = channel

    @property
    def start_note(self) -> int:
        return self._start_note

    @start_note.setter
    def start_note(self, note:int) -> None:
        #TODO What happens to octave when we change start note?
        if (MIDIUtil.isValidMIDINote(note)):
            self._start_note = note
            return
        raise ValueError(f'{note} is not a valid MIDI note')

    @property
    def octave(self) -> int:
        return self._octave
    
    @octave.setter
    def octave(self, octave_number:int) -> None:
        if (octave_number<0 or octave_number>8):
            raise ValueError(f'{octave_number} is not a valid octave number')
        #TODO update key midi mapping
        self._octave = octave_number
