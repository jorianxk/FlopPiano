import math
from mido import Message

class MIDIUtil():
    """_summary_
        A helper class for all things MIDI
    """


    # A look-up table of midi note numbers, frequency and notation
    # https://en.wikipedia.org/wiki/Piano_key_frequencies
    MIDI_LOOK_UP = {
        0:{"freq":8.176,"name":""},
        1:{"freq":8.662,"name":""},
        2:{"freq":9.177,"name":""},
        3:{"freq":9.723,"name":""},
        4:{"freq":10.301,"name":""},
        5:{"freq":10.913,"name":""},
        6:{"freq":11.562,"name":""},
        7:{"freq":12.25,"name":""},
        8:{"freq":12.978,"name":""},
        9:{"freq":13.75,"name":""},
        10:{"freq":14.568,"name":""},
        11:{"freq":15.434,"name":""},
        12:{"freq":16.352,"name":""},
        13:{"freq":17.324,"name":""},
        14:{"freq":18.354,"name":""},
        15:{"freq":19.445,"name":""},
        16:{"freq":20.602,"name":""},
        17:{"freq":21.827,"name":""},
        18:{"freq":23.125,"name":""},
        19:{"freq":24.5,"name":""},
        20:{"freq":25.957,"name":""},
        21:{"freq":27.5,"name":"A0"},
        22:{"freq":29.135,"name":"A#0/Bb0"},
        23:{"freq":30.868,"name":"B0"},
        24:{"freq":32.703,"name":"C1"},
        25:{"freq":34.648,"name":"C#1/Db1"},
        26:{"freq":36.708,"name":"D1"},
        27:{"freq":38.891,"name":"D#1/Eb1"},
        28:{"freq":41.203,"name":"E1"},
        29:{"freq":43.654,"name":"F1"},
        30:{"freq":46.249,"name":"F#1/Gb1"},
        31:{"freq":48.999,"name":"G1"},
        32:{"freq":51.913,"name":"G#1/Ab1"},
        33:{"freq":55,"name":"A1"},
        34:{"freq":58.27,"name":"A#1/Bb1"},
        35:{"freq":61.735,"name":"B1"},
        36:{"freq":65.406,"name":"C2"},
        37:{"freq":69.296,"name":"C#2/Db2"},
        38:{"freq":73.416,"name":"D2"},
        39:{"freq":77.782,"name":"D#2/Eb2"},
        40:{"freq":82.407,"name":"E2"},
        41:{"freq":87.307,"name":"F2"},
        42:{"freq":92.499,"name":"F#2/Gb2"},
        43:{"freq":97.999,"name":"G2"},
        44:{"freq":103.826,"name":"G#2/Ab2"},
        45:{"freq":110,"name":"A2"},
        46:{"freq":116.541,"name":"A#2/Bb2"},
        47:{"freq":123.471,"name":"B2"},
        48:{"freq":130.813,"name":"C3"},
        49:{"freq":138.591,"name":"C#3/Db3"},
        50:{"freq":146.832,"name":"D3"},
        51:{"freq":155.563,"name":"D#3/Eb3"},
        52:{"freq":164.814,"name":"E3"},
        53:{"freq":174.614,"name":"F3"},
        54:{"freq":184.997,"name":"F#3/Gb3"},
        55:{"freq":195.998,"name":"G3"},
        56:{"freq":207.652,"name":"G#3/Ab3"},
        57:{"freq":220,"name":"A3"},
        58:{"freq":233.082,"name":"A#3/Bb3"},
        59:{"freq":246.942,"name":"B3"},
        60:{"freq":261.626,"name":"C4"},
        61:{"freq":277.183,"name":"C#4/Db4"},
        62:{"freq":293.665,"name":"D4"},
        63:{"freq":311.127,"name":"D#4/Eb4"},
        64:{"freq":329.628,"name":"E4"},
        65:{"freq":349.228,"name":"F4"},
        66:{"freq":369.994,"name":"F#4/Gb4"},
        67:{"freq":391.995,"name":"G4"},
        68:{"freq":415.305,"name":"G#4/Ab4"},
        69:{"freq":440,"name":"A4"},
        70:{"freq":466.164,"name":"A#4/Bb4"},
        71:{"freq":493.883,"name":"B4"},
        72:{"freq":523.251,"name":"C5"},
        73:{"freq":554.365,"name":"C#5/Db5"},
        74:{"freq":587.33,"name":"D5"},
        75:{"freq":622.254,"name":"D#5/Eb5"},
        76:{"freq":659.255,"name":"E5"},
        77:{"freq":698.456,"name":"F5"},
        78:{"freq":739.989,"name":"F#5/Gb5"},
        79:{"freq":783.991,"name":"G5"},
        80:{"freq":830.609,"name":"G#5/Ab5"},
        81:{"freq":880,"name":"A5"},
        82:{"freq":932.328,"name":"A#5/Bb5"},
        83:{"freq":987.767,"name":"B5"},
        84:{"freq":1046.502,"name":"C6"},
        85:{"freq":1108.731,"name":"C#6/Db6"},
        86:{"freq":1174.659,"name":"D6"},
        87:{"freq":1244.508,"name":"D#6/Eb6"},
        88:{"freq":1318.51,"name":"E6"},
        89:{"freq":1396.913,"name":"F6"},
        90:{"freq":1479.978,"name":"F#6/Gb6"},
        91:{"freq":1567.982,"name":"G6"},
        92:{"freq":1661.219,"name":"G#6/Ab6"},
        93:{"freq":1760,"name":"A6"},
        94:{"freq":1864.655,"name":"A#6/Bb6"},
        95:{"freq":1975.533,"name":"B6"},
        96:{"freq":2093.005,"name":"C7"},
        97:{"freq":2217.461,"name":"C#7/Db7"},
        98:{"freq":2349.318,"name":"D7"},
        99:{"freq":2489.016,"name":"D#7/Eb7"},
        100:{"freq":2637.02,"name":"E7"},
        101:{"freq":2793.826,"name":"F7"},
        102:{"freq":2959.955,"name":"F#7/Gb7"},
        103:{"freq":3135.963,"name":"G7"},
        104:{"freq":3322.438,"name":"G#7/Ab7"},
        105:{"freq":3520,"name":"A7"},
        106:{"freq":3729.31,"name":"A#7/Bb7"},
        107:{"freq":3951.066,"name":"B7"},
        108:{"freq":4186.009,"name":"C8"},
        109:{"freq":4434.922,"name":"C#8/Db8"},
        110:{"freq":4698.636,"name":"D8"},
        111:{"freq":4978.032,"name":"D#8/Eb8"},
        112:{"freq":5274.041,"name":"E8"},
        113:{"freq":5587.652,"name":"F8"},
        114:{"freq":5919.911,"name":"F#8/Gb8"},
        115:{"freq":6271.927,"name":"G8"},
        116:{"freq":6644.875,"name":"G#8/Ab8"},
        117:{"freq":7040,"name":"A8"},
        118:{"freq":7458.62,"name":"A#8/Bb8"},
        119:{"freq":7902.133,"name":"B8"},
        120:{"freq":8372.018,"name":""},
        121:{"freq":8869.844,"name":""},
        122:{"freq":9397.273,"name":""},
        123:{"freq":9956.063,"name":""},
        124:{"freq":10548.082,"name":""},
        125:{"freq":11175.303,"name":""},
        126:{"freq":11839.822,"name":""},
        127:{"freq":12543.854,"name":""}
        }


    @staticmethod
    def freq2n(frequency:float) -> float:
        """_summary_
            Given an frequency, returns the corresponding 'n' value.
            See: https://en.wikipedia.org/wiki/Piano_key_frequencies
            
        Args:
            frequency (float): A frequency in Hz

        Returns:
            float: The 'n' value
        """
        n = 12 * math.log2(frequency/440) + 49
        return n
    
    @staticmethod
    def n2freq(n:float) -> float:
        """_summary_
            Given a 'n' value, returns corresponding the frequency.
            See: https://en.wikipedia.org/wiki/Piano_key_frequencies
        Args:
            n (float): The 'n' value

        Returns:
            float: The frequency in Hz
        """
        #n = note - 20
        freq = math.pow(2,(n-49)/12)*440
        #freq = round(freq,3)
        return freq

    @staticmethod
    def MIDI2Freq(note:int) -> float:
        """_summary_
            Given a MIDI note number, returns the frequency of the note
        Args:
            note (int): A MIDI note number

        Raises:
            ValueError: If the note given is not in the range [0,127]. i.e not 
                a MIDI note

        Returns:
            float: The frequency in Hz of the MIDI note.
        """
        if(not MIDIUtil.isValidMIDINote(note)):
            raise ValueError("Note must be in the range [0,127]")
        return MIDIUtil.MIDI_LOOK_UP[note]['freq']

    @staticmethod 
    def MIDI2notation(note:int) -> str:
        """_summary_
            Given a MIDI note number, returns the musical scientific name for 
            the note.
        Args:
            note (int): A MIDI note number

        Raises:
            ValueError: If the note given is not in the range [0,127]. i.e. not 
                a MIDI note

        Returns:
            str: The musical scientific notation of the note.
        """
        if(not MIDIUtil.isValidMIDINote(note)):
            raise ValueError("Note must be in the range [0,127]")    
        
        return MIDIUtil.MIDI_LOOK_UP[note]['name']
    
    @staticmethod
    def freq2MIDI(frequency:float) -> int:
        """_summary_
            Given a frequency, returns a the corresponding MIDI note.
        Args:
            frequency (float): The frequency in Hz

        Raises:
            ValueError: If the frequency is not a MIDI note

        Returns:
            int: The corresponding MIDI Note number
        """
        n = MIDIUtil.freq2n(frequency)
        note = round(n+20)

        if (MIDIUtil.isValidMIDINote(note)):
            return note

        raise ValueError(f'Frequency {frequency:0.3f} is not a midi note')

    @staticmethod
    def isValidNote(note:int) -> bool:
        """_summary_
            Given an integer, returns True if that integer is a MIDI note.
            i.e. in the range [0,127]
        Args:
            note (int): The integer to test

        Returns:
            bool: True if the integer is a MIDI note, False otherwise
        """
        if(note <0 or note>127):
            return False
        return True

    @staticmethod
    def isValidChannel(channel:int) -> bool:
        """_summary_
            Given an integer, returns True if that integer is a MIDI channel.
            i.e. in the range [0,15] (Note: zero Indexed because of mido)
        Args:
            note (int): The integer to test

        Returns:
            bool: True if the integer is a MIDI channel, False otherwise
        """        
        if (channel<0 or channel >15):
            return False
        return True
    
    @staticmethod
    def isValidPitch(pitch:int) -> bool:
        """_summary_
            Given an integer, returns True if that integer is a MIDI pitch.
            i.e. in the range [-8192,8191] 
        Args:
            note (int): The integer to test

        Returns:
            bool: True if the integer is a MIDI pitch, False otherwise
        """  
        if pitch < -8192 or pitch > 8191:
            return False
        return True
    
    @staticmethod
    def isValidModulation(modulation:int) -> bool:
        """_summary_
            Given an integer, returns True if that integer is a MIDI modulation.
            i.e. in the range [0,127] 
        Args:
            note (int): The integer to test

        Returns:
            bool: True if the integer is a MIDI modulation, False otherwise
        """  
        return MIDIUtil.isValidNote(modulation)

    @staticmethod
    def hasChannel(msg:Message) -> bool:
        """_summary_
            Given a mido.Message returns true if that message has the 'channel'
            attribute
        Args:
            msg (Message): A mido Message to test

        Returns:
            bool: True if the Message has a channel, false otherwise
        """
        try:
            msg.channel
            return True
        except AttributeError as ae:
            return False

    @staticmethod
    def integer_map_range(x, in_min, in_max, out_min, out_max) -> int:
        """_summary_
            A function to map a number in one range, to a another number in 
            another range - preforms integer division. 
            See:https://www.arduino.cc/reference/en/language/functions/math/map/
        Args:
            x (_type_): The number to map
            in_min (_type_): The lower bound of the value's current range. 
            in_max (_type_): The upper bound of the value's current range.
            out_min (_type_): The lower bound of the value's target range.
            out_max (_type_): The upper bound of the value's target range.

        Returns:
            int: The number x, mapped to the out range
        """
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

