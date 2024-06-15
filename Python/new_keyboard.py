from enum import IntEnum, Enum
from mido import Message
import floppiano.bus as bus
from floppiano.midi import MIDIUtil



# Led states
# mute, Octave up, octave down, Octave #,



class Keyboard():
    class Keys(IntEnum):
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
        MUTE        = 34
        OCTAVE_UP   = 35
        OCTAVE_DOWN = 36
        UNUSED      = 36

#TODO: fix byte masks
    BYTE_0 = {
        Keys.KEY_1  : 0b10000000,
        Keys.KEY_2  : 0b01000000,
        Keys.KEY_3  : 0b00100000,
        Keys.KEY_4  : 0b00010000,
        Keys.KEY_5  : 0b00001000,
        Keys.KEY_6  : 0b00000100,
        Keys.KEY_7  : 0b00000010,
        Keys.KEY_8  : 0b00000001
    }

    BYTE_1 = {
        Keys.KEY_9  : 0b10000000,
        Keys.KEY_10 : 0b01000000,
        Keys.KEY_11 : 0b00100000,
        Keys.KEY_12 : 0b00010000,
        Keys.KEY_13 : 0b00001000,
        Keys.KEY_14 : 0b00000100,
        Keys.KEY_15 : 0b00000010,
        Keys.KEY_16 : 0b00000001
    }

    BYTE_2 = {
        Keys.KEY_17 : 0b01000000,
        Keys.KEY_18 : 0b00100000,
        Keys.KEY_19 : 0b00010000,
        Keys.KEY_20 : 0b00001000,
        Keys.KEY_21 : 0b00000100,
        Keys.KEY_22 : 0b00000010,
        Keys.KEY_23 : 0b00000001,
        Keys.KEY_24 : 0b10000000
    }

    BYTE_3 = {
        Keys.KEY_25 : 0b01000000,
        Keys.KEY_26 : 0b00100000,
        Keys.KEY_27 : 0b00010000,
        Keys.KEY_28 : 0b00001000,
        Keys.KEY_29 : 0b00000100,
        Keys.KEY_30 : 0b00000010,
        Keys.KEY_31 : 0b00000001,
        Keys.KEY_32 : 0b10000000
    }

    BYTE_4 = {
        Keys.KEY_33      : 0b01000000,
        Keys.MUTE        : 0b00100000,
        Keys.OCTAVE_UP   : 0b00010000,
        Keys.OCTAVE_DOWN : 0b00001000,
        Keys.UNUSED      : 0b00000100,
        Keys.UNUSED      : 0b00000010,
        Keys.UNUSED      : 0b00000001,
        Keys.UNUSED      : 0b10000000
    }
    

    def __init__(
            self,
            address:int = 0x77,
            output_channel:int=0,
            start_note:int = 35,
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



    def update(self) -> list[Message]:
        #TODO: where does ctrl update happen? led states in ctrl 
        
        
        # Get the states from the nano
        new_state = bus.read(self.address, self._ctrl, 9)
        
        #TODO: compare new_state with last state

        #TODO return messages
        return []
    