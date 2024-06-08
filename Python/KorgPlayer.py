from FlopPiano.MIDI import MIDIParser
from FlopPiano.Conductor import *
import mido
import logging




usb_interface = None
for input in mido.get_input_names():
     if input.startswith("USB"):
          usb_interface = input
          break

if usb_interface is None: raise Exception("Could not find MIDI USB Interface!")


logging.basicConfig(level=logging.DEBUG)

conductor = Conductor(loopback=False, doKeyboard=False)

transpose = 0

print("Begin Playing! [ctrl+c to exit]")

try:
    with mido.open_input(usb_interface) as inport:
            for msg in inport:
                conductor.conduct([msg])
except KeyboardInterrupt:
    print("Exiting..")
finally:
    conductor.silence()



