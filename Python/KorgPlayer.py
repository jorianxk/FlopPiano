from FlopPiano.MIDI import MIDIParser
from FlopPiano.Conductor import *
import mido




usb_interface = None
for input in mido.get_input_names():
     if input.startswith("USB"):
          usb_interface = input
          break

if usb_interface is None: raise Exception("Could not find MIDI USB Interface!")

print("Begin Playing! [ctrl+c to exit]")


conductor = Conductor(loopback=False)

transpose = 0

try:
    with mido.open_input(usb_interface) as inport:
            for msg in inport:
                conductor.conduct([msg])
except KeyboardInterrupt:
    print("Exiting..")
finally:
    conductor.silence()



