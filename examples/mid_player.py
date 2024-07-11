from floppiano.synths import DriveSynth
import mido
import logging
import time

transpose = -12
#test_midi_file = 'assets/Testing_MIDI/80_Synth_track.mid'
#test_midi_file = 'assets/Testing_MIDI/Backstreet_Boys_I Want_It_That_Way.mid'
#test_midi_file = 'assets/Testing_MIDI/Beethoven-Moonlight-Sonata.mid'
#test_midi_file = 'assets/Testing_MIDI/bloody.mid'
#test_midi_file = 'assets/Testing_MIDI/brahms-symphony3-3-theme-piano-solo.mid'
#test_midi_file = 'assets/Testing_MIDI/castle_deep.mid'
#test_midi_file = 'assets/Testing_MIDI/CrazyTrain.mid'
#test_midi_file = 'assets/Testing_MIDI/Cristina.mid'
#test_midi_file = 'assets/Testing_MIDI/Exodus.mid'
#test_midi_file = 'assets/Testing_MIDI/Finish_the_Fight.mid'
#test_midi_file = 'assets/Testing_MIDI/FNF_DubstepV2.mid'
#test_midi_file = 'assets/Testing_MIDI/gerudo.mid'
#test_midi_file = 'assets/Testing_MIDI/Happy_Birthday_MIDI.mid'
#test_midi_file = 'assets/Testing_MIDI/Hyrule_Castle_-_Zelda_A_Link_to_the_Past.mid'
#test_midi_file = 'assets/Testing_MIDI/imperial.mid'
#test_midi_file = 'assets/Testing_MIDI/knight_rider.mid'
#test_midi_file = 'assets/Testing_MIDI/level1.mid'
#test_midi_file = 'assets/Testing_MIDI/Liszt_La_Campanella.mid'
#test_midi_file = 'assets/Testing_MIDI/lostwoods.mid'
#test_midi_file = 'assets/Testing_MIDI/Mariage_Damour.mid'
#test_midi_file = 'assets/Testing_MIDI/metallica-one.mid'
#test_midi_file = 'assets/Testing_MIDI/phantom_of_the_floppera.mid'
#test_midi_file = 'assets/Testing_MIDI/phonk.mid'
#test_midi_file = 'assets/Testing_MIDI/Sarias_Song_piano.mid'
#test_midi_file = 'assets/Testing_MIDI/debussy-doctor-gradus-ad-parnassum.mid'
#test_midi_file = 'assets/Testing_MIDI/runescape_lumbridge_piano.mid'
test_midi_file = 'assets/Testing_MIDI/drunken-sailor.mid'
#test_midi_file = 'assets/Testing_MIDI/Sonata-c.mid'
#test_midi_file = 'assets/Testing_MIDI/super_mario_v2.mid'
#test_midi_file = 'assets/Testing_MIDI/super_mario.mid'
#test_midi_file = 'assets/Testing_MIDI/Super_Mario.mid'
#test_midi_file = 'assets/Testing_MIDI/synth_doodle.mid'
#test_midi_file = 'assets/Testing_MIDI/the_imperial_march.mid'
#test_midi_file = 'assets/Testing_MIDI/The-Entertainer.mid'
#test_midi_file = 'assets/Testing_MIDI/zelda_deep.mid'

#test_midi_file = 'assets/Testing_MIDI/jacob/bach-bourree-in-e-minor-guitar.mid'
#test_midi_file = 'assets/Testing_MIDI/jacob/CallOfKtulu.mid'
#test_midi_file = 'assets/Testing_MIDI/jacob/cs3-5bou.mid'
#test_midi_file = 'assets/Testing_MIDI/jacob/furelise.mid'
#test_midi_file = 'assets/Testing_MIDI/jacob/mario_overworld.mid'
#test_midi_file = 'assets/Testing_MIDI/jacob/tocatta_and_fuguge.mid'




logging.basicConfig(level=logging.DEBUG)


drive_addrs = [i for i in range(8,18)]

synth = DriveSynth(drive_addrs)
synth.bow  = False
#synth.polyphonic = False

print(f'Playing {test_midi_file} in 2 second [ctrl+c to stop]')

#time.sleep(2)

try:
    for msg in mido.MidiFile(test_midi_file).play():
        if (msg.type == "note_on" or msg.type =="note_off"):
            msg.note = msg.note + transpose
        
        synth.parse([msg])
except KeyboardInterrupt:
    print("Exiting..")
finally:
    synth.reset()
   
