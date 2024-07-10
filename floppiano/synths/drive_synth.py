from typing import Any
from .synth import Synth, PITCH_BEND_RANGES
from midi import MIDIUtil
from devices import Drives

#TODO what about bus errors on 'Drives' calls?

class DriveVoice():
    """
        A DriveVoice is an object that encapsulates one or more floppy drives
        to make them a act single synth voice and manages I2C calls to do so. 
    """

    def __init__(self, addresses:tuple[int]) -> None:
        """
            A DriveVoice is an object that encapsulates one or more floppy drives
            to make them a act single synth voice and manages I2C calls to do so
        Args:
            addresses (tuple[int]): The iterable list/tuple of floppy drive 
                I2C addresses to use.
        """
        #Should only be set once.
        self._addresses = addresses
        #public, can set be at anytime
        self.source = None
        # set by note setter/getter
        self._frequency = None
  
    @property
    def addresses(self) -> list[int]:
        """
            The I2C address of the floppy drives being used for the DriveVoice. 
        """
        return self._addresses
    
    @property
    def note(self) -> int:
        """
            Gets the current MIDI note of the DriveVoice
        """
        return MIDIUtil.freq2MIDI(self._frequency)
    
    @note.setter
    def note(self, note:int):
        """
            Sets the current MIDI note of the DriveVoice
        """
        self._frequency = MIDIUtil.MIDI2Freq(note)


    def play(self) -> bool:
        """
            Immediately plays the current note on all floppy drives associated 
            with the DriveVoice (if the current note is set).

        Returns:
            bool: True if the floppy drives were played. (DriveVoice note is not
            none), False otherwise
        """        

        if self._frequency is not None:
            for address in self._addresses:
                Drives.frequency(address, self._frequency)
                Drives.enable(address, True)
            return True
        
        return False
    
    def silence(self):
        """
            Immediately silences all floppy drives associated with the 
            DriveVoice.
        """
        for address in self._addresses:
            Drives.enable(address, False)

    def match_mute(self, muted:bool):
        """
            Immediately matches the mute state of all floppy drives associated 
            with the DriveVoice.
        Args:
            muted (bool): The mute state to be matched
        """        
        for address in self._addresses:
            Drives.enable(address, not muted)

    def __repr__(self) -> str:
        return f'DriveVoice using addresses {self._addresses}'
    
    # def __eq__(self, value: object) -> bool:
    #     if isinstance(value, DriveVoice):
    #         if self.addresses != value.addresses:
    #             return False
    #         if self.source != value.source:
    #             return False
    #         if self._frequency != value._frequency:
    #             return False

    #         return True               

    #     return False

class DriveSynth(Synth):

    def __init__(
        self,
        drive_addresses: tuple[int],
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

        #Ensure we have valid drive addresses 
        for address in drive_addresses: Drives._check_address(address)
        
        # Keep a copy of the Drive address the use
        self._drive_addresses = drive_addresses
        # Set the available voice stack to match the polyphony state
        self._available:list[DriveVoice] = self._gen_voices()        
        self._active:list[DriveVoice] = []
    
        # Setup property changed callbacks/observers
        self.attach_observer('bow', self._bow_changed)
        self.attach_observer('spin', self._spin_changed)
        self.attach_observer('modulation_rate', self._modulation_rate_changed)
        self.attach_observer('modulation', self._modulation_changed)
        self.attach_observer('muted', self._muted_changed)
        self.attach_observer('pitch_bend', self._pitch_bend_changed)
        self.attach_observer('poly_voices', self._poly_voices_changed)

    #----------------------Inherited from from Synth---------------------------#
  
    def note_on(self, note: int, velocity: int, source) -> bool:
        try:
            #Get an available voice throws IndexError if not possible
            voice = self._available.pop()
            # Setup the voice
            voice.note = note
            voice.source = source
            #Play the note (if not muted)
            if not self.muted:
                voice.play()

            #add the voice to the active pool/stack
            self._active.append(voice)

            self.logger.debug(
                f"Note {note} from '{source}' played with {voice}")
        except IndexError: 
            #We could not get an available drive
            self.logger.debug(
                'No available DriveVoices. '
                f"Note {note} from '{source}' rolled")
            #We did not handle the note, return false so that it is rolled
            return False

        #We handled the note, return true (nothing to rollover)
        return True
    
    def note_off(self, note: int, velocity: int, source) -> bool:
        # Test to see if that note is playing
        for index, voice in enumerate(self._active):
            if voice.source == source and voice.note == note:
                #The note is playing so stop it
                voice.silence()          
                # Remove from the active stack
                self._active.pop(index)
                # add the drive back to the available pool
                self._available.append(voice)
                self.logger.debug(
                    f"Note {note} from '{source}' silenced with {voice} ")
                break
        else:
            #The note is not currently playing
            self.logger.debug(
                f"Note {note} from '{source}' is not playing (rolled?)")
            #if the message got rolled we need to pass off the msg so it stops
            return False
            
        #We successfully stopped the note, nothing to rollover
        return True

    def reset(self) -> None:
        # Stop all drives from sounding
        Drives.enable(0,False)
        #clear the active stack
        self._active = []
        #reset the available stack, to match our polyphony states
        self._available = self._gen_voices()
        # call super to reset mute state/set defaults       
        super().reset() 
        self.logger.info('DriveSynth reset')

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
        # Update active drives' enable states so they are muted/not muted
        for voice in self._active:
            voice.match_mute(muted)
    
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
                
    #---------------------------Private Functions------------------------------#

    def _gen_voices(self) -> list[DriveVoice]:
        """
            Generates an appropriate list of DriveVoices based upon the
            polyphony (or lack thereof) state  of the DriveSynth. 
        Returns:
            list[DriveVoice]: The list of Drive Voices to be used as the
                available voice pool for the DriveSynth
        """
        voices = []        
        if self.polyphonic:
            # DriveSynth is polyphonic
            # if self.poly_voices == 0 or self.poly_voices is greater than the 
            # number of drives/addresses, use as many DriveVoices as there are 
            # drives/addresses. Otherwise split the drives/addresses equally 
            # into a number of DriveVoices equal to self.poly_voices and don't
            # use the remainder drives/addresses
            if self.poly_voices == 0 or \
                (self.poly_voices > len(self._drive_addresses)):
                for address in self._drive_addresses:
                    voices.append(DriveVoice((address,)))
                return voices

            address_pool = list(self._drive_addresses)
            address_per_voice = len(address_pool) // self.poly_voices

            for _ in range(self.poly_voices):
                voice_addresses = []
                for i in range(address_per_voice):
                    voice_addresses.append(address_pool.pop())
                voices.append(DriveVoice(tuple(voice_addresses)))
            return voices            
        else:
            # DriveSynth is  monophonic
            # if self._mono_voices == 0 or self._mono_voices is greater
            # than the number of drives/address then use all the drives/
            # addresses on one voice. Otherwise use a single DriveVoice but with
            # a number of drives/addresses == self._mono_voices.             
            if self._mono_voices == 0 or \
                (self.mono_voices > len(self._drive_addresses)):
                #Use all drives/addresses on a single voice
                voices.append(DriveVoice(self._drive_addresses))
                return voices            

            drives_to_use = tuple(
                self._drive_addresses[i] for i in range(self.mono_voices))
            
            voices.append(DriveVoice(drives_to_use))
            return voices

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
    