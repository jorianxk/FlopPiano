from enum import IntEnum
import logging

from mido import Message

from ..midi import MIDIUtil, MIDIListener, MIDIParser
from ..voices.voice import PitchBendRange, ModulationWave, Voice


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
        sysex_id:int = 123,
        pitch_bend_range:PitchBendRange = PitchBendRange.OCTAVE,
        pitch_bend:int = 0,
        modulation_wave:ModulationWave = ModulationWave.SINE,
        modulation: int = 0,
        muted:bool = False,) -> None:

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
    
    def update(self, messages:list[Message])->list[Message]:
        pass

    def reset(self):
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
        if not MIDIUtil.isValidMIDIChannel(channel):
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
        if not MIDIUtil.isValidMIDIChannel(channel):
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
