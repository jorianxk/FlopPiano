import mido
from mido import Message

from .Drives import *
from .MIDI import *
from smbus import SMBus
import copy

# from threading import Thread, Event
# from queue import Queue, Empty
# import time


class Conductor(MIDIListener):

    __cc2PitchMode__ = (PitchBendMode.HALF, 
                        PitchBendMode.WHOLE, 
                        PitchBendMode.MINOR3RD, 
                        PitchBendMode.MAJOR3RD, 
                        PitchBendMode.FOURTH, 
                        PitchBendMode.FIFTH, 
                        PitchBendMode.OCTAVE)
    
    __cc2CrashMode__ = (CrashMode.OFF, CrashMode.BOW, CrashMode.FLIP)

    def __init__(self, *,
                 driveAddresses:set[int],
                 inChannel:int = -1) -> None:
        
        MIDIListener.__init__(self, inChannel)
  
        self.i2c_bus:SMBus =  SMBus(1) # indicates /dev/ic2-1

        self.notes:list[Note] = [] # a list to hold the unmolested notes/drives

        for addr in driveAddresses:
            self.notes.append(Note(i2c_bus=self.i2c_bus, address=addr))

        self.available_notes:list[Note] = copy.copy(self.notes)
        self.active_notes:dict[int,Note] = {} 

        self.pitchBendMode = PitchBendMode.OCTAVE
        self.pitchBend = 0
        self.modulate = 0

        self.outputMessages:list[Message] = []

    def conduct(self)->list[Message]:        
        for note_id, note in self.active_notes.items():
            note.bend(self.pitchBend,self.pitchBendMode)
            note.modulate(self.modulate)
            note.play()
        
        #return any messages that we could not play/ need to pass on
        out = self.outputMessages
        self.outputMessages = []
        return out

    def noteOn(self, msg:Message):
        try:
            #get an available Note and remove it from the pool
            nextNote:Note = self.available_notes.pop()

            #Modify the note to match the incoming message
            nextNote.setOriginal(MIDIUtil.MIDI2Freq(msg.note))

            #add the note to the active notes, so that it will be played
            self.active_notes[msg.note] = nextNote
            #print(f'Added note:{msg.note} to active notes [address:{nextNote.address}].')

        except IndexError as ie: #There are no available drives. 
            #print(f'Cant add note:{msg.note}, no available drives. passing it along')
            #pass along notes we could not play
            self.outputMessages.append(msg)

    def noteOff(self, msg:Message):
        try:
            #get the active note
            playedNote:Note = self.active_notes.pop(msg.note)

            #stop the note playing
            playedNote.silence()            
            #print(f'Removed note:{msg.note} on address {playedNote.address}')

            #add the drive back to the available note pool
            self.available_notes.append(playedNote)

        except KeyError as ke:
            #print("Commanded to stop", msg.note, "but it's not playing - it was probably rolled over")
            #if we're not playing that note pas it along
            self.outputMessages.append(msg)
    
    def controlChange(self, msg:Message):  
        #1 -> modulation value is 0 = off else value 
        if msg.control == 1: # this is a modulation cc
            self.modulate = msg.value

        #70 -> Sound Controller sound variation -> CRASH MODES
        if msg.control == 70:
            if msg.value < len(Conductor.__cc2CrashMode__):
                for note in self.active_notes.values():
                    note.crash_mode =  Conductor.__cc2CrashMode__[msg.value]
                for note in self.available_notes:
                    note.crash_mode =  Conductor.__cc2CrashMode__[msg.value]
        
        #71 -> control pitch bend range
        if msg.control == 71:
            if msg.value < len(Conductor.__cc2PitchMode__):
                self.pitchBendMode = Conductor.__cc2PitchMode__[msg.value]

        #120, 123 -> Mute/stop all sounding notes drives
        if msg.control == 120 or msg.control ==123:
            self.silence()
        
        #we need to pass on all cc messages
        self.outputMessages.append(msg)


    def pitchwheel(self, msg:Message):
        self.pitchBend = msg.pitch
        #we need to pass on all pitchwheel msgs
        self.outputMessages.append(msg)

    #TODO handle sysex
    def sysex(self, msg:Message):
        '''
            Sysex messages
            LISTENING current channel 
                specific 
                all channels
            OUTPUT channel 
                specific 
                all channels
        '''
        pass
    
    def silence(self)->None:
        for note in self.notes:
            note.silence()
        
        #Remove all active notes and put them in the available pool
        for note in self.active_notes.values():
            self.available_notes.append(note)
        
        self.active_notes:dict[int,Note] = {}
