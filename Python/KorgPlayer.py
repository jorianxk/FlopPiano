from FlopPiano.FloppyDrives import *
from FlopPiano.MIDI import MessageParser
import mido


print(mido.get_input_names())

bow = False

available_drives:list[FloppyDrive] = []

for addr in range(8,18):
    if bow:
        available_drives.append(FloppyDrive(address=addr,
                                            crash_mode=CrashMode.BOW))
    else:
        available_drives.append(FloppyDrive(address=addr))

player = FloppyDrivePlayer(available_drives)
msgParser = MessageParser(player)



try:
    with mido.open_input('USB MIDI Interface:USB MIDI Interface MIDI 1 20:0') as inport:
            for msg in inport:
                msgParser.parseMessage(msg)
except KeyboardInterrupt:
    print("Exiting..")
except Exception as e:
    print(e)
finally:
    player.silenceDrives()

