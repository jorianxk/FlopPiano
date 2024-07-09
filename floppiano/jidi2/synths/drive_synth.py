from .synth import Synth, PITCH_BEND_RANGES
from ..midi import MIDIUtil
from ..devices import Drives

#TODO what about bus errors on 'Drives' calls?

class DriveSynth(Synth):

    def __init__(
        self,
        drive_addresses: list[int],
        bow:bool = False,
        spin:bool = False,   
        **kwargs) -> None:

        super().__init__(**kwargs)
        
        # Add support for crash mode and spin (Custom). Both spin and bow use 
        # generic on/off MIDI control change messages
        if 'bow' not in self.control_change_map:
            self.control_change_map['bow'] = 80
        
        if 'spin' not in self.control_change_map:
            self.control_change_map['spin'] = 81

        self.bow = bow
        self.spin = spin

        self._drives = drive_addresses
        self._available = self._drives.copy()
        self._active = []

        # Setup property changed callbacks/observers
        self.attach_observer('bow', self._bow_changed)
        self.attach_observer('spin', self._spin_changed)
        self.attach_observer('modulation_rate', self._modulation_rate_changed)
        self.attach_observer('modulation', self._modulation_changed)
        self.attach_observer('muted', self._muted_changed)
        self.attach_observer('pitch_bend', self._pitch_bend_changed)
        self.attach_observer('poly_voices', self._poly_voices_changed)

    #----------------------Inherited from from Synth---------------------------#

    #TODO write the stuff that makes drives go. AGAIN
    def note_on(self, note: int, velocity: int, source) -> bool:
        return super().note_on(note, velocity, source)
    
    def note_off(self, note: int, velocity: int, source) -> bool:
        return super().note_off(note, velocity, source)

    def reset(self) -> None:
        super().reset() # call super to reset mute state/set defaults
        #clear the active stack
        self._active = []
        #reset the available stack
        self._available = self._drives.copy()
        self.logger.info('drive synth reset')

    #--------------------Overridden from Synth---------------------------------#

    def mono_mode(self, mono_voices: int = 0) -> None:
        # Call super to do the actual work. Overridden because a DriveSynth must
        # be reset when it's polyphony is changed
        super().mono_mode(mono_voices)
        # Reset to change how the notes will be played
        self.reset()

    def poly_mode(self) -> None:
        # Call super to do the actual work. Overridden because a DriveSynth must
        # be reset when it's polyphony is changed
        super().poly_mode()
        # Reset to change how the notes will be played
        self.reset()

    #------------------Property Callbacks/Observers----------------------------#

    def _bow_changed(self, bow:bool) -> None:
        self.logger.info(f'_bow_changed: {bow}')
        Drives.bow(0, bow)

    def _spin_changed(self, spin:bool) -> None:
        self.logger.info(f'_spin_changed: {spin}')
        # Update all drives' spin states
        Drives.spin(0, spin)
    
    def _modulation_rate_changed(self, modulation_rate:int) -> None:
        self.logger.info(f'modulation_rate_changed: {modulation_rate}')
        # Update all drives' modulation rates
        Drives.modulation_rate(0, modulation_rate)
    
    def _modulation_changed(self, modulation:int) -> None:
        #TODO only 1-16hz sounds good, do we want this hard coded?
        # 0 -> no modulation/off
        self.logger.info(f'_modulation_changed: {modulation}')
        # Map the frequency
        modulation_freq = MIDIUtil.integer_map_range(modulation, 0, 127, 0, 16)
        # Update all drives' modulation frequencies                  
        Drives.modulation_frequency(0,modulation_freq)

    def _muted_changed(self, muted:bool) -> None:
        self.logger.info(f'_muted_changed: {muted}')
        # Update all drives' enable states
        Drives.enable(0, not muted)
    
    def _poly_voices_changed(self,  poly_voices:int) -> None:
        # If currently polyphonic a reset is needed to reflect the changes. 
        # If monophonic, no worries poly_voice will be used when a change in 
        # polyphony occurs
        self.logger.info(f'_poly_voices_changed: {poly_voices}')
        if self.polyphonic:
            self.reset()
    
    # TODO: this isn't working right - fix it
    def _pitch_bend_changed(self, pitch_bend:int) -> None:
        self.logger.info(f'_pitch_bend_changed: {pitch_bend}')
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

    # TODO: Update the MIDI message <65 >65 on/off thing for bool states
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
 