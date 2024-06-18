import logging
from mido import Message

from ..midi import MIDIUtil, MIDIListener, MIDIParser
from ..voices.voice import PitchBendRange, ModulationWave, Voice
from ..bus import BusException

class CommandMap(dict):
    """_summary_
        A two-way dict to map command names(str) and command codes(int)
        Shamelessly stolen and modified from:
        https://stackoverflow.com/questions/1456373/two-way-reverse-ma
    """

    def __setitem__(self, key, value):

        #Ensures commands names are str and command codes are int
        if (not isinstance(key, int)) and (not isinstance(key, str)):
            raise ValueError("Keys must be int or str")
        if (not isinstance(value, int)) and (not isinstance(value, str)):
            raise ValueError("values must be int or str")

        # Remove any previous connections with these values
        if key in self:
            del self[key]
        if value in self:
            del self[value]
        dict.__setitem__(self, key, value)
        dict.__setitem__(self, value, key)

    def __delitem__(self, key):
        dict.__delitem__(self, self[key])
        dict.__delitem__(self, key)

    def __len__(self):
        """Returns the number of connections"""
        return dict.__len__(self) // 2
    
    def code(self, command) -> int:
        """_summary_
            Given any command name or command code, return the command
            code(int)
        Args:
            command (str or int): The command name or command code

        Raises:
            ValueError: If the command name or command code was not in the
                CommandMap

        Returns:
            int: The command code
        """
        if command in self:
            value = self[command]
            if isinstance(value, str):
                value = self[value]
            return value
        raise ValueError("command not found")

    def name(self, command) -> str:
        """_summary_
            Given any command name or command code, return the command
            name (str)
        Args:
            command (str or int): The command name or command code

        Raises:
            ValueError: If the command name or command code was not in the
                CommandMap

        Returns:
            str: The command name
        """
        if command in self:
            value = self[command]
            if isinstance(value, int):
                value = self[value]
            return value
        raise ValueError("command not found")

    
    def codes(self) -> list[int]:
        """_summary_
            gets all the command codes
        Returns:
            list[str]: All command codes in this CommandMap
        """
        codes = []
        for item in self:
            if isinstance(item,int):
                codes.append(item)
        return codes    
    
    def names(self) -> list[str]:
        """_summary_
            gets all the command names
        Returns:
            list[str]: All command names in this CommandMap
        """
        names = []
        for item in self:
            if isinstance(item,str):
                names.append(item)
        return names

