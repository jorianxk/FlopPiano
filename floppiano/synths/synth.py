import logging
from abc import ABC, abstractmethod
from typing import Any, Callable
from mido import Message
from floppiano.midi import MIDIUtil, MIDIListener, MIDIParser

# Constants for Synths #
OUTPUT_MODES = ['off', 'rollover']

PITCH_BEND_RANGES = {
    #Number indicates steps. 1/2 steps = 1 note
    'half':0.5,     #  1 note(s) or   1/2 step(s)
    'whole':1,      #  2 note(s) or     1 step(s)
    'minor3rd':1.5, #  3 note(s) or 1 1/2 step(s) 
    'major3rd':2,   #  4 note(s) or     2 step(s)
    'fourth':2.5,   #  5 note(s) or 2 1/2 step(s)
    'fifth':3.5,    #  7 note(s) or 3 1/2 step(s)
    'octave':6      # 12 note(s) or     6 step(s)
    }

MODULATION_WAVES = ['sine', 'square', 'saw', 'triangle']

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

class Synth(MIDIParser, MIDIListener, ABC):
    """
        An abstract MIDI Synthesizer. Parses MIDI messages and sets the
        Synth's attributes accordingly. Relies on inheritance for sounding
        implementation. 
    """

    def __init__(
        self,
        input_channel:int = 0,
        output_channel:int = 0,
        output_mode:str = 'rollover',
        sysex_id:int = 123,
        pitch_bend_range:str = 'octave',
        pitch_bend:int = 0,
        modulation_wave:str = 'sine',
        modulation_rate:int = 1,
        modulation: int = 0,
        muted:bool = False,
        polyphonic:bool = True,
        poly_voices:int = 0, 
        control_change_map:CommandMap = None,
        sysex_map:CommandMap = None) -> None:

        """
            Creates a Synth with initial specified properties attributes. 
        Args:
            input_channel (int, optional): The MIDI Channel which the Synth
                is should listen to. Defaults to 0.
            output_channel (int, optional): The MIDI CHannel in which outgoing 
                Synth Messages should be sent on. Defaults to 0.
            output_mode (str, optional): The output mode for the Synth. 
                Must be a member of OUTPUT_MODES. Defaults to 'rollover'.
            sysex_id (int, optional): A unique ID in the range [0-127]. to
                distinguish the Synth from other Synths during MIDI sysex 
                messages. Defaults to 123.
            pitch_bend_range (str, optional): Must be a member of 
                PITCH_BEND_RANGES. Sets the pitch bend wheel's range.
                Defaults to 'octave'.
            pitch_bend (int, optional): The amount of pitch bend the synth
             has on start up.  Defaults to 0.
            modulation_wave (str, optional): The modulation wave type of the 
                Synth. Defaults to 'sine'.
            modulation_rate (int, optional): The modulation attack or 
                rate in Hz. Defaults to 1.
            modulation (int, optional): The initial modulation value of the 
                Synth on startup. Defaults to 0.
            muted (bool, optional): The initial mute state of the Synth. 
                Defaults to False (un-muted).
            polyphonic (bool, optional): The inital polyphony state of the
                Synth. Defaults to True.
            poly_voices (int, optional): The number of voices to use when 
                polyphonic. Defaults to 0 (Max).
            control_change_map (CommandMap, optional): The two-way map that is 
                used to map MIDI Control Changes to Synth properties. 
                Defaults to None (Default Map).
            sysex_map (CommandMap, optional): The two-way map that is used to 
                map MIDI sysex messages to Synth properties. Defaults to None.
                (Default Map)
        """


        #Set up this before so that inherited properties work with observers        
        self._attr_observers:dict[str, list[callable]] = {}
        self.logger = logging.getLogger(__name__) 

        MIDIListener.__init__(self, input_channel)
        MIDIParser.__init__(self, self)       
 
        # System attributes #
        #self.input_channel = input_channel inherited from MidiListener
        self.output_channel = output_channel
        self.output_mode = output_mode  
        self.sysex_id = sysex_id   

        # Sound behavior attributes #
        self.pitch_bend_range = pitch_bend_range        
        self.pitch_bend = pitch_bend
        self.modulation_wave = modulation_wave
        self.modulation_rate = modulation_rate
        self.modulation = modulation
        self.muted = muted # no getter/setter needed (bool)

        # Polyphony attributes #
        # private set via mono_mode() and poly_mode()
        self._polyphonic:bool = polyphonic 
        # private set via mono_mode()
        self._mono_voices:int = 0
        # public because this is not supported via MIDI control change 127 
        # i.e. it's custom       
        self.poly_voices = poly_voices

        # MIDI message attribute mappings #
        #See https://nickfever.com/music/midi-cc-list for details
        if sysex_map is None:
            sysex_map = CommandMap()
            sysex_map[0] = 'input_channel'  # Custom
            sysex_map[1] = 'output_channel' # Custom
            sysex_map[2] = 'output_mode'    # Custom
        self.sysex_map = sysex_map

        if control_change_map is None:
            control_change_map = CommandMap()
            control_change_map[1]   = 'modulation'       # Standard MIDI
            control_change_map[16]  = 'pitch_bend_range' # Custom
            control_change_map[17]  = 'modulation_wave'  # Custom
            control_change_map[18]  = 'modulation_rate'  # Custom
            control_change_map[19]  = 'poly_voices'      # Custom
            control_change_map[120] = 'mute'             # Standard MIDI
            control_change_map[121] = 'reset'            # Standard MIDI
            control_change_map[126] = 'mono_mode'        # Standard MIDI
            control_change_map[127] = 'poly_mode'        # Standard MIDI
        self.control_change_map = control_change_map

        # A list of messages that should be output on parse()
        self._output:list[Message] = []
    
    #--------------------------Force Inherit-----------------------------------#

    @abstractmethod
    def note_on(self, note:int, velocity:int, source) -> bool:
        return False

    @abstractmethod
    def note_off(self, note:int, velocity:int, source) -> bool:
        return False
    
    #--------------------------Public Functions--------------------------------#
    
    def reset(self) -> None:
        """
        Forces the synth to be un-muted
        """
        #On a reset all things should be set back to default. In MIDI there is 
        # no 'unmute'. On reset make sure the Synth is not muted
        self.muted = False

    def mute(self) -> None:
        """
        Mutes the synth
        """
        self.muted = True

    def mono_mode(self, mono_voices:int=0) -> None:
        """
            Puts the synth into monophonic mode using a number of voices equal
            to mono_voices
        Args:
            mono_voices (int, optional): The number of voices to use 
                when monophonic. Defaults to 0.

        Raises:
            ValueError: If mono_voices is not in the range [0,127]
        """
        if mono_voices<0 or mono_voices>127:
            raise ValueError('mono_voices must be [0,127]')
        # disable polyphony (make monophonic)
        self._polyphonic = False  
        self._mono_voices = mono_voices
    
    def poly_mode(self) -> None:
        """
            Puts the synth in polyphonic mode using a number of voices equal 
            to Synth.poly_voices. 
        """
        # enable polyphony (make polyphonic)
        self._polyphonic = True 

    def parse(self, messages:list[Message], source = None) -> list[Message]:
        """
            Forces the synth to consume then act on the specified MIDI. returns
            the resultant MIDI depending on the Synth's output mode.
        Args:
            messages (list[Message]): The MIDI messages to parse
            source (_type_, optional): The source of the MIDI messages
                Defaults to None.

        Returns:
            list[Message]: A list of MIDI messages that occurred or should be
            passed on as a result of the Synth processing the messages in the 
            message parameter. For example, notes that could not be played, 
            sysex messages, etc. If the Synths output_mode is 'off' the 
            list returned will be empty.
        """
        # process all the messages from the messages
        for msg in messages: MIDIParser.parse(self, msg, source)        
        # Flush the output and return any rolled over messages
        return self._flush_output()
    
    def attach_observer(self, attr_name:str, observer:Callable) -> None:
        """
            Attaches the specified callback to the specified property of the
            Synth. When the specified property is changed, the specified 
            callable will be invoked. The callable should expect a single 
            of attr_name's type which will be the new set value of the attribute
        Args:
            attr_name (str): The name of the Synth's attribute to attach an 
                observer to.
            observer (Callable): A callback function to receive the new 
                attribute value whn the attribute changes.
        """
        if attr_name in self._attr_observers.keys():
            # Already in the dict. Add a the observer to the list
            self._attr_observers[attr_name].append(observer)
        else:
            # Instantiate the list of observers for the attribute
            self._attr_observers[attr_name] = [observer]
    
    def detach_observer(self, attr_name:str, observer:Callable) -> None:
        """
            Removes an already attached attribute observer. 
        Args:
            attr_name (str): The name of the attribute in which the observer
                is attached
            observer (Callable): The observer that should be removed from the
                attribute's observers
        """
        # Remove the observer for the the attribute
        self._attr_observers[attr_name].remove(observer)
   
    #-------------------------Private Functions--------------------------------#

    def _flush_output(self) -> list[Message]:
        #Preps the output of the synth
        # Ready the outputs
        output_buffer:list[Message] = [] 
        if self.output_mode == OUTPUT_MODES.index('off'):
            # output buffer is already empty, nothing to do
            pass
        elif self.output_mode == OUTPUT_MODES.index('rollover'): 
            output_buffer = self._output.copy()
        else:
            # A new output mode has probably been added. So don't do anything
            pass            
        # clear the the output, so it can be reused
        self._output = []
        # ensure all outgoing messages are on self.output_channel
        for msg in output_buffer:
            if MIDIUtil.hasChannel(msg):
                msg.channel = self.output_channel
        # return the output buffer as the output
        return output_buffer

    def __setattr__(self, name:str, value:Any) -> None:
        # Overridden to invoke any attached attribute observers on
        # a successful attribute change.
        # Set the attribute
        object.__setattr__(self, name,value)
        #If an observer exists for the attribute, then call it
        if name in self._attr_observers.keys(): 
            for observer in self._attr_observers[name]:
                observer(value)

    def _map_attr(self, attr_name:str, value:Any = None) -> None:
        """
            Sets/Calls a Synth attribute by it's (str) name with parameter
            value. Used to map MIDI messages to functional changes in the 
            Synth. 
        Args:
            attr_name (str): The attribute to be invoked/set
            value (Any, optional): The value or parameter to set/call the 
                attribute with/to. Defaults to None.
        """
        try:
            attr = self.__getattribute__(attr_name)
            # Setting a property or calling a function?
            if callable(attr):
                try: #if the function takes an argument pass it 
                    attr(value)
                    self.logger.info(f'{attr_name}({value}): success')
                except TypeError: #if the function does not take an argument
                    attr()
                    self.logger.info(f'{attr_name}(): success')
            else:
                # set the property
                self.__setattr__(attr_name, value)
                # pitch bend and modulation happen frequently so they need to 
                # be logged at the debug and not info level
                level = logging.INFO
                if attr_name =='pitch_bend' or attr_name =='modulation':
                    level = logging.DEBUG
                
                self.logger.log(level,f'{attr_name} set to: {value}')
        except ValueError as ve:
            self.logger.warning(f'Bad value while mapping {attr_name}: {ve}')
        except Exception as e:
            self.logger.error(f'Error while mapping {attr_name}: {e}')    

    #------------Overridden from MIDIListener MIDI Handling--------------------#
    # Below methods/ functions are invoked on a Synth.parse() call via the
    # super classes MIDIListener and MIDIParser

    def on_note_on(self, msg: Message, source) -> None:
        # If the note_on function did not handle the message, pass the message
        # along to the output
        if not (self.note_on(msg.note, msg.velocity, source)):
            self._output.append(msg)
   
    def on_note_off(self, msg: Message, source) -> None:
        # If the note_on function did not handle the message, pass the message
        # along to the output
        if not (self.note_off(msg.note, msg.velocity, source)):
            self._output.append(msg)

    def on_control_change(self, msg: Message, source) -> None:
        if msg.control in self.control_change_map:
            attr_name = self.control_change_map[msg.control]
            self._map_attr(attr_name, msg.value)
        # pass along all control change messages
        self._output.append(msg) 
    
    def on_pitchwheel(self, msg: Message, source) -> None:
        # set the pitch bend value
        self._map_attr('pitch_bend', msg.pitch) 
        # pass along all pitchwheel messages
        self._output.append(msg)

    def on_sysex(self, msg: Message, source) -> None:
        # ignore any system messages that don't have 3 data bytes
        if (not (len(msg.data)<3 or len(msg.data)>3)):
            id = msg.data[0]
            command = msg.data[1]
            value = msg.data[2]
            # check that the first byte matches our sysex_id, 
            # ignore it otherwise
            if id == self.sysex_id:
                # make sure its a valid command
                if command in self.sysex_map:
                    attr_name = self.sysex_map[command]
                    self._map_attr(attr_name, value)
        # pass along all sysex messages
        self._output.append(msg)

    #------------------------------Properties----------------------------------#

    @property
    def output_channel(self) -> int:
        return self._output_channel
    
    @output_channel.setter
    def output_channel(self, channel:int) -> None:
        if not MIDIUtil.isValidChannel(channel):
            raise ValueError("Channel must be [0-15]")
        self._output_channel = channel
    
    @property
    def output_mode(self) -> int:
        return self._output_mode
    
    @output_mode.setter
    def output_mode(self, output_mode) -> None:
        if isinstance(output_mode, str):
            # this will throw an exception if output mode is not in OUTPUT_MODES
            # which is ok because strs can only be used programmatically.
            output_mode = OUTPUT_MODES.index(output_mode)

        if output_mode <0 or output_mode > len(OUTPUT_MODES)-1:
            raise ValueError('Not a valid mode')
   
        self._output_mode = output_mode

    @property
    def sysex_id(self) -> int:
        return self._sysex_id

    @sysex_id.setter
    def sysex_id(self, id:int) -> None:
        if id<0 or id>127:
            raise ValueError('sysex_id must be [0-127]')
        self._sysex_id = id

    @property
    def pitch_bend_range (self) -> int:
        return self._pitch_bend_range
    
    @pitch_bend_range.setter
    def pitch_bend_range(self, pitch_bend_range) -> None:
        range_names = list(PITCH_BEND_RANGES.keys())
        if isinstance(pitch_bend_range, str):
            # this will throw an exception if pitch_bend_range mode is not 
            # in range_names which is ok because strs can only be used 
            # programmatically.
            pitch_bend_range = range_names.index(pitch_bend_range)

        if pitch_bend_range< 0 or pitch_bend_range > len(range_names)-1:
            raise ValueError('Not a not valid pitch bend range')

        self._pitch_bend_range = pitch_bend_range

    @property
    def pitch_bend(self) -> int:
        return self._pitch_bend
    
    @pitch_bend.setter
    def pitch_bend(self, pitch_bend:int) -> None:
        if not MIDIUtil.isValidPitch(pitch_bend):
            raise ValueError('Not a valid pitch bend')           
        self._pitch_bend = pitch_bend
    
    @property
    def modulation_wave(self) -> int:
        return self._modulation_wave

    @modulation_wave.setter
    def modulation_wave(self, modulation_wave) -> None:
        if isinstance(modulation_wave, str):
            # this will throw an exception if modulation_wave is not in 
            # MODULATION_WAVES which is ok because strs can only be 
            # used programmatically.
            modulation_wave = MODULATION_WAVES.index(modulation_wave)

        if modulation_wave <0 or modulation_wave > len(MODULATION_WAVES)-1:
            raise ValueError('Not a modulation wave')

        self._modulation_wave = modulation_wave
    
    @property
    def modulation_rate(self) -> int:
        return self._modulation_rate
    
    @modulation_rate.setter
    def modulation_rate(self, modulation_rate:int) -> None:
        if modulation_rate<0 or modulation_rate>127:
            raise ValueError("modulation_rate must be [0-127]")
        self._modulation_rate = modulation_rate

    @property
    def modulation(self) -> int:
        return self._modulation
    
    @modulation.setter
    def modulation(self, modulation:int) -> None:
        if not MIDIUtil.isValidModulation(modulation):
            raise ValueError('Not a not valid modulation')         
        self._modulation = modulation

    @property
    def polyphonic(self) -> bool:
        # no setter because polyphonic should be set via 
        # mono_mode() and poly_mode()
        return self._polyphonic

    @property
    def mono_voices(self) -> int:
        # no setter because mono voices should be set via mono_mode()
        return self._mono_voices
    
    @property
    def poly_voices(self) -> int:
        return self._poly_voices
    
    @poly_voices.setter
    def poly_voices(self, poly_voices:int) -> int:
        if poly_voices <0 or poly_voices>127:
            raise ValueError("poly_voices must be [0,127]")
        self._poly_voices = poly_voices
