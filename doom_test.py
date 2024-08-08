import mido
from floppiano.synths import DriveSynth
from floppiano.midi import MIDIUtil
import logging
import time
transpose = 0


#logging.basicConfig(level=logging.DEBUG)



drive_addrs = [i for i in range(8,18)]

synth = DriveSynth(drive_addrs)

synth.reset()

synth.bow  = False

# time_out = time.time()



try:
    for msg in mido.open_input('doom_test', virtual=True):
        if MIDIUtil.hasChannel(msg):
            msg.channel = synth.input_channel
        


        if (msg.type == "note_on" or msg.type =="note_off"):
            msg.note = msg.note + transpose
        
        print(msg)
        if msg.type == 'control_change' and msg.control ==123:
            synth.reset()
        else:
            synth.parse([msg])
except KeyboardInterrupt:
    print("Exiting..")
finally:
    synth.reset()