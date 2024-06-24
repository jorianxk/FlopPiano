from jidi.voices import DriveVoice
from jidi.synths import DriveSynth
import mido
import logging




usb_interface = None
for input in mido.get_input_names():
     if input.startswith("USB"):
          usb_interface = input
          break

if usb_interface is None: raise Exception("Could not find MIDI USB Interface!")


logging.basicConfig(level=logging.DEBUG)


voices = [DriveVoice(i) for i in range(8,18)]


synth = DriveSynth(voices)

print(synth.pitch_bend_range)
print("Begin Playing! [ctrl+c to exit]")

try:
    with mido.open_input(usb_interface) as inport:
            for msg in inport:
                synth.update([msg])
except KeyboardInterrupt:
    print("Exiting..")
finally:
    synth.reset()