class Synth(MIDIParser, MIDIListener):

    #warning: type checking: no explicit errors!
    def __init__(
        self, 
        voices:tuple[Voice],
        input_channel:int = 0,
        output_channel:int = 0,
        output_modes = ['off', 'rollover'],
        output_mode:str = 'rollover',
        sysex_id:int = 123,
        pitch_bend_range:PitchBendRange = PitchBendRange.OCTAVE,
        pitch_bend:int = 0,
        modulation_wave:ModulationWave = ModulationWave.SINE,
        modulation: int = 0,
        muted:bool = False,
        control_change_map:CommandMap = None,
        sysex_map:CommandMap = None) -> None:

        #logger goes before super, because super calls self.input_channel which
        # has been overridden
        self.logger = logging.getLogger("Synth") 
        MIDIListener.__init__(self, input_channel)
        MIDIParser.__init__(self, self)
 
        self._voices = voices
        #self.input_chanel = input_channel see above comment
        self.output_channel = output_channel

        self.output_modes = output_modes        
        if output_mode not in self.output_modes:
            raise ValueError("output mode not valid")
        
        self.output_mode = output_mode

        self.sysex_id = sysex_id        
        self.pitch_bend_range = pitch_bend_range
        self.pitch_bend = pitch_bend
        self.modulation_wave = modulation_wave
        self.modulation = modulation
        self.muted = muted

        if control_change_map is None:
            control_change_map = CommandMap()
            control_change_map[1]   = 'modulation'
            control_change_map[76]  = 'pitch_bend_range'
            control_change_map[120] = 'reset'
            control_change_map[123] = 'muted'
        self.control_change_map = control_change_map

        if sysex_map is None:
            sysex_map = CommandMap()
            sysex_map[0] = 'input_channel'
            sysex_map[1] = 'output_channel'
            sysex_map[2] = 'output_mode'
        self.sysex_map = sysex_map

        self._available_voices:list[Voice] = list(self.voices)
        self._active_voices:dict[int, Voice] = {}

        self._output:list[Message] = []
    
    def update(self, messages:list[Message])->list[Message]:
        #process all the messages from the message parameter
        for msg in messages: self._parse(msg,source='update')        
        #make all the sounds
        self._sound()
        #flush and return the output
        return self._flush_output()

    def reset(self) -> None:
        try:        
            for voice in self.voices:
                voice.update(make_noise=False)

            self.logger.info("voices silenced") 

        except BusException as be:
            self.logger.warning("voices failed to silence")         
                    
        self._available_voices.extend(
            list(self._active_voices.values()))        
        self._active_voices = {}

        self.logger.info("stack cleared")
    
    def _sound(self) -> None:
        try:
            for voice in self._active_voices.values():
                voice.pitch_bend(self.pitch_bend, self.pitch_bend_range)
                voice.modulate(self.modulation, self.modulation_wave)
                voice.update((not self._muted))
        except BusException as be:
            self.logger.warning("voices failed to update") 

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

    def _map_attr(self, attr_name:str, value=None) -> None:
        attr = self.__getattribute__(attr_name)
        if callable(attr):
            attr()
        else:
            self.__setattr__(attr_name, value)
    
    def _voice_on(
            self, 
            msg:Message, 
            source:str,
            active_stack:dict[int, Voice]) -> None:
        try:
            #get an available voice and remove it from the pool
            nextVoice:Voice = self._available_voices.pop()

            #Modify the note to match the incoming message
            nextVoice.note = msg.note

            #add the note to the active voice, so that it will be played
            active_stack[msg.note] = nextVoice

            self.logger.debug(
                f'added note: {msg.note} to {source} stack ')

        except IndexError as ie: #There are no available voices. 
            self.logger.debug(
                f'could not add note: {msg.note} to {source} stack, '
                'no available voices - rolled')
            #We can't play it so pass it along
            self._output.append(msg)
    
    def _voice_off(
            self,
            msg:Message,
            source:str, 
            active_stack:dict[int, Voice]) -> None:
        try:
            #get the active Voice
            playedVoice:Voice = active_stack.pop(msg.note)

            #stop the note playing
            playedVoice.update(make_noise=False)
            self.logger.debug(
                f'removed note: {msg.note} from {source} stack ')          

            #add the drive back to the available voice pool
            self._available_voices.append(playedVoice)

        except KeyError as ke:
            self.logger.debug(
                f'could not remove note: {msg.note} from {source} stack, '
                f"it's not playing [rolled?]") 
            #if we're not playing that note pass it along
            self._output.append(msg)
        except BusException as be:
            self.logger.warning(
                f'could not remove note: {msg.note} from {source} stack, '
                'there was was a problem silencing the voice') 
    
    #-------------------Overridden from MIDIListener---------------------------#

    def _note_on(self, msg: Message, source) -> None:
        self._voice_on(msg, source, self._active_voices)
   
    def _note_off(self, msg: Message, source) -> None:
        self._voice_off(msg, source, self._active_voices)

    def _control_change(self, msg: Message, source) -> None:
        if msg.control in self.control_change_map:
            attr_name = self.control_change_map[msg.control]
            self._map_attr(attr_name,msg.value)
        #pass along all control change messages
        self._output.append(msg) 
    
    def _pitchwheel(self, msg: Message, source) -> None:
        #set the pitch bend value
        self.pitch_bend = msg.pitch
        #pass along all pitchwheel messages
        self._output.append(msg)

    def _sysex(self, msg: Message, source) -> None:
        #ignore any system messages that don't have 3 data bytes
        if (not (len(msg.data)<3 or len(msg.data)>3)):
            id = msg.data[0]
            command = msg.data[1]
            value = msg.data[2]
            #check that the first byte matches our sysex_id, ignore it otherwise
            if id == self.sysex_id:
                #make sure its a valid command
                if command in self.sysex_map:
                    attr_name = self.sysex_map[command]
                    self._map_attr(attr_name, value)
        #pass along all sysex messages
        self._output.append(msg)

    #--------------------Properties--------------------------------------------#

    @property
    def voices(self) -> tuple[Voice]:
        return self._voices
    
    # CAN NOT change voices after instantiation - it causes so many problems
    # @voices.setter
    # def voices(self, voices:tuple[Voice]) -> None:
    #     self._voices = voices

    #@property for input channel in parent class MidiListener

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
            #which is ok because strs can only be used programmatically.
            output_mode = self.output_modes.index(output_mode)

        if output_mode <0 or output_mode > len(self.output_modes)-1:
            self.logger.warning(
                f"output_mode NOT set: {output_mode} is not a valid mode")
            return
        
        self._output_mode = output_mode
        self.logger.info(
            f'output_mode set: {self.output_modes[self.output_mode]}')

    @property
    def sysex_id(self) -> int:
        return self._sysex_id

    @sysex_id.setter
    def sysex_id(self, id:int) -> None:
        if id<0 or id>127:
            self.logger.info(f'sysex_id not set: {id} is not valid')
            return
        self._sysex_id = id
        self.logger.info(f'sysex_id set: {self.sysex_id}')

    @property
    def pitch_bend_range (self) -> PitchBendRange:
        return self._pitch_bend_range
    
    @pitch_bend_range.setter
    def pitch_bend_range(self, pitch_bend_range) -> None:
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
    def modulation(self) -> int:
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
    def muted(self) -> bool:
        return self._muted
    
    @muted.setter
    def muted(self, muted:bool) -> None:
        self._muted = bool(muted)
        self.logger.info(f'muted set: {self.muted}')
