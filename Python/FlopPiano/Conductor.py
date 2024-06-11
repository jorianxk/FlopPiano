from mido import Message
from smbus import SMBus
from .MIDI import *
from .Drive import *
from .Keyboard import *
import logging
import time

class PitchBendMode(Enum):
    #Number indicates steps. 1/2 steps = 1 note
    HALF     = 0.5 #  1 note(s) or   1/2 step(s)
    WHOLE    =   1 #  2 note(s) or     1 step(s)
    MINOR3RD = 1.5 #  3 note(s) or 1 1/2 step(s)
    MAJOR3RD =   2 #  4 note(s) or     2 step(s)
    FOURTH   = 2.5 #  5 note(s) or 2 1/2 step(s)
    FIFTH    = 3.5 #  7 note(s) or 3 1/2 step(s)
    OCTAVE   =   6 # 12 note(s) or     6 step(s)


#TODO: We need to add provisions for tuning a drive/note
class Note(Drive):

    def __init__(self, i2c_bus:SMBus, address:int) -> None:
        super().__init__(i2c_bus=i2c_bus, address=address)
 
    def setOriginal(self, original:float)->None:
        self._original = original
        self.setCenter(original)

    def setCenter(self, center:float):
        self._center = center
        self.setFrequency(center)

    def bend(self, bendAmount:int, mode:PitchBendMode):
        if bendAmount == 0:
            self.setCenter(self._original)
            return
        else:
            old_n = MIDIUtil.freq2n(self._original)
            n_mod = map_range(bendAmount,-8192,8192,-mode.value, mode.value)
            self.setCenter(MIDIUtil.n2freq(old_n+n_mod))
            
    def modulate(self, modAmount:int):
        if modAmount ==0:
            return
        else:
            #Play with 2, and 16 below for differing effects
            omega = map_range(modAmount,1,127,2,16) * math.pi
            self.setFrequency(self._center+math.sin(omega * time.time()))

    def play(self):
        self.enable = True
        self.update()

class OutputMode(Enum):
    ROLLOVER = 'rollover'
    KEYS = 'keys'
    OFF = 'off'