class MIDIListener():

    def __init__(self, input_channel:int = 0) -> None:
        """_summary_
            A class that should be inherited from. A MIDIListener has methods 
            that are invoked when a corresponding MIDIParser parses a message            
        Args:
            input_channel (int, optional): The MIDI channel which the listener
                should receive messages from.
        """
        self.input_channel = input_channel
    
    @property
    def input_channel(self) -> int:
        """_summary_
            The MIDI channel the listener is sensitive to.
        Returns:
            int: The MIDI channel the listener is sensitive to.
        """
        return self._input_channel
    
    @input_channel.setter
    def input_channel(self, channel:int) -> None:
        """_summary_
            Set's the input channel of the listener
        Args:
            channel (int): The channel to be set 

        Raises:
            ValueError: If the channel is not a valid MIDI channel
        """
        if not MIDIUtil.isValidChannel(channel):
            raise ValueError("Channel must be [0-15]") 
        self._input_channel = channel

    def on_note_on(self, msg:Message, source) -> None:
        """_summary_
            Invoked by a MIDIParser when a 'note on' message is received
        Args:
            msg (Message): the mido.Message received
            source (_type_): A parameter for the source of the message 
                (defaults to None)
        """
        pass

    def on_note_off(self, msg:Message, source) -> None:
        """_summary_
            Invoked by a MIDIParser when a 'note off' message is received
        Args:
            msg (Message): the mido.Message received
            source (_type_): A parameter for the source of the message 
                (defaults to None)
        """
        pass
    
    def on_control_change(self, msg:Message, source) -> None:
        """_summary_
            Invoked by a MIDIParser when a 'control change' message is received
        Args:
            msg (Message): the mido.Message received
            source (_type_): A parameter for the source of the message 
                (defaults to None)
        """
        pass
    
    def on_pitchwheel(self, msg:Message, source) -> None:
        """_summary_
            Invoked by a MIDIParser when a 'pitchwheel' message is received
        Args:
            msg (Message): the mido.Message received
            source (_type_): A parameter for the source of the message 
                (defaults to None)
        """
        pass

    def on_sysex(self, msg:Message, source) -> None:
        """_summary_
            Invoked by a MIDIParser when a 'sysex' message is received
        Args:
            msg (Message): the mido.Message received
            source (_type_): A parameter for the source of the message 
                (defaults to None)
        """
        pass

