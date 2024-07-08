from mido import Message
from .synth import Synth, PITCH_BEND_RANGES
from ..midi import MIDIUtil
from ..devices import Drives

#TODO what about bus errors?

class DriveSynth(Synth):

    def __init__(
        self,
        drive_addresses: list[int],
        bow:bool = False,
        spin:bool = False,   
        **kwargs) -> None:

        super().__init__(**kwargs)
        
        # Add support for crash mode and spin (Custom)
        if 'bow' not in self.control_change_map:
            self.control_change_map['bow'] = 80
        
        if 'spin' not in self.control_change_map:
            self.control_change_map['spin'] = 81

        self.bow = bow
        self.spin = spin


        self._drives = drive_addresses
        self._available = self._drives.copy()
        self._active = []

        # Setup property changed callbacks
        self.attach_observer('bow', self._bow_changed)
        self.attach_observer('spin', self._spin_changed)
        self.attach_observer('modulation_rate', self._modulation_rate_changed)
        self.attach_observer('modulation', self._modulation_changed)
        self.attach_observer('muted', self._muted_changed)
        #self.attach_observer('polyphonic', self._polyphonic_changed)
        self.attach_observer('pitch_bend', self._pitch_bend_changed)



    #-------------------------Inherited from from Synth------------------------#

    def note_on(self, note: int, velocity: int, source) -> bool:
        return super().note_on(note, velocity, source)
    
    def note_off(self, note: int, velocity: int, source) -> bool:
        return super().note_off(note, velocity, source)

    def reset(self) -> None:
        super().reset() # call super to reset mute state/ set defaults

        Drives.enable(0,False)        
        #clear the active stack
        self._active = []
        #reset the available stack
        self._available = self._drives.copy()
        self.logger.info('drive synth reset')

    def _bow_changed(self, bow:bool) -> None:
        print("bow changed:", bow)
        Drives.bow(0, bow)

    def _spin_changed(self, spin:bool) -> None:
        print("spin changed:", spin)
        Drives.spin(0, spin)
    
    def _modulation_rate_changed(self, modulation_rate:int) -> None:
        print("modulation_rate changed:", modulation_rate)
        Drives.modulation_rate(0, modulation_rate)
    
    def _modulation_changed(self, modulation:int) -> None:
        #TODO only 1-16hz sounds good, do we want this hard coded?
        # 0 -> no modulation
        print("modulation changed:", modulation)
        modulation_freq = MIDIUtil.integer_map_range(modulation, 0, 127, 0, 16)                   
        Drives.modulation_frequency(0,modulation_freq)

    def _muted_changed(self, muted:bool) -> None:
        print("muted changed:", muted)
        for item in self._active:
            Drives.enable(item['drive'], not muted)
    
    # def _polyphonic_changed(self, polyphonic:bool) -> None:
    #     #TODO: change polyphony behavior
    #     # if polyphonic != self.polyphonic:
    #     #         self.reset()
    #     print("polyphonic changed:", polyphonic)
    
    def _pitch_bend_changed(self, pitch_bend:int) -> None:
        print("pitch_bend changed:", pitch_bend)
        # We DON'T change the note since the note is the identifier for
        # turning on/off drives. We changed the drives' sounding frequency

        # Loop through the active drives and change their pitch based on the
        # incoming bend
        for item in self._active:

            if pitch_bend == 0:
                # Pitch bend is zero so ensure that each drive is playing 
                # their original note
                Drives.frequency(
                    item['drive'], MIDIUtil.MIDI2Freq(item['note']))
            else:
                # Pitch bend is set so we need to bend the note

                # The pitch bend range is the index of the value we 
                # need to bend by in PITCH_BEND_RANGES
                bend_range = \
                    list(PITCH_BEND_RANGES.values())[self.pitch_bend_range]

                old_n = MIDIUtil.freq2n(MIDIUtil.MIDI2Freq(item['note']))
                n_mod = MIDIUtil.integer_map_range(
                    pitch_bend,
                    -8192, # Min midi pitchwheel msg value
                    8191,  # Max midi pitchwheel msg value
                    -bend_range, 
                    bend_range)

                #bend the note (based on log)
                Drives.frequency(
                    item['drive'], MIDIUtil.n2freq(old_n+n_mod))


    #------------------------------Properties----------------------------------#

    @property
    def bow(self)-> bool:
        return self._bow
    
    @bow.setter
    def bow(self, bow:bool) -> None:
        self._bow = bool(bow)        

    @property
    def spin(self):
        return self._spin

    @spin.setter
    def spin(self, spin:bool):
        self._spin = bool(spin)
 

    