#TODO:
#-Update all doc strings
#-Add sysex command for shifting keyboard up and down in range - command (4)?
#-switch __init__ to **kwargs?
class Conductor(MIDIListener, MIDIParser):
    #An ID for sysex messages - this is so we know that a sysex message is
    # intended for a Conductor
    __sysex_id__ = 123

    #Index used for mapping sysex command (2) to OutputMode
    __sysex2OutputMode__ = (OutputMode.ROLLOVER, 
                            OutputMode.KEYS, 
                            OutputMode.OFF)

    #Index used for mapping incoming control change (70) to CrashMode
    __cc2CrashMode__ = (CrashMode.OFF, CrashMode.BOW, CrashMode.FLIP)

    #Index used for mapping incoming control change (71) to PitchBendMode
    __cc2PitchMode__ = (PitchBendMode.HALF, 
                        PitchBendMode.WHOLE, 
                        PitchBendMode.MINOR3RD, 
                        PitchBendMode.MAJOR3RD, 
                        PitchBendMode.FOURTH, 
                        PitchBendMode.FIFTH, 
                        PitchBendMode.OCTAVE)
 

    def __init__(self,*,
                 driveAddresses:set[int]= (8, 9, 10 ,11, 12, 13, 14, 15, 16, 17),
                 doKeyboard:bool = True,
                 keyboardAddress:int = 0x77,
                 loopback:bool = True,
                 inChannel:int = 0,
                 outChannel:int = 0,
                 outputMode:int = 0) -> None:
        
        self.logger:logging.Logger = logging.getLogger(__name__)
        ##Init parent classes
        # this does validation for inChannel
        MIDIListener.__init__(self) 
        MIDIParser.__init__(self, self)

        #Setup the I2C bus
        self.i2c_bus:SMBus =  SMBus(1) # indicates /dev/ic2-1

        #Setup the drives(notes)
        # a tuple to hold the unmolested notes/drives
        self.notes:tuple[Note] = [Note(self.i2c_bus,i) for i in driveAddresses] 

        #Setup the keyboard. 
        self.keyboard = Keyboard(i2c_bus=self.i2c_bus,
                                 i2c_address=keyboardAddress)

        self.doKeyboard = doKeyboard
        
        #Setup loopback      
        self.__setLoopback(loopback)

        #Setup input channel
        if (inChannel <0 or inChannel>16):
            raise ValueError("inChannel must be [0-16]")
        self.__setInputChannel(inChannel)

        #Setup output channel
        if (outChannel<0 or outChannel>15):
            raise ValueError("outChannel must be [0-15]")                 
        self.__setOutputChannel(outChannel)

        #Setup output mode
        if (outputMode<0 or outputMode>2):
            raise ValueError("outputMode must be [0-2]")          
        self.__setOutputMode(outputMode)

        #Setup note pools
        self.available_notes:list[Note] = list(self.notes)
        self.active_notes:dict[int,Note] = {} 

        #Setup sound modification states
        self.__setPitchBendMode(6) # set to PitchBendMode.OCTAVE
        self.__setPitchBend(0)
        self.__setModulate(0)

        #Setup the outgoing message buffer
        self.outputBuffer:list[Message] = []

        #make sure the drives are quiet
        self.silence()

    #----------------------_PUBLIC FUNCTIONS-----------------------------------#
    # Used by instantiator to pump the conduct cycle and to manage behavior

    def conduct(self, incoming_msgs:list[Message]=[])->list[Message]:

        keyboard_msgs:list[Message] = []
        if self.doKeyboard:
            #Read the keyboard every time to maintain consistent-ish timing
            keyboard_msgs = self.__getKeyboardMessages()
            #If we want to play the keyboard messages then add them to the incoming
            if(self.loopback): incoming_msgs.extend(keyboard_msgs)

        #Parse all the incoming messages (updates self states)
        for msg in incoming_msgs:
            self.parse(msg)

        #sound all the notes
        self.__soundNotes()
       
        #return any output messages
        return self.__flushOutputBuffer(keyboard_msgs)
    
    def silence(self)->None:
        for note in self.notes:
            note.silence()
        
        #Remove all active notes and put them in the available pool
        for note in self.active_notes.values():
            self.available_notes.append(note)
        
        self.active_notes:dict[int,Note] = {}
        self.logger.info("Silenced all notes and cleared active notes.")

    #----------------------PRIVATE FUNCTIONS-----------------------------------#
    # Used by an instance of Conductor to set states and update operation

    def __getKeyboardMessages(self)->list[Message]:        
        keyboard_msgs:list[Message] = []
        try:
            keyboard_msgs = self.keyboard.read()
        except OSError as oe:
            #This is normal just log it
            self.logger.debug("Error reading keyboard state - skipping")
        finally:
            return keyboard_msgs
    
    def __soundNotes(self)->None:
        try:
            #sound all of the active notes
            for note_id, note in self.active_notes.items():
                note.bend(self.pitchBend,self.pitchBendMode)
                note.modulate(self.modulate)
                note.play()
        except OSError as oe:
            self.logger.warn("Could not update drives - skipping")
    
    def __flushOutputBuffer(self, keyboard_msgs:list[Message]=[])->list[Message]:
        if (self.outputMode == OutputMode.ROLLOVER): #rollover mode
            #if we needed to do something for rollover we'd do it here
            pass 
        elif (self.outputMode == OutputMode.KEYS): #key output only
            #clear the output buffer because we only want key messages
            self.outputBuffer = []
            #add all the keyboard messages to the output buffer - this converts 
            # all the keyboard messages to the outgoing channel
            for msg in keyboard_msgs: self.__add2OutputBuffer(msg)
        elif (self.outputMode == OutputMode.OFF):
            #We don't want to output anything, just output an empty list
            self.outputBuffer = []
        else:
            pass
        
        #temporary variable so we can clear the output buffer before returning
        outgoing_msgs = self.outputBuffer
        #clear the outgoing message buffer
        self.outputBuffer = []

        #return any messages we could not play, or just the keyboard messages
        return outgoing_msgs

    def __add2OutputBuffer(self, msg:Message)->None:
        if MIDIParser.hasChannel(msg):
            #Redirect the output channel to our output channel
            msg.channel = self.outChannel
        
        self.outputBuffer.append(msg)
    
    def __setCrashMode(self, value:int)->None:
        if value < len(Conductor.__cc2CrashMode__):
            mode = Conductor.__cc2CrashMode__[value]
            for note in self.active_notes.values():
                note.crash_mode =  mode
            for note in self.available_notes:
                note.crash_mode =  mode
            self.logger.info(f'Crash Mode set: {mode}')
            return
        self.logger.warn(f"Crash Mode not set: {value} not [0-2]")
    
    def __setPitchBendMode(self, value:int)->None:
        if value < len(Conductor.__cc2PitchMode__):
            mode = Conductor.__cc2PitchMode__[value]
            self.pitchBendMode = mode
            self.logger.info(f'Pitch Bend Mode set: {self.pitchBendMode}')
            return 
        self.logger.warn(f"Pitch Bend Mode not set: {value} not [0-6]")
    
    def __setPitchBend(self, value:int)->None:
        self.pitchBend = value
        self.logger.debug(f'Pitch Bend set: {self.pitchBend}')
    
    def __setModulate(self, value:int)->None:
        self.modulate = value
        self.logger.debug(f'Modulate set: {self.modulate}')

    def __setInputChannel(self, inputChannel:int)->None:
        #check that value is in in channel range
        if (inputChannel>=0 and inputChannel <= 16):
            #Value maps as below:
            # 0 = all channels, 1 = channel 0, 2 = channel 1 ...
            self.inChannel = (inputChannel -1)
            # change the keyboard to send to the new input channel
            if (self.inChannel > -1):
                self.keyboard.channel = self.inChannel

            self.logger.info(f'Input channel set: {self.inChannel} [change on conduct()]')
            return

        self.logger.warn(f"Input channel not set: {inputChannel} not [0-16]")
    
    def __setOutputChannel(self, outputChannel:int)->None:
        if (outputChannel <=15):
            self.outChannel = outputChannel
            self.logger.info(f'Output channel set: {self.outChannel}')
            return
        self.logger.warn(f"Input channel NOT set: {outputChannel} not [0-15]")

    def __setOutputMode(self, value:int)->None:
        #check that value valid output mode, if not ignore 
        if (value < len(Conductor.__sysex2OutputMode__)):
            #convert the value to a OutputMode, and set the mode
            mode = Conductor.__sysex2OutputMode__[value]
            self.outputMode = mode
            self.logger.info(f'Output mode set: {self.outputMode}')
            return
        self.logger.warn(f"Output mode not set: {value} not [0-2]")

    def __setLoopback(self, value:int)->None:
        #Warning: takes effect after next conduct cycle
        loopback = bool(value)
        self.loopback = loopback
        self.logger.info(f'Loopback set: {self.loopback} [change on conduct()]')

    #---------------------------MIDI HANDLING----------------------------------#
    # Inherited from MIDIListener used to handle incoming mido.Messages

    def noteOn(self, msg:Message)->None:
        try:
            #get an available Note and remove it from the pool
            nextNote:Note = self.available_notes.pop()

            #Modify the note to match the incoming message
            nextNote.setOriginal(MIDIUtil.MIDI2Freq(msg.note))

            #add the note to the active notes, so that it will be played
            self.active_notes[msg.note] = nextNote

            self.logger.debug(f'Added note: {msg.note} to active notes [address:{nextNote.address}].')

        except IndexError as ie: #There are no available drives. 
            self.logger.debug(f'Cant add note: {msg.note}, no available drives - rolled')
            #We can't play it so pass it along
            self.__add2OutputBuffer(msg)

    def noteOff(self, msg:Message)->None:
        try:
            #get the active note
            playedNote:Note = self.active_notes.pop(msg.note)

            #stop the note playing
            playedNote.silence()
            self.logger.debug(f'Removed note: {msg.note} from active notes [address:{playedNote.address}]')          

            #add the drive back to the available note pool
            self.available_notes.append(playedNote)

        except KeyError as ke:
            self.logger.debug(f"Attempted to remove: {msg.note} - but it's not playing [rolled?]") 
            #if we're not playing that note pass it along
            self.__add2OutputBuffer(msg)
    
    def controlChange(self, msg:Message)->None:  
        #1 -> modulation value is 0 = off else value 
        if msg.control == 1: # this is a modulation cc
            self.__setModulate(msg.value)

        #70 -> Sound Controller sound variation -> CRASH MODES
        if msg.control == 70:
            self.__setCrashMode(msg.value)
        
        #71 -> control pitch bend range
        if msg.control == 71:
            self.__setPitchBendMode(msg.value)

        #120, 123 -> Mute/stop all sounding notes drives
        if msg.control == 120 or msg.control ==123:
            self.silence()

        #pass along all cc msgs
        self.__add2OutputBuffer(msg)

    def pitchwheel(self, msg:Message)->None:
        self.__setPitchBend(msg.pitch)
        #pass along all pitch messages
        self.__add2OutputBuffer(msg)
    
    def sysex(self, msg:Message)->None:
         
        #ignore any system messages that don't have 3 data bytes
        if (not (len(msg.data)<3 or len(msg.data)>3)):
            id = msg.data[0]
            command = msg.data[1]
            value = msg.data[2]

            #check that the first byte matches our id ignore it otherwise
            if(id == Conductor.__sysex_id__):                
                #check what the command is
                if (command == 0): # Input channel change command
                    self.__setInputChannel(value)
                elif (command == 1): # Output channel change command 
                    self.__setOutputChannel(value)
                elif (command == 2): # Output mode change command
                    self.__setOutputMode(value)
                elif (command == 3): # Loopback change command
                    self.__setLoopback(value)
                else:
                    #we could add other things here
                    pass
   
        #we need to pass along all sysex messages
        self.__add2OutputBuffer(msg)
