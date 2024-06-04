from .FloppyDrives  import FloppyDrive
from .Utils import  MIDIUtil
from mido import Message
from smbus import SMBus
import copy


class MidiMessageListener():

    def noteOnMsg(self, message:Message):
        pass

    def noteOffMsg(self, message:Message):
        pass
    
    def controlChangeMsg(self, message:Message):
        pass
    
    def pitchwheelMsg(self, message:Message):
        pass

    def sysexMsg(self, message:Message):
        pass
    
    def startMsg(self, message:Message):
        pass

    def stopMsg(self, message:Message):
        pass

    def resetMsg(self, message:Message):
        pass

class MessageParser():
    
    def __init__(self, listener:MidiMessageListener) -> None:
        self.listener = listener
    
    def parseMessage(self, message:Message):
        msgType = message.type
        if (message.type =='note_on'):

            if (message.velocity == 0):
                self.listener.noteOffMsg(message)
            else:
                self.listener.noteOnMsg(message)

        elif (message.type == 'note_off'):

            self.listener.noteOffMsg(message)

        elif (message.type == 'control_change'):

            self.listener.controlChangeMsg(message)

        elif (message.type == 'pitchwheel'):

            self.listener.pitchwheelMsg(message)

        elif (message.type == 'sysex'):

            self.listener.sysexMsg(message)

        elif (message.type == 'start'):

            self.listener.startMsg(message)

        elif (message.type == 'stop'):

            self.listener.stopMsg(message)

        elif (message.type == 'reset'):

            self.listener.resetMsg(message)
        
        else:

            pass

class FloppyDriveHandler():
    
    def __init__(self, drives:list[FloppyDrive]) -> None:
        self.i2c_bus:SMBus =  SMBus(1) # indicates /dev/ic2-1
        self.drives = drives
    
    #TODO: update docstring
    def updateDrive(self, drive:FloppyDrive, justCTRL:bool=True)->None:
        """
        A function to send all set CTRL Register values and TOP values a slave 
        drive, or to broadcast to the bus

        see code firmware and send(self, address:int=None, justCTRL:bool=True)
        Comments for details

        parameters: 
            address:int optional. if none the data is sent bus wide (broadcast)
                to all devices on the bus (address 0x0)
            justCTRL:bool optional. if true, just the CTRL register is sent
                if false, CTRL plus the TOP value is sent to the address

        raises: 
            Idk some error: If the I2C bus cant sent the message for whatever
            reason          
        """

        # |------------------------------------------------------------------|
        # |                   The 'FIRST Byte' - CTRL byte                   |
        # |------------------------------------------------------------------|
        # |   0000   |     0      |       0      |      0     |      0       |
        # |----------|------------|--------------|---------------------------|
        # | Not used | Crash Mode |  Crash Mode  | Drive Spin | Drive Enable |
        # |------------------------------------------------------------------| 
        # 
        #  Crash mode - the two crash mode bits represent which crash mode the
        #  drive will use. Two bit combined give four possible states:
        #    MSB LSB
        #     0   0  - Crash prevention OFF
        #     0   1  - Crash prevention ON (BOW Mode)
        #     1   0  - Crash prevention ON (FLIP Mode)
        #     1   1  - Not used (results in crash prevention mode off if set)
        #     
        #     BOW mode: The drive will step until end of travel then flip
        #     direction (like a violin bow changing direction at the end of a
        #     bow stroke)
        #     
        #     FLIP mode: THe drive will flip direction after every step/pulse
        #  
        #  Drive Spin - if the bit is 1, the SPIN_PIN is pulled HIGH. 0 
        #  SPIN_PIN is pulled LOW. This is to turn on/off disc spin.
        #  
        #  Drive Enable - if the bit is high then the drive select/enable 
        #  (ENABLE_PIN) pin is pulled LOW (because the drives are active low) 
        #  and the drive is selected/enabled. If 0, then then the ENABLE_PIN
        #  is pulled HIGH and the drive is de-selected/disabled.

        #Prepare the CTRL Register 
        CTRL = (drive.crash_mode.value << 2)     
        CTRL = CTRL | (drive.spin << 1)
        CTRL = CTRL | (drive.enable)

        #print("{:08b}".format(CTRL), CTRL)

        #|----------------------------------------------------------------|
        #|            The second and third bytes - TOP Value              |
        #|----------------------------------------------------------------|
        #|  The second byte is the most significant byte of the TOP value |
        #|  The third byte is the least significant byte of the TOP value |
        #|----------------------------------------------------------------|

        TOP = drive.top.to_bytes(2,'little')

        
        ########################################################################
        #                  Write the values to the address                     #
        ########################################################################



        # #are we just senting the CTRL register?
        if(justCTRL):
            self.i2c_bus.write_block_data(drive.address, CTRL, [])
        else:
            self.i2c_bus.write_block_data(drive.address, CTRL, [TOP[1], TOP[0]])

    #TODO: update docstring
    def silenceDrives(self)->None:
        for drive in self.drives:
            drive.enable = False
            drive.spin = False
            self.updateDrive(drive, justCTRL=True)

class FloppyDrivePlayer(FloppyDriveHandler, MidiMessageListener):

    def __init__(self, drives: list[FloppyDrive]) -> None:
        super().__init__(drives)
        self.available_drives = copy.copy(drives)
        self.active_notes = dict() 
        self.transpose:int = 0

    def noteOnMsg(self, message:Message):

        note = message.note + self.transpose
        # #check that the note can actually be sounded
        # if(not (note <=27 or note>=127)):
        # if(not (message.note <FloppyDrive.__min_note__ or message.note>FloppyDrive.__max_note__)):
            #Cant play a note if all drives are busy
        if (len(self.available_drives)==0):
            print("Can't play", message.note, "no available drives")
            print("    ", len(self.available_drives))
        else:
            #get an available drive
            next_drive:FloppyDrive = self.available_drives.pop()
            #set up the drive to play the note 
            next_drive.setFrequency(MIDIUtil.MIDI2Freq(note))
            next_drive.enable = True

            #tell the drive to play the note
            self.updateDrive(next_drive, justCTRL=False)
            print("Playing", message.note, "on address", next_drive.address)

            #add the note to the active notes
            self.active_notes[message.note] = next_drive
        # else:
        #     print("Can't sound:", message)

    def noteOffMsg(self, message:Message):
        #handle note off
        #note_on velocity 0 is the same as note off
        #print('Found note off',msg.note ,MIDI_LOOK_UP[msg.note])
        #Get the drive that was playing the note

        try:
            sounding_drive:FloppyDrive = self.active_notes.pop(message.note)

            #stop the drive from playing
            sounding_drive.enable = False
            self.updateDrive(sounding_drive, justCTRL=True)
            print("Stopped", message.note, "on address", sounding_drive.address)

            #add the drive back to the available drives
            self.available_drives.append(sounding_drive)
        except KeyError as ke:
            print("Commanded to stop", message.note, "but it's not playing")
        
    
    def controlChangeMsg(self, message:Message):
        pass
    
    def pitchwheelMsg(self, message:Message):
        
        transpose = FloppyDrivePlayer.map_range(message.pitch, -8192,8192, -6, 6)
        for note in self.active_notes:
            newNote = note + transpose
            if (MIDIUtil.isValidMIDI(newNote)):
                sounding_drive:FloppyDrive = self.active_notes[note]
                sounding_drive.setFrequency(MIDIUtil.MIDI2Freq(newNote))
                self.updateDrive(sounding_drive, justCTRL=False)
        self.transpose = transpose
        print("Pitch bent by", transpose)
        

    
    @classmethod
    def map_range(cls, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
