from floppiano.midi import MIDIUtil
from floppiano.devices import Drives
from floppiano.synths import Synth, PITCH_BEND_RANGES


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

    def pitch_bend(self, pitch_bend:int, bend_range:float) -> None:
        """
            Bends all the notes associated with the DriveVoice
        Args:
            pitch_bend (int): The MIDI pitch_wheel value
            bend_range (float): The number of steps to bend
        """
        if pitch_bend == 0:
            # Pitch bend is zero so ensure that each drive is playing 
            # their original note/frequency
            for address in self._addresses:
                Drives.frequency(address, self._frequency)
        else:
            old_n = MIDIUtil.freq2n(self._frequency)
            #Calculate the offset
            n_mod = MIDIUtil.integer_map_range(
                pitch_bend,
                -8192, # Min midi pitchwheel msg value
                8191,  # Max midi pitchwheel msg value
                -bend_range, 
                bend_range)
            
            bent_freq = MIDIUtil.n2freq(old_n+n_mod)
            for address in self._addresses:
                Drives.frequency(address, bent_freq)   

    def __repr__(self) -> str:
        return f'DriveVoice using addresses {self._addresses}'

class DriveSynth(Synth):
    """
        A DriveSynth is an implementation of Synth that plays notes 
        (from MIDI or programmatically) on Floppy drives.
    """

    def __init__(
        self,
        drive_addresses: tuple[int],
        bow:bool = False,
        spin:bool = False,   
        **kwargs) -> None:
        """
            Constructs a DriveSynth. Accepts Synth arguments via **kwargs 
        Args:
            drive_addresses (tuple[int]): An iterable of int where each int is
                an I2C address of a floppy drive
            bow (bool, optional): The initial bow state of the DriveSynth.
                Defaults to False.
            spin (bool, optional): The initial spin state of the DriveSynth. 
                Defaults to False.
        """
        super().__init__(**kwargs)
        
        # Add support for crash mode and spin (Custom). Both spin and bow use 
        # generic on/off MIDI control change messages
        if 'bow' not in self.control_change_map:
            self.control_change_map['bow'] = 80
        
        if 'spin' not in self.control_change_map:
            self.control_change_map['spin'] = 81

        if 'modulation_wave' in self.control_change_map:
            # Drives only support one modulation wave (triangle)
            # prevent setting property modulation_wave via MIDI
            self.control_change_map.pop('modulation_wave')
        
        if 'hardware_reset' not in self.sysex_map:
            self.sysex_map['hardware_reset'] = 3
        
        self.bow = bow
        self.spin = spin

        #Ensure we have valid drive addresses 
        for address in drive_addresses: Drives._check_address(address)
        
        # Keep a copy of the Drive address to use
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
        self.attach_observer('modulation_wave', self._modulation_wave_changed)

        # Hardware reset to force the drives to match the DriveSynth's state
        self.hardware_reset()

    #----------------------Inherited from from Synth---------------------------#
  
    def note_on(self, note: int, velocity: int, source) -> bool:
        """
            Plays a given MIDI Note. Velocity is ignored. If called directly 
            (not via MIDI) the note on will not be rolled if there are no 
            available voices.
        Args:
            note (int): A valid MIDI Note number
            velocity (int): Ignored
            source (_type_): The source of the incoming MIDI note. Can be None.
            used to turn off a given note with the same source. 

        Returns:
            bool: True if the note was handled, False if the note could not be
            played (There were no available voices.)
        """
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
        """
            Stops a MIDI note from being played (if the note is actively being 
            played) If called directly (not via MIDI) the note off will not be 
            rolled if the note is not being played.
        Args:
            note (int): The MIDI note to halt
            velocity (int): Ignored
            source (_type_): The source from which the note was played

        Returns:
            bool: True if the note was halted, false if the note was not halted
            (The note is not active)
        """
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
        """
            Resets all voices and force un-mutes the DriveSynth
        """
        # Stop all drives from sounding
        Drives.enable(0,False)
        #clear the active stack
        self._active = []
        #reset the available stack, to match our polyphony states
        self._available = self._gen_voices()
        # call super to reset mute state/set defaults       
        super().reset() 
        self.logger.info('DriveSynth reset')
    
    def hardware_reset(self) -> None:
        """
            Immediately forces all drives to match the DriveSynth's states.  
            Resets all voices and force un-mutes the DriveSynth.
        """
        self.mute()  # Ensure all drives are quiet
        self.reset() # Release the mute

        # Invoke all properties that use Drives() calls in order to write the
        # properties to the Drives
        self.bow = self.bow
        self.spin = self.spin
        self.modulation_rate = self.modulation_rate
        self.modulation = self.modulation

        self.logger.info('DriveSynth hardware reset')



    #--------------------Overridden from Synth---------------------------------#

    def mono_mode(self, mono_voices: int = 0) -> None:
        """
        Puts the synth in monophonic mode. If mono_voices is 0, or 
        mono_voices is greater than the number of voices available, all the 
        available voices will be used.

        Args:
            mono_voices (int, optional): The number of voices to used when 
            sounding monophonically

        Raises:
            ValueError: If mono_voices is not in the range [0,127]
        """
        # Call super to do the actual work. Overridden because a DriveSynth must
        # be reset when it's polyphony is changed
        super().mono_mode(mono_voices)
        # Reset to change how the notes will be played
        self.reset()

    def poly_mode(self) -> None:
        """
            Puts the DriveSynth in polyphonic mode using a number of voices
            equal to DriveSynth.poly_voices. If poly_voices is zero or greater
            than the number of available drives, all available drives will be 
            used. 
        """
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

    def _pitch_bend_changed(self, pitch_bend:int) -> None:
        self.logger.info(f'_pitch_bend_changed: {pitch_bend}')
        bend_range = list(PITCH_BEND_RANGES.values())[self.pitch_bend_range]
        # Loop through the active voices and change their pitch based on the
        # incoming bend
        for voice in self._active:
            voice.pitch_bend(pitch_bend, bend_range)               

    def _modulation_wave_changed(self, modulation_wave:int) -> None:
        # Drives only support one modulation wave (triangle)
        # prevent setting property modulation_wave programmatically
        raise NotImplementedError('DriveSynth only supports one modulation wave'
                                  ' (triangle). Setting the modulation_wave is '
                                  'not supported')

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
