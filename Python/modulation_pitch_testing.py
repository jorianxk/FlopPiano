from FlopPiano.FloppyDrives import FloppyDrive
from FlopPiano.Utils import MIDIUtil
from smbus import SMBus
from enum import Enum
import copy
import time 
import math




class Note():

    def __init__(self, midi_id:int, drive:FloppyDrive) -> None:
        if (not MIDIUtil.isValidMIDI(midi_id)):
            raise ValueError ("midi_id is not a valid MIDI note")
        
        self.id = midi_id
        self.drive = drive

        self.setTone(midi_note=midi_id)
    
    def setTone(self, * ,frequency:float = None, midi_note:int=None):
        if (frequency is not None):
            self.frequency = frequency
            self.drive.setFrequency(self.frequency)
            return
        
        if (midi_note is not None):
            self.frequency = MIDINoteHelper.MIDI2Freq(midi_note)
            self.drive.setFrequency(self.frequency)
            return
                
        raise ValueError("A frequency or a midi note must be given")

    def transpose(self,frequency:float):
        self.reset()      
        self.setTone(frequency=self.frequency+frequency)

    def reset(self):
        self.setTone(midi_note=self.id)

    def play(self):
        self.drive.enable = True
        self.drive.update()
    
    def stop(self):
        self.drive.enable = False
        self.drive.update()
    






bus = SMBus(1) # indicates /dev/ic2-1

# drives:list[FloppyDrive] = [FloppyDrive(i2c_bus=bus,address=i) for i in range(8,18)]


# notes:list[Note] = []

# for index, drive in enumerate(drives):
#     notes.append(Note(index+40, drive))



drive = FloppyDrive(i2c_bus=bus, address= 8)
note = Note(60, drive)




def modsin(time:int):
    return math.sin(8*math.pi*time)


try:

    startTime = time.time()

    while True:        
        note.transpose(modsin(time.time() - startTime))
        print(note.frequency)
        note.play()
        #time.sleep(0.005)

        


    
    

except KeyboardInterrupt as ki:
    print("Exited")
except Exception as e:
    print(e)
finally:
    drive.silence()