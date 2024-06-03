from FlopPiano.FloppyDrives import FloppyDrive, FloppyDriveHandler
from FlopPiano.FloppyKeyboard import FlopKeyboard
from mido import Message
import time


def testAll(driveHandler:FloppyDriveHandler):
    print("Testing all drives sequentially...")
    time.sleep(1)
    for drive in driveHandler.drives:
        print(drive.address)
        drive.enable = True
        driveHandler.updateDrive(drive, justCTRL= False)
        time.sleep(0.5)
        drive.enable = False
        driveHandler.updateDrive(drive, justCTRL= False)
    print("Done.")

def timingTest(driveHandler:FloppyDriveHandler, keyboard:FlopKeyboard):
    totalTime = time.time()

    print ("Turning on all drives...")
    startTime = time.time()
    for drive in driveHandler.drives:
        drive.setFrequency(38.891)
        drive.enable = True
        driveHandler.updateDrive(drive)

    print("Time to turn on drives:",time.time()- startTime)

    print ("Waiting 1 second ...")
    time.sleep(1)

    print ("Turning off all drives...")
    startTime = time.time()
    for drive in driveHandler.drives:
        drive.enable = False
        driveHandler.updateDrive(drive)

    print("Time to turn off drives:",time.time()- startTime)   

    print ("Waiting 1 second ...")
    time.sleep(1)

    print ("Reading inputs...")
    startTime = time.time()
    keyboard.read()
    print("Time to get inputs:",time.time()- startTime)   

    print("Total Time:",(time.time()- totalTime)-2)   





available_drives:list[FloppyDrive] = []

for addr in range(8,18):
    available_drives.append(FloppyDrive(address=addr))


driveHandler = FloppyDriveHandler(available_drives)
keyboard = FlopKeyboard(i2c_bus=driveHandler.i2c_bus)

timingTest(driveHandler, keyboard)
#testAll(driveHandler)