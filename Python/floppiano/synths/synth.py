from enum import IntEnum
import logging

from mido import Message

from ..midi import MIDIUtil, MIDIListener, MIDIParser
from ..voices.voice import PitchBendRange, ModulationWave, Voice
from ..bus import BusException


class Synth(MIDIParser, MIDIListener):

    DEFAULT_CONTROL_CHANGE_MAP ={
        1  : 'modulation',
        76 : 'pitch_bend_range',
        120: 'reset',
        123: 'muted'
    }

    DEFAULT_SYSEX_MAP = {
        0: 'input_channel',
        1: 'output_channel',
        2: 'output_mode'
    }

    OUTPUT_MODES = ['off','rollover']

    #warning: type checking: no explicit errors!
    def __init__(
        self, 
        voices:tuple[Voice],
        input_channel:int = 0,
        output_channel:int = 0,
        output_mode:str = 'rollover',
        sysex_id:int = 123,
        pitch_bend_range:PitchBendRange = PitchBendRange.OCTAVE,
        pitch_bend:int = 0,
        modulation_wave:ModulationWave = ModulationWave.SINE,
        modulation: int = 0,
        muted:bool = False,
        control_change_map:dict[int, str] = DEFAULT_CONTROL_CHANGE_MAP,
        sysex_map:dict[int, str] = DEFAULT_SYSEX_MAP) -> None:

        #logger goes before super, because super calls self.input_channel which
        # has been overridden
        self.logger = logging.getLogger(__name__) 
        MIDIListener.__init__(self, input_channel)
        MIDIParser.__init__(self, self)
 
        self._voices = voices

        #self.input_chanel = input_channel

        self.output_channel = output_channel
        self.output_mode = output_mode

        self.sysex_id = sysex_id
        
        self.pitch_bend_range = pitch_bend_range
        self.pitch_bend = pitch_bend

        self.modulation_wave = modulation_wave
        self.modulation = modulation

        self.muted = muted

        self.control_change_map = control_change_map
        self.sysex_map = sysex_map

        self._available_voices:list[Voice] = list(self.voices)
        self._active_voices:dict[int, Voice] = {}

        self._output:list[Message] = []

    
    def update(self, messages:list[Message])->list[Message]:
        #process all the messages from the message parameter
        for msg in messages: self._parse(msg,source='update')
        
        #make all the sounds
        self._sound()


        return self._flush_output()


    def reset(self):
        for voice in self.voices:
            voice.update(make_noise=False)
    
    def _flush_output(self)->list[Message]:
        #Ready the output
        output_buffer:list[Message] = []        
        match self.output_mode:
            case 0: #output mode off
                #output buffer is already empty
                pass
            case 1: #rollover mode
                output_buffer = self._output
            case _:
                #should never happen output mode setter prevents this
                raise ValueError("Can not ready output - invalid output mode")
            
        #clear the the output
        self._output = []       
        return output_buffer
    
    def _sound(self):
        for voice in self._active_voices.values():
            voice.pitch_bend(self.pitch_bend, self.pitch_bend_range)
            voice.modulate(self.modulation, self.modulation_wave)
            voice.update((not self._muted))


    def _map_attr(self, attr_name:str, value=None):
        attr = self.__getattribute__(attr_name)
        if callable(attr):
            attr()
        else:
            self.__setattr__(attr_name, value)

    
    def _voice_on(self, msg:Message, active_stack:dict[int, Voice]):
        try:
            #get an available voice and remove it from the pool
            nextVoice:Voice = self._available_voices.pop()

            #Modify the note to match the incoming message
            nextVoice.note = msg.note

            #add the note to the active voice, so that it will be played
            active_stack[msg.note] = nextVoice

            self.logger.debug(
                f'added note: {msg.note} to active stack '
                f'[address:{nextVoice.address}]')

        except IndexError as ie: #There are no available voices. 
            self.logger.debug(
                f'could not add note: {msg.note} to active stack, '
                'no available voices - rolled')
            #We can't play it so pass it along
            self._output.append(msg)
    
    def _voice_off(self, msg:Message, active_stack:dict[int, Voice]):
        try:
            #get the active Voice
            playedVoice:Voice = active_stack.pop(msg.note)

            #stop the note playing
            playedVoice.update(make_noise=False)
            self.logger.debug(
                f'removed note: {msg.note} from active stack '
                f'[address:{playedVoice.address}]')          

            #add the drive back to the available voice pool
            self._available_voices.append(playedVoice)

        except KeyError as ke:
            self.logger.debug(
                f'could not remove note: {msg.note} from active stack, '
                f"it's not playing [rolled?]") 
            #if we're not playing that note pass it along
            self._output.append(msg)
        except BusException as be:
            self.logger.warn(
                f'could not remove note: {msg.note} from active stack, '
                'there was was a problem stopping the note from sounding') 
    

    #-------------------Overridden from MIDIListener---------------------------#
    def _note_on(self, msg: Message, source):
        self._voice_on(msg, self._active_voices)

   
    def _note_off(self, msg: Message, source):
        self._voice_off(msg, self._active_voices)


    def _control_change(self, msg: Message, source):
        if msg.control in self.control_change_map.keys():
            attr_name = self.control_change_map[msg.control]
            self._map_attr(attr_name,msg.value)
        #pass along all control change messages
        self._output.append(msg) 
    
    def _pitchwheel(self, msg: Message, source):
        #set the pitch bend value
        self.pitch_bend = msg.pitch
        #pass along all pitchwheel messages
        self._output.append(msg)

    def _sysex(self, msg: Message, source):
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

    #--------------------Properties--------------------------------------------#

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
        if not MIDIUtil.isValidMIDIChannel(channel):
            self.logger.warning(
                f"input_channel NOT set: {channel} is not a valid channel")
            return
        self._input_channel = channel
        self.logger.info(
            f'input_channel set: {self.input_channel}')

    @property
    def output_channel(self) -> int:
        return self._output_channel
    
    @output_channel.setter
    def output_channel(self, channel:int) -> None:
        if not MIDIUtil.isValidMIDIChannel(channel):
            self.logger.warning(
                f"output_channel NOT set: {channel} is not a valid channel")
            return
        self._output_channel = channel
        self.logger.info(
            f'output_channel set: {self.output_channel}')
    
    @property
    def output_mode(self) -> str:
        return self._output_mode
    
    @output_mode.setter
    def output_mode(self, output_mode) -> None:

        if isinstance(output_mode, str):
            #this will throw an exception if output mode is not in keys()
            #which is ok because strs can only be uses programmatically.
            output_mode = Synth.OUTPUT_MODES.index(output_mode)

        if output_mode <0 or output_mode > len(Synth.OUTPUT_MODES)-1:
            self.logger.warning(
                f"output_mode NOT set: {output_mode} is not a valid mode")
            return
        
        self._output_mode = output_mode
        self.logger.info(
            f'output_mode set: {Synth.OUTPUT_MODES[self.output_mode]}')

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
