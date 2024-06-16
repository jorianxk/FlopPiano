from mido import Message


from .synth import OutputModes
from .keyboard_synth import KeyboardSynth
from ..voices import DriveVoice

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
        crash_mode:DriveVoice.CrashMode = DriveVoice.CrashMode.FLIP,
        spin:bool = False,        
        control_change_map:dict[int, str] = DEFAULT_CONTROL_CHANGE_MAP,
        sysex_map:dict[int, str] = DEFAULT_SYSEX_MAP,
        **kwargs) -> None:

        super().__init__(voices, **kwargs)

 
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
        all_active_voices = list(self._active_incoming_voices.values())
        all_active_voices.extend(list(self._active_keyboard_voices.values()))
        for voice in all_active_voices:
            voice.pitch_bend(self.pitch_bend, self.pitch_bend_range)
            voice.modulate(self.modulation, self.modulation_wave)
            voice.update((not self._muted))

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


    def reset(self) -> None:
        #silence all voices using super().reset()
        super().reset()
        
        #Add the active incoming DriveVoices back to the available voices stack
        self._available_voices.extend(
            list(self._active_incoming_voices.values()))
        #Clear the active incoming DriveVoices Stack
        self._active_incoming_voices = {}

        #Add the active keyboard DriveVoices back to the available voices stack
        self._available_voices.extend(
            list(self._active_keyboard_voices.values()))        
        #Clear the active keyboard DriveVoices Stack
        self._active_keyboard_voices = {}
        
    
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
                f"added note: {msg.note} to '{source}' stack "
                f'[address:{nextVoice.address}]')

        except IndexError as ie: #There are no available voices. 
            self.logger.debug(
                f"could not add note: {msg.note} to '{source}' stack, "
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
                f"removed note: {msg.note} from '{source}' stack "
                f'[address:{playedVoice.address}]')          

            #add the drive back to the available voice pool
            self._available_voices.append(playedVoice)

        except KeyError as ke:
            self.logger.debug(
                f"could not remove note: {msg.note} from '{source}' stack, "
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
