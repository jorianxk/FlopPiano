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
        
        # Add support for crash mode and spin
        if 'bow' not in self.control_change_map:
            self.control_change_map['bow'] = 70
        
        if 'spin' not in self.control_change_map:
            self.control_change_map['spin'] = 75

        self.bow = bow
        self.spin = spin

        self._drives = drive_addresses
        self._available = self._drives.copy()
        self._active = []



    #-------------------------Inherited from from Synth------------------------#

    def note_on(self, msg: Message, source) -> Message:
        # Handle monophonic behavior
        if not self.polyphonic: return self.mono_note_on(msg, source)        
        try:
            #Get an available drive
            drive = self._available.pop()
            #Add it to the active stack
            self._active.append(
                {
                    'source': source,
                    'note': msg.note,
                    'drive': drive
                }
            )
            #Play the note (if not muted)
            Drives.frequency(drive, MIDIUtil.MIDI2Freq(msg.note))
            Drives.enable(drive, not self.muted)

            self.logger.debug(
                f"Note {msg.note} from '{source}' played (addr: {drive})")
        except IndexError: 
            #We could not get an available drive
            self.logger.debug(
                'No available drives. '
                f"Note {msg.note} from '{source}' rolled")
            #Return the message so it gets sent to the output
            return msg

        #We played the note, nothing to rollover
        return None
    
    def mono_note_on(self, msg: Message, source) -> Message:
        #Are we currently playing a note? if so, roll the incoming note
        if len (self._active) == 1: 
            self.logger.debug(
                'No available drives. '
                f"Note {msg.note} from '{source}' rolled (monophonic)")
            return msg
        
        if len(self._active) != 0: 
            raise Exception("mono_note_on -malformed active stack")

        #Add the drive to the active stack
        self._active.append(
            {
                'source':source,
                'note': msg.note,
                'drive': 0 
            }
        )

        #We're not playing anything -play the note on all drives (if not muted)
        Drives.frequency(0, MIDIUtil.MIDI2Freq(msg.note))
        Drives.enable(0, not self.muted)

        self.logger.debug(
            f"Note {msg.note} from '{source}' played (addr: 0 monophonic)")
        
        #We played the note - nothing to return
        return None
 
    def note_off(self, msg: Message, source) -> Message:
        # Handle monophonic behavior
        if not self.polyphonic: return self.mono_note_off(msg, source)
        # Test to see if that note is playing
        for index ,item in enumerate(self._active):
            if item['source'] == source and item['note'] == msg.note:
                #The note is playing so stop the drive
                drive = item['drive']
                Drives.enable(drive,False)               
                # Remove from the active stack
                self._active.pop(index)
                # add the drive back to the available
                self._available.append(drive)
                self.logger.debug(
                    f"Note {msg.note} from '{source}' silenced on "
                    f'(addr: {drive})')
                break
        else:
            #The note is not currently playing
            self.logger.debug(
                f"Note {msg.note} from '{source}' is not playing (rolled?)")
            #if the message got rolled we need to pass off the msg so it stops
            return msg
            
        #We successfully stopped the note, nothing to rollover
        return None

    def mono_note_off(self, msg: Message, source) -> Message:
        if len(self._active) !=0 and len(self._active) !=1: 
            raise Exception("mono_note_off - malformed active stack")

        # We're not playing anything so roll the msg
        if len(self._active) == 0:
            self.logger.debug(
                f"Note {msg.note} from '{source}' is not playing "
                '(rolled? monophonic)')
            return msg

        # Check if the message is our note
        active = self._active[0]       
        if active['source'] == source and active['note'] == msg.note:
            #Stop the drive from playing
            Drives.enable(0, False)            
            #clear the active list
            self._active =[]              
            self.logger.debug(
                f"Note {msg.note} from '{source}', silenced on "
                '(addr: 0 monophonic)')
            # We successfully stopped the note, nothing to rollover
            return None
        
        # We're not playing it so pass it along
        self.logger.debug(
            f"Note {msg.note} from '{source}' is not playing "
            '(rolled? monophonic)')
        return msg

    def reset(self) -> None:
        Drives.enable(0,False)
        
        #clear the active stack
        self._active = []

        #reset the available stack
        self._available = self._drives.copy()

        self.logger.info('drive synth reset')
  
    #------------------------------Properties----------------------------------#

    @property
    def bow(self)-> bool:
        return self._bow
    
    @bow.setter
    def bow(self, bow:bool) -> None:
        self._bow = bool(bow)
        Drives.bow(0,self.bow)


    @property
    def spin(self):
        return self._spin

    @spin.setter
    def spin(self, spin:bool):
        self._spin = bool(spin)
        Drives.spin(0, self.spin)
        

    #----------------------------Property Overrides----------------------------#

    @Synth.modulation_rate.setter
    def modulation_rate(self, modulation_rate:int) -> None:
        #MIDI prevents the rate from being set any higher than 127, 
        #but the drives can go up to 255
        if modulation_rate<0 or modulation_rate>127:
            raise ValueError("modulation_rate must be [0-127]")
        self._modulation_rate = modulation_rate

        Drives.modulation_rate(0, self.modulation_rate)
    
    @Synth.modulation.setter
    def modulation(self, modulation:int) -> None:
        if not MIDIUtil.isValidModulation(modulation):
            raise ValueError('Not a not valid modulation')
        self._modulation = modulation       

        #TODO only 1-16hz sounds good, do we want this hard coded?
        # 0 -> no modulation
        modulation_freq = MIDIUtil.integer_map_range(
            self.modulation, 0, 127, 0, 16)
                   
        Drives.modulation_frequency(0,modulation_freq)
    
    @Synth.muted.setter
    def muted(self, muted:bool) -> None:
        self._muted = bool(muted)

        try:
            # Ensure all of the active drives are silenced or that all active drives
            # will sound        
            for item in self._active:
                Drives.enable(item['drive'], not muted)   
        except AttributeError:
            # This occurs when the Synth constructor sets self.muted
            # self._active does not exist yet 
            pass     
  
    @Synth.polyphonic.setter
    def polyphonic(self, polyphonic:bool):
        try:
            # We need to silence all drives and clear the active stack when we 
            # change polyphony
            if polyphonic != self.polyphonic:
                self.reset()
        except AttributeError:
            # This occurs when the Synth constructor sets self.polyphonic
            # self._polyphonic does not exist yet 
            pass

        self._polyphonic = bool(polyphonic)



    @Synth.pitch_bend.setter
    def pitch_bend(self, pitch_bend:int) -> None:
        if not MIDIUtil.isValidPitch(pitch_bend):
            raise ValueError('Not a valid pitch bend')
           
        self._pitch_bend = pitch_bend
        
        try:
            # We DON'T change the note since the note is the identifier for
            # turning on/off drives. We changed the drives' sounding frequency
         
            # Loop through the active drives and change their pitch based on the
            # incoming bend
            for item in self._active:

                if self.pitch_bend == 0:
                    # Pitch bend is zero so ensure that each drive is playing 
                    # their original note
                    Drives.frequency(
                        item['drive'], MIDIUtil.MIDI2Freq(item['note']))
                else:
                    # Pitch bend is set so we need to bend the note

                    # The self.pitch_bend_range is the index of the value we 
                    # need to bend by in PITCH_BEND_RANGES
                    bend_range = \
                        list(PITCH_BEND_RANGES.values())[self.pitch_bend_range]

                    old_n = MIDIUtil.freq2n(MIDIUtil.MIDI2Freq(item['note']))
                    n_mod = MIDIUtil.integer_map_range(
                        self.pitch_bend,
                        -8192, # Min midi pitchwheel msg value
                        8191,  # Max midi pitchwheel msg value
                        -bend_range, 
                        bend_range)

                    #bend the note (based on log)
                    Drives.frequency(
                        item['drive'], MIDIUtil.n2freq(old_n+n_mod))
                    
        except AttributeError:
            # This occurs when the Synth constructor sets self.pitch and
            # self._active does not exist yet
            pass

    