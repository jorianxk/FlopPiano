from mido import Message
import logging
import time
from enum import IntEnum
import math


from .bus import BusException
from .midi import MIDIListener, MIDIParser, MIDIUtil
from .devices import Keyboard
from .voices import PitchBendRange, ModulationWave, Voice, DriveVoice


class OutputModes(IntEnum):
    __order__ = 'OFF ROLLOVER KEYS'    
    OFF = 0
    ROLLOVER = 1
    KEYS = 2


class Synth(MIDIParser, MIDIListener):

    #warning: type checking: no explicit errors!
    def __init__(
        self, 
        voices:tuple[Voice],
        input_channel:int = 0,
        output_channel:int = 0,
        output_mode = OutputModes.ROLLOVER,
        pitch_bend_range:PitchBendRange = PitchBendRange.OCTAVE,
        pitch_bend:int = 0,
        modulation_wave:ModulationWave = ModulationWave.SINE,
        modulation: int = 0,
        muted:bool = False,) -> None:

        #logger goes before super, because super calls self.input_channel which ahs been 
        # overridden
        self.logger = logging.getLogger(__name__) 
        MIDIListener.__init__(self, input_channel)
        MIDIParser.__init__(self, self)
 
        self._voices = voices

        #self.input_chanel = input_channel

        self.output_channel = output_channel
        self.output_mode = output_mode

        
        self.pitch_bend_range = pitch_bend_range
        self.pitch_bend = pitch_bend

        self.modulation_wave = modulation_wave
        self.modulation = modulation

        self.muted = muted
    
    def update(self, messages:list[Message])->list[Message]:
        pass

    def silence(self):
        for voice in self.voices:
            voice.update(make_noise=False)
    
    @property
    def voices(self) -> tuple[Voice]:
        return self._voices
    
    # #TODO: Handle what happens when instruments change!
    # CAN NOT CHANGE VOICES After instantiation
    # @voices.setter
    # def voices(self, voices:tuple[Voice]) -> None:
    #     self._voices = voices

    #@property for input channel in super class MidiListener

    @MIDIListener.input_channel.setter
    def input_channel(self, channel:int) -> None:
        #Overridden super() setter because we don't want exceptions for bad
        #channel parameters
        if channel<0 or channel >15:
            self.logger.warning(
                f"input_chanel NOT set: {channel} is not a valid channel")
            return
        self._input_channel = channel
        self.logger.info(
            f'input_chanel set: {self.input_channel}')

    @property
    def output_channel(self) -> int:
        return self._output_channel
    
    @output_channel.setter
    def output_channel(self, channel:int) -> None:
        if channel<0 or channel >15:
            self.logger.warning(
                f"output_channel NOT set: {channel} is not a valid channel")
            return
        self._output_channel = channel
        self.logger.info(
            f'output_channel set: {self.output_channel}')
    
    @property
    def output_mode(self) -> OutputModes:
        return self._output_mode
    
    @output_mode.setter
    def output_mode(self, output_mode:int) -> None:
        if output_mode not in OutputModes.__members__.values():
            self.logger.warning(
                f"output_mode NOT set: {output_mode} is not a valid mode")
            return
        self._output_mode = output_mode
        self.logger.info(
            'output_mode set: '
            f'{OutputModes._member_names_[output_mode]}')

    @property
    def pitch_bend_range (self) -> PitchBendRange:
        return self._pitch_bend_range
    
    @pitch_bend_range.setter
    def pitch_bend_range(self, pitch_bend_range):
        if isinstance(pitch_bend_range, PitchBendRange):
            pitch_bend_range = list(PitchBendRange).index(pitch_bend_range)

        if pitch_bend_range<0 or pitch_bend_range>len(PitchBendRange)-1:
            self.logger.warning(
                f"pitch_bend_range NOT set: {pitch_bend_range} not valid")
            return

        self._pitch_bend_range = list(
            PitchBendRange.__members__.values())[pitch_bend_range]

        self.logger.info(
            'pitch_bend_range set: '
            f'{PitchBendRange._member_names_[pitch_bend_range]}')

    @property
    def pitch_bend(self) -> int:
        return self._pitch_bend
    
    @pitch_bend.setter
    def pitch_bend(self, pitch_bend:int) -> None:
        if (pitch_bend < Voice._MIN_PITCH_BEND or 
            pitch_bend > Voice._MAX_PITCH_BEND):
            self.logger.debug(f'pitch_bend NOT set: {pitch_bend} not valid')
            return
        self._pitch_bend = pitch_bend
        self.logger.debug(f'pitch_bend set: {self.pitch_bend}')
    
    @property
    def modulation_wave(self) -> ModulationWave:
        return self._modulation_wave

    @modulation_wave.setter
    def modulation_wave(self, modulation_wave:int) -> None:
        if modulation_wave not in ModulationWave.__members__.values():
            self.logger.warning(
                f"modulation_wave NOT set: {modulation_wave} is not valid")
            return
        self._modulation_wave = modulation_wave
        self.logger.info(
            'modulation_wave set: '
            f'{ModulationWave._member_names_[modulation_wave]}')
 
    @property
    def modulation(self) ->int:
        return self._modulation
    
    @modulation.setter
    def modulation(self, modulation:int) -> None:
        if (modulation < Voice._MIN_MODULATION or 
            modulation > Voice._MAX_MODULATION):
            self.logger.debug(
                f"modulation NOT set: {modulation} not valid")
            return

        self._modulation = modulation
        self.logger.debug(f"modulation set: {modulation}")

    @property
    def muted(self):
        return self._muted
    
    @muted.setter
    def muted(self, muted:bool):
        self._muted = bool(muted)
        self.logger.info(f'muted set: {self.muted}')

