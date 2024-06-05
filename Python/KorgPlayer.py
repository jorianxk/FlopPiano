from FlopPiano.MIDI import MIDIParser
from FlopPiano.Conductor import Conductor
import mido




usb_interface = None
for input in mido.get_input_names():
     if input.startswith("USB"):
          usb_interface = input
          break

if usb_interface is None: raise Exception("Could not find MIDI USB Interface!")

print("Begin Playing! [ctrl+c to exit]")


conductor = Conductor((8, 9, 10 ,11, 12, 13, 14, 15, 16, 17))
parser = MIDIParser(conductor)

transpose = 0

try:
    with mido.open_input(usb_interface) as inport:
            for msg in inport:
                parser.parse(msg)
                conductor.conduct()
except KeyboardInterrupt:
    print("Exiting..")
finally:
    conductor.silence()



