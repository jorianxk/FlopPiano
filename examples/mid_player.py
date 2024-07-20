from floppiano.synths import DriveSynth
import mido
import logging
import time
from floppiano.midi import MIDIUtil

transpose = 0

#test_midi_file = 'assets/MIDI/Beethoven-Moonlight-Sonata.mid'
#test_midi_file = 'assets/MIDI/bloody.mid'
#test_midi_file = 'assets/MIDI/castle_deep.mid'
#test_midi_file = 'assets/MIDI/CrazyTrain.mid'
#test_midi_file = 'assets/MIDI/Cristina.mid'
#test_midi_file = 'assets/MIDI/drunken-sailor.mid'
#test_midi_file = 'assets/MIDI/gerudo.mid'
#test_midi_file = 'assets/MIDI/Happy_Birthday_MIDI.mid'
#test_midi_file = 'assets/MIDI/Hyrule_Castle_-_Zelda_A_Link_to_the_Past.mid'
test_midi_file = 'assets/MIDI/level1.mid'
#test_midi_file = 'assets/MIDI/metallica-one.mid'
#test_midi_file = 'assets/MIDI/Sarias_Song_piano.mid'
#test_midi_file = 'assets/MIDI/The-Entertainer.mid'
#test_midi_file = 'assets/MIDI/zelda_deep.mid'

#test_midi_file = 'assets/MIDI/jacob/bach-bourree-in-e-minor-guitar.mid'
#test_midi_file = 'assets/MIDI/jacob/CallOfKtulu.mid'
#test_midi_file = 'assets/MIDI/jacob/cs3-5bou.mid'
#test_midi_file = 'assets/MIDI/jacob/furelise.mid'
#test_midi_file = 'assets/MIDI/jacob/mario_overworld.mid'
#test_midi_file = 'assets/MIDI/jacob/tocatta_and_fuguge.mid'
#test_midi_file = 'assets/MIDI/jacob/AlsoSprachZ_long_withbass.mid'
#test_midi_file = 'assets/MIDI/jacob/AlsoSprachZ_long.mid'
#test_midi_file = 'assets/MIDI/jacob/AlsoSprachZ_short.mid'
#test_midi_file = 'assets/MIDI/jacob/CallOfKtulu_nodrums.mid'
#test_midi_file = 'assets/MIDI/jacob/mario_nopercussion.mid'



logging.basicConfig(level=logging.DEBUG)


drive_addrs = [i for i in range(8,18)]

synth = DriveSynth(drive_addrs)
#synth.bow  = True
#synth.polyphonic = False

print(f'Playing {test_midi_file} in 2 second [ctrl+c to stop]')

#time.sleep(2)

try:
    for msg in mido.MidiFile(test_midi_file).play():
        if MIDIUtil.hasChannel(msg):
            msg.channel = synth.input_channel

        if (msg.type == "note_on" or msg.type =="note_off"):
            msg.note = msg.note + transpose
        
        synth.parse([msg])
except KeyboardInterrupt:
    print("Exiting..")
finally:
    synth.reset()
   