class KeyboardSynth(Synth):

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
                messages = self.keyboard.read()
                #if loopback is off then wipe the messages
                if not self.loopback: messages = []

            except BusException as be:
                #This is normal just log it
                self.logger.debug("Error reading keyboard state - skipping")

        return messages

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

    @property
    def keyboard_octave(self) -> int:
        return self._keyboard_octave
    
    @keyboard_octave.setter
    def keyboard_octave(self, octave:int) -> None:
        self._keyboard_octave = octave
        # if self.keyboard is None:
        #     return
        # else:
        #     #TODO: validate the octave then set the keyboard octave
        #     #self.keyboard.setoctave()
        #     self._keyboard_octave = octave
        self.logger.info(f'keyboard_octave set: {self.keyboard_octave}')

class DriveSynth(KeyboardSynth):


    DEFAULT_CONTROL_CHANGE_MAP ={
        1  : 'modulation',
        70 : 'crash_mode',
        75 : 'spin',
        76 : 'pitch_bend_range',
        120: 'silence',
        123: 'muted'

    }

    DEFAULT_SYSEX_MAP = {
        0: 'input_channel',
        1: 'output_channel',
        2: 'output_mode',
        3: 'loopback',
        4: 'keyboard_octave'
    }


    def __init__(
        self,
        voices: tuple[DriveVoice],
        keyboard: Keyboard = None,
        sysex_id:int = 123,
        crash_mode:DriveVoice.CrashMode = DriveVoice.CrashMode.FLIP,
        spin:bool = False,        
        control_change_map:dict[int, str] = DEFAULT_CONTROL_CHANGE_MAP,
        sysex_map:dict[int, str] = DEFAULT_SYSEX_MAP,
        **kwargs) -> None:

        super().__init__(voices, keyboard, **kwargs)

        self.sysex_id = sysex_id
        self.crash_mode = crash_mode
        self.spin = spin
        self.control_change_map = control_change_map
        self.sysex_map = sysex_map


        self._available_voices:list[DriveVoice] = list(voices)
        self._active_incoming_voices:dict[int, DriveVoice] = {}
        self._active_keyboard_voices:dict[int, DriveVoice] = {}

        self._output:list[Message] = []


    def update(self, messages: list[Message]) -> list[Message]:
        #get keyboard messages if any, then parse them
        key_msgs = self.keyboard_messages()
        for msg in key_msgs: self.parse(msg, source='keyboard')
        
        #Now process all the messages from the message parameter
        for msg in messages: self.parse(msg,source='incoming')

        #Makes sounds
        self._sound_drives()

        #Ready the output
        output_buffer:list[Message] = []        
        match self.output_mode:
            case OutputModes.OFF:
                #output buffer is already empty
                pass
            case OutputModes.ROLLOVER:
                output_buffer = self._output
            case OutputModes.KEYS:
                output_buffer = key_msgs
            case _: pass
        
        #clear the the output
        self._output = []
        #Return the output
        return output_buffer

    def _sound_drives(self):
        #TODO this
        #TODO handle mute behavior
        pass

    def silence(self) -> None:
        super().silence()
        #TODO: clear active, and restore available stacks
        return 
    
    def _map_attr(self, attr_name:str, value=None):
        attr = self.__getattribute__(attr_name)
        if callable(attr):
            attr()
        else:
            self.__setattr__(attr_name, value)


    ##----------------Overrides from MIDIListener------------------------------#
    def note_on(self, msg: Message, source):
        active_stack = self._active_incoming_voices

        if source == 'keyboard': active_stack = self._active_keyboard_voices

        try:
            #get an available voice and remove it from the pool
            nextVoice:DriveVoice = self._available_voices.pop()

            #Modify the note to match the incoming message
            nextVoice.note = msg.note

            #add the note to the active voice, so that it will be played
            active_stack[msg.note] = nextVoice

            self.logger.debug(
                f"Added note: {msg.note} to '{source}' stack "
                f'[address:{nextVoice.address}]')

        except IndexError as ie: #There are no available voices. 
            self.logger.debug(
                f"Could not add note: {msg.note} to '{source}' stack, "
                'no available voices - rolled')
            #We can't play it so pass it along
            self._output.append(msg)
   
    def note_off(self, msg: Message, source):
        active_stack = self._active_incoming_voices

        if source == 'keyboard': active_stack = self._active_keyboard_voices

        try:
            #get the active Voice
            playedVoice:DriveVoice = active_stack.pop(msg.note)

            #stop the note playing
            playedVoice.update(make_noise=False) #TODO what if this throws an error?
            self.logger.debug(
                f"Removed note: {msg.note} from '{source}' stack "
                f'[address:{playedVoice.address}]')          

            #add the drive back to the available voice pool
            self._available_voices.append(playedVoice)

        except KeyError as ke:
            self.logger.debug(
                f"Could not remove note: {msg.note} from '{source}' stack, "
                f"it's not playing [rolled?]") 
            #if we're not playing that note pass it along
            self._output.append(msg)
        

    def control_change(self, msg: Message, source):
        if msg.control in self.control_change_map.keys():
            attr_name = self.control_change_map[msg.control]
            self._map_attr(attr_name,msg.value)
        #pass along all control change messages
        self._output.append(msg) 
    
    def pitchwheel(self, msg: Message, source):
        #set the pitch bend value
        self.pitch_bend = msg.pitch
        #pass along all pitchwheel messages
        self._output.append(msg)

    def sysex(self, msg: Message, source):
        #ignore any system messages that don't have 3 data bytes
        if (not (len(msg.data)<3 or len(msg.data)>3)):
            id = msg.data[0]
            command = msg.data[1]
            value = msg.data[2]
            #check that the first byte matches our sysex_id, ignore it otherwise
            if id == self.sysex_id:
                #make sure its a valid command
                if command in self.sysex_map.keys():
                    attr_name = self.sysex_map[command]
                    self._map_attr(attr_name, value)
        #pass along all sysex messages
        self._output.append(msg)
    #------------------Getters/Setters-----------------------------------------#

    @property
    def sysex_id(self) -> int:
        return self._sysex_id

    @sysex_id.setter
    def sysex_id(self, id:int):
        if id<0 or id>127:
            self.logger.info(f'sysex_id not set: {id} is not valid')
            return
        self._sysex_id = id
        self.logger.info(f'sysex_id set: {self.sysex_id}')

    @property
    def crash_mode(self)->DriveVoice.CrashMode:
        return self._crash_mode
    
    @crash_mode.setter
    def crash_mode(self, crash_mode:int) -> None:
        if crash_mode not in DriveVoice.CrashMode.__members__.values():
            self.logger.warning(
                f"crash_mode NOT set: {crash_mode} is not a valid mode")
            return
        self._crash_mode = crash_mode    
        self.logger.info(
            'crash_mode set: '
            f'{DriveVoice.CrashMode._member_names_[crash_mode]}')

    @property
    def spin(self):
        return self._spin

    @spin.setter
    def spin(self, spin:bool):
        self._spin = bool(spin)
        self.logger.info(f'spin set: {self.spin}')

    @property
    def control_change_map(self):
        return self._control_change_map
    
    @control_change_map.setter
    def control_change_map(self, control_change_map:dict[int,str]):
        self._control_change_map = control_change_map

    @property
    def sysex_map(self):
        return self._sysex_map
    
    @sysex_map.setter
    def sysex_map(self, sysex_map:dict[int, str]):
        self._sysex_map = sysex_map    