class MIDIParser():
    
    def __init__(self, listener:MIDIListener) -> None:
        """_summary_
            A class to parse (or switch, or invoke) MIDIListener callbacks
            when a mido MIDI Message is parsed via MIDIListener.parse()
        Args:
            listener (MIDIListener): The MIDIListener to invoke
        """
        self.listener = listener
    
    def parse(self, msg:Message, source = None) -> None:
        """_summary_
            Parses the MIDI mido Message. If the message has a valid MIDI 
            channel and that channel is the MIDIListeners channel the 
            corresponding on_<message type>() method in the listener will be 
            invoked. If the message has no channel attribute either no method 
            will be invoked, or the corresponding (non-channeled) message method
            will be invoked. (ex. sysex) 

            Note: A 'note on' message with a velocity of zero is interpreted as
            a 'note_off'  
        Args:
            msg (Message): The message to parse
            source (_type_, optional): An optional source to pass to the
             MIDIListener Defaults to None.
        """

        # This check is to filter out messages that have a channel, and that 
        # channel is not our listener's channel.
        if (MIDIUtil.hasChannel(msg)):
            if (msg.channel != self.listener.input_channel): return
        
        match msg.type:
            case 'note_on':
                #A 'note on' with velocity 0 is commonly a 'note off'
                if (msg.velocity == 0):
                    self.listener.on_note_off(msg, source)
                else:
                    self.listener.on_note_on(msg, source)
            case 'note_off':
                self.listener.on_note_off(msg, source)
            case 'control_change':
                self.listener.on_control_change(msg, source)
            case 'pitchwheel':
                self.listener.on_pitchwheel(msg, source)
            case 'sysex':
                self.listener.on_sysex(msg, source)
            case _:
                pass
