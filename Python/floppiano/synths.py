from mido import Message
import logging
import time
from enum import IntEnum
import math


from .bus import BusException
from .midi import MIDIListener, MIDIParser, MIDIUtil
from .devices import CrashMode, Keyboard
from .voices import PitchBendRange, ModulationWave, Voice, DriveVoice


class OutputModes(IntEnum):
    __order__ = 'OFF ROLLOVER KEYS'    
    OFF = 0
    ROLLOVER = 1
    KEYS = 2


class Synth(MIDIParser, MIDIListener):

    #warning: type checking: no explicit errors!
    def __init__(self, voices:tuple[Voice]) -> None:
        MIDIListener.__init__(self)
        MIDIParser.__init__(self, self)

        self.logger = logging.getLogger(__name__)
 
        self._voices = voices

        self.pitch = 0
        self.pitch_bend_range = PitchBendRange.OCTAVE

        self.modulation = 0
        self.modulation_wave = ModulationWave.SINE

        self.input_chanel = 0
        self.output_channel = 0
        self.output_mode = OutputModes.ROLLOVER

    
    def play(self, messages:list[Message])->list[Message]:
        pass

    def silence(self):
        for voice in self.voices:
            voice.silence()
    
    @property
    def voices(self) -> tuple[Voice]:
        return self._voices
    
    # #TODO: Handle what happens when instruments change!
    # CAN NOT CHANGE VOICES After instantiation
    # @voices.setter
    # def voices(self, voices:tuple[Voice]) -> None:
    #     self._voices = voices

    @property
    def pitch_bend(self) -> int:
        return self._pitch
    
    @pitch_bend.setter
    def pitch_bend(self, pitch_bend:int) -> None:
        if (pitch_bend < Voice._MIN_PITCH_BEND or 
            pitch_bend > Voice._MAX_PITCH_BEND):
            self.logger.debug(f'Pitch bend NOT set: {pitch_bend} not valid')
            return
        self._pitch_bend = pitch_bend
        self.logger.debug(f'Pitch bend set: {self.pitch}')
    
    @property
    def pitch_bend_range (self) -> PitchBendRange:
        return self._pitch_bend_range
    
    @pitch_bend_range.setter
    def pitch_bend_range(self, pitch_bend_range:int):
        if pitch_bend_range<0 or pitch_bend_range>len(PitchBendRange):
            self.logger.warning(
                f"Pitch Bend Mode NOT set: {pitch_bend_range} not valid")
            return

        self._pitch_bend_range = list(
            PitchBendRange.__members__.values())[pitch_bend_range]

        self.logger.info(f'Pitch Bend Range set: {self.pitch_bend_range}')
 
    @property
    def modulation(self) ->int:
        return self._modulation
    
    @modulation.setter
    def modulation(self, modulation:int) -> None:
        if (modulation < Voice._MIN_MODULATE or 
            modulation > Voice._MAX_MODULATE):
            self.logger.debug(
                f"Modulation NOT set: {modulation} not valid")
            return

        self._modulation = modulation
        self.logger.debug(f"Modulation set: {modulation}")

    @property
    def modulation_wave(self) -> ModulationWave:
        return self._modulation_wave

    @modulation_wave.setter
    def modulation_wave(self, modulation_wave:int) -> None:
        if modulation_wave not in ModulationWave.__members__.values():
            self.logger.warning(
                f"Modulation Wave NOT set: {modulation_wave} is not valid")
            return
        self._modulation_wave = modulation_wave
        self.logger.info(f'Modulation Wave set: {self.modulation_wave}')


    #@property for input channel in super class MidiListener

    @MIDIListener.input_chanel.setter
    def input_chanel(self, channel:int) -> None:
        #Overridden super() setter because we don't want exceptions for bad
        #channel parameters
        if channel<0 or channel >15:
            self.logger.warning(
                f"Input channel NOT set: {channel} is not a valid channel")
            return
        self._input_channel = channel
        self.logger.info(
            f'Input channel set: {self.input_chanel} [change on update()]')

    @property
    def output_channel(self) -> int:
        return self._output_channel
    
    @output_channel.setter
    def output_channel(self, channel:int) -> None:
        if channel<0 or channel >15:
            self.logger.warning(
                f"Output channel NOT set: {channel} is not a valid channel")
            return
        self._output_channel = channel
        self.logger.info(
            f'Output channel set: {self.output_channel} [change on update()]')
    
    @property
    def output_mode(self) -> OutputModes:
        return self._output_mode
    
    @output_mode.setter
    def output_mode(self, output_mode:int) -> None:
        if output_mode not in OutputModes.__members__.values():
            self.logger.warning(
                f"Output mode NOT set: {output_mode} is not a valid mode")
            return
        self._output_mode = output_mode
        self.logger.info(f'Output mode set: {self.output_mode}')


class KeyboardSynth(Synth):

    def __init__(self, voices: tuple[Voice], keyboard:Keyboard = None) -> None:
        super().__init__(voices)

        self.do_keyboard = True
        self.loopback = True
        self.keyboard = keyboard

    def keyboard_messages(self) ->list[Message]:
        if self.do_keyboard:
            try:  
                messages = self.keyboard.read()
            except BusException as be:
                #This is normal just log it
                self.logger.debug("Error reading keyboard state - skipping")
                #clear the messages
                messages = []
            finally:
                return messages

        return []

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
        self.logger.info(f'Loopback set: {self.loopback} [change on update()]')
    
    @property
    def keyboard(self) -> Keyboard:
        return self._keyboard
    
    @keyboard.setter
    def keyboard(self, keyboard:Keyboard) -> None:
        self._keyboard = keyboard
        if self.keyboard is None:
            #We don't have a keyboard so don't attempt to r/w its states
            self.do_keyboard = False

class DriveSynth(KeyboardSynth):

    def __init__(self, voices: tuple[DriveVoice], keyboard: Keyboard = None) -> None:
        super().__init__(voices, keyboard)

        self.crash_mode = CrashMode.FLIP

        self._available_drives:list[DriveSynth] = list(voices)
        self._active_drives:list[DriveSynth] = []

        self._output:list[Message] = []


    def play(self, messages: list[Message]) -> list[Message]:

        #get keyboard messages if any.
        key_msgs = self.keyboard_messages()
        messages.extend(key_msgs)
        
        #parse all the messages
        for msg in messages: self.parse(msg)

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

        return output_buffer

    def _sound_drives(self):
        #TODO this
        pass

    def silence(self) -> None:
        super().silence()
        #TODO: clear active, and restore available stacks
        return 

    def _add_to_output(self, message:Message) -> list[Message]:
        if MIDIParser.has_channel(message):
            message.channel = self.output_channel
        self._output.append(message)    


    @property
    def crash_mode(self)->CrashMode:
        return self._crash_mode
    
    @crash_mode.setter
    def crash_mode(self, crash_mode:int) -> None:
        if crash_mode not in CrashMode.__members__.values():
            self.logger.warning(
                f"Crash mode NOT set: {crash_mode} is not a valid mode")
            return
        self._crash_mode = crash_mode    
        self.logger.info(f'Crash mode set: {self.crash_mode}')
    
    ##----------------Overrides from MIDIListener------------------------------#
    #TODO: Below
    def note_on(self, msg: Message):
        return
    def note_off(self, msg: Message):
        return
    def control_change(self, msg: Message):
        return
    def pitchwheel(self, msg: Message):
        return
    def sysex(self, msg: Message):
        return
    
        
