import math
from mido import Message

#TODO: Make listener and Parser abstract?
class MIDIUtil():
    #https://en.wikipedia.org/wiki/Piano_key_frequencies
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
    def freq2n(frequency:float)->int:
        n = 12 * math.log2(frequency/440) +49
        return n
    
    @staticmethod
    def n2freq(n:float)->float:
        #n = note - 20
        freq = math.pow(2,(n-49)/12)*440
        #freq = round(freq,3)
        return freq

    @staticmethod
    def MIDI2Freq(note:int) -> float:
        if(not MIDIUtil.isValidMIDINote(note)):
            raise ValueError("Note must be in the range [0,127]")
        return MIDIUtil.MIDI_LOOK_UP[note]['freq']

    @staticmethod 
    def MIDI2notation(note:int) -> str:
        if(not MIDIUtil.isValidMIDINote(note)):
            raise ValueError("Note must be in the range [0,127]")
        
        return MIDIUtil.MIDI_LOOK_UP[note]['name']
    
    @staticmethod
    def freq2MIDI(frequency:float)->int:
        n = MIDIUtil.freq2n(frequency)
        note = round(n+20)

        if (MIDIUtil.isValidMIDINote(note)):
            return note

        raise ValueError(f'Frequency {frequency:0.3f} is not a midi note')

    @staticmethod
    def isValidMIDINote(note:int)->bool:
        if(note <0 or note>127):
            return False
        return True

    @staticmethod
    def isValidMIDIChannel(channel:int)-> bool:
        if (channel<0 or channel >15):
            return False
        return True
    
    @staticmethod
    def integer_map_range(x, in_min, in_max, out_min, out_max) -> int:
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

class MIDIListener():

    def __init__(self, input_channel:int =0) -> None:
        self.input_channel = input_channel
    
    @property
    def input_channel(self) -> int:
        return self._input_channel
    
    @input_channel.setter
    def input_channel(self, channel:int):
        if MIDIUtil.isValidMIDIChannel(channel):
            raise ValueError("Channel must be [0-15]") 
        self._input_channel = channel

    def note_on(self, msg:Message, source):
        pass

    def note_off(self, msg:Message, source):
        pass
    
    def control_change(self, msg:Message, source):
        pass
    
    def pitchwheel(self, msg:Message, source):
        pass

    def sysex(self, msg:Message, source):
        pass
    
    def start(self, msg:Message, source):
        pass

    def stop(self, msg:Message, source):
        pass

    def reset(self, msg:Message, source):
        pass

class MIDIParser():
    
    def __init__(self, listener:MIDIListener) -> None:
        self.listener = listener
    
    def parse(self, msg:Message, source = None):

        # This check is to filter out messages that have a channel, and that 
        # channel is not our listener's channel.
        if (MIDIParser.has_channel(msg)):
            if (msg.channel != self.listener.input_channel): return
        
        match msg.type:
            case 'note_on':
                #A 'note on' with velocity 0 is commonly a 'note off'
                if (msg.velocity == 0):
                    self.listener.note_off(msg, source)
                else:
                    self.listener.note_on(msg, source)
            case 'note_off':
                self.listener.note_off(msg, source)
            case 'control_change':
                self.listener.control_change(msg, source)
            case 'pitchwheel':
                self.listener.pitchwheel(msg, source)
            case 'sysex':
                self.listener.sysex(msg, source)
            case 'start':
                self.listener.start(msg, source)
            case 'stop':
                self.listener.stop(msg, source)
            case 'reset':
                self.listener.reset(msg, source)
            case _:
                pass

    @staticmethod
    def has_channel(msg:Message)->bool:    
        try:
            msg.channel
            return True
        except AttributeError as ae:
            return False
