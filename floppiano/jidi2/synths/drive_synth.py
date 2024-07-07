from mido import Message
from ..midi import MIDIUtil
from .synth import Synth


class DriveSynth(Synth):

    def __init__(
        self,
        #voices: tuple[DriveVoice], TODO: The synth needs it's drives
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

        self._drives = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
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
            if not self.muted:
                # TODO: play the note if not muted
                # drive.freq = MIDIUtil.note2Freq(msg.note)
                # drive.enable = True
                pass

            # TODO:drive in below needs to be the address of the drive
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

        #We're not playing anything -play the note (if not muted)
        if not self.muted:
            # TODO: play the note using drive(addr0)
            pass

        #Add the drive to the active stack
        self._active.append(
            {
                'source':source,
                'note': msg.note,
                'drive': 0 #TODO: change this to drive(addr 0)
            }
        )

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
                # The note is playing                
               
                # TODO: stop the note from playing
                # drive.enable = false
               
                # Remove from the active stack
                self._active.pop(index)
                # add the drive back to the available
                self._available.append(item['drive'])
                # TODO:drive in below needs to be the address of the drive
                self.logger.debug(
                    f"Note {msg.note} from '{source}' silenced on "
                    f'(addr: {item['drive']})')
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
            # TODO: stop the note from playing
            # drive(addr 0).enable = false 
            
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
        # TODO: stop all drives from playing by using drive addr 0
        # drive(address 0).enable = false
        
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

        # TODO: drive 0 set all bow states
        # drive(addr 0).bow = bow

    @property
    def spin(self):
        return self._spin

    @spin.setter
    def spin(self, spin:bool):
        self._spin = bool(spin)

        # TODO: drive 0 set all spin states
        # drive(addr 0).spin = spin
        

    #----------------------------Property Overrides----------------------------#

    @Synth.modulation_rate.setter
    def modulation_rate(self, modulation_rate:int) -> None:
        if modulation_rate<0 or modulation_rate>127:
            raise ValueError("modulation_rate must be [0-127]")
        self._modulation_rate = modulation_rate

        # TODO: drive 0 set all modulation rates
        # drive(addr 0).modulation_rate = modulation_rate   
    
    @Synth.modulation.setter
    def modulation(self, modulation:int) -> None:
        if not MIDIUtil.isValidModulation(modulation):
            raise ValueError('Not a not valid modulation')
        self._modulation = modulation       
        
        # TODO: drive 0 set all modulation frequencies
        # drive(addr 0).modulation = modulation
    
    @Synth.muted.setter
    def muted(self, muted:bool) -> None:
        self._muted = bool(muted)

        # TODO: ensure all of the active drives are silenced or 
        # all active voices will sound        
        #for item in self._active:
            #item['drive'].enable = not muted        
  
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

    