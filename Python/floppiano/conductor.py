from mido import Message
import logging
import time
from enum import IntEnum
import math


from .midi import MIDIListener, MIDIParser, MIDIUtil
from .devices import CrashMode, Keyboard
from .instruments import PitchBendRange, ModulationWave, Instrument

class OutputModes(IntEnum):
    __order__ = 'OFF ROLLOVER KEYS'    
    OFF = 0
    ROLLOVER = 1
    KEYS = 2



from mido import Message

class Conductor(MIDIParser, MIDIListener):

    #warning: type checking: no explicit errors!
    def __init__(self,
        instruments:tuple[Instrument],
        keyboard:Keyboard = None) -> None:

        MIDIListener.__init__(self)
        MIDIParser.__init__(self, self)

        self.logger = logging.getLogger(__name__)
 
        self.instruments = instruments

        self.pitch = 0
        self.pitch_bend_range = PitchBendRange.OCTAVE

        self.modulation = 0
        self.modulation_wave = ModulationWave.SINE

        self.do_keyboard = True
        self.loopback = True
        self.keyboard = keyboard


        self.input_chanel = 0
        self.output_channel = 0
        self.output_mode = OutputModes.ROLLOVER

    
    def conduct(self, messages:list[Message])->list[Message]:
        pass

    def silence(self):
        pass

    
    @property
    def instruments(self) -> tuple[Instrument]:
        return self._instruments
    
    #TODO: Handle what happens when instruments change!
    @instruments.setter
    def instruments(self, instruments:tuple[Instrument]) -> None:
        self._instruments = instruments

    @property
    def pitch_bend(self) -> int:
        return self._pitch
    
    @pitch_bend.setter
    def pitch_bend(self, pitch_bend:int) -> None:
        if (pitch_bend < Instrument._MIN_PITCH_BEND or 
            pitch_bend > Instrument._MAX_PITCH_BEND):
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
        if (modulation < Instrument._MIN_MODULATE or 
            modulation > Instrument._MAX_MODULATE):
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
        self.logger.info(f'Loopback set: {self.loopback} [change on conduct()]')
    
    @property
    def keyboard(self) -> Keyboard:
        return self._keyboard
    
    @keyboard.setter
    def keyboard(self, keyboard:Keyboard) -> None:
        self._keyboard = keyboard
        if self.keyboard is None:
            #We don't have a keyboard so don't attempt to r/w its states
            self.do_keyboard = False

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
        self.logger.info(f'Input channel set: {self.input_chanel}')

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
        self.logger.info(f'Output channel set: {self.output_channel}')
    
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
        
   

