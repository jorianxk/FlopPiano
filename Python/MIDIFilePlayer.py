from FlopPiano.MIDI import MIDIParser
from FlopPiano.Conductor import Conductor
import mido
import logging
import time

transpose = 0
#test_midi_file = 'Testing_MIDI/80_Synth_track.mid'
#test_midi_file = 'Testing_MIDI/Backstreet_Boys_I Want_It_That_Way.mid'
test_midi_file =  'Testing_MIDI/Beethoven-Moonlight-Sonata.mid'
#test_midi_file = 'Testing_MIDI/bloody.mid'
#test_midi_file = 'Testing_MIDI/brahms-symphony3-3-theme-piano-solo.mid'
#test_midi_file = 'Testing_MIDI/castle_deep.mid'
#test_midi_file = 'Testing_MIDI/CrazyTrain.mid'
#test_midi_file = 'Testing_MIDI/Cristina.mid'
#test_midi_file = 'Testing_MIDI/Exodus.mid'
#test_midi_file = 'Testing_MIDI/Finish_the_Fight.mid'
#test_midi_file = 'Testing_MIDI/FNF_DubstepV2.mid'
#test_midi_file = 'Testing_MIDI/gerudo.mid'
#test_midi_file = 'Testing_MIDI/Happy Birthday_Black.mid'
#test_midi_file = 'Testing_MIDI/Happy_Birthday_MIDI.mid'
#test_midi_file = 'Testing_MIDI/Happy_Birthday.mid'
#test_midi_file = 'Testing_MIDI/HappyBirthday.mid'
#test_midi_file = 'Testing_MIDI/Hyrule_Castle_-_Zelda_A_Link_to_the_Past.mid'
#test_midi_file = 'Testing_MIDI/imperial.mid'
#test_midi_file = 'Testing_MIDI/knight_rider.mid'
#test_midi_file = 'Testing_MIDI/level1.mid'
#test_midi_file = 'Testing_MIDI/Liszt_La_Campanella.mid'
#test_midi_file = 'Testing_MIDI/lostwoods.mid'
#test_midi_file = 'Testing_MIDI/Mariage_Damour.mid'
#test_midi_file = 'Testing_MIDI/metallica-one.mid'
#test_midi_file = 'Testing_MIDI/phantom_of_the_floppera.mid'
#test_midi_file = 'Testing_MIDI/phonk.mid'
#test_midi_file = 'Testing_MIDI/Sarias_Song_piano.mid'
#test_midi_file = 'Testing_MIDI/debussy-doctor-gradus-ad-parnassum.mid'
#test_midi_file = 'Testing_MIDI/runescape_lumbridge_piano.mid'
#test_midi_file = 'Testing_MIDI/drunken-sailor.mid'
#test_midi_file = 'Testing_MIDI/Sonata-c.mid'
#est_midi_file = 'Testing_MIDI/super_mario_v2.mid'
#test_midi_file = 'Testing_MIDI/super_mario.mid'
#test_midi_file = 'Testing_MIDI/Super_Mario.mid'
#test_midi_file = 'Testing_MIDI/synth_doodle.mid'
#test_midi_file = 'Testing_MIDI/the_imperial_march.mid'
#test_midi_file = 'Testing_MIDI/The-Entertainer.mid'
#test_midi_file = 'Testing_MIDI/zelda_deep.mid'

#test_midi_file = 'Testing_MIDI/jacob/bach-bourree-in-e-minor-guitar.mid'
#test_midi_file = 'Testing_MIDI/jacob/CallOfKtulu.mid'
#test_midi_file = 'Testing_MIDI/jacob/cs3-5bou.mid'
#test_midi_file = 'Testing_MIDI/jacob/furelise.mid'
#test_midi_file = 'Testing_MIDI/jacob/mario_overworld.mid'
#test_midi_file = 'Testing_MIDI/jacob/tocatta_and_fuguge.mid'




logging.basicConfig(level=logging.DEBUG)


conductor = Conductor(loopback=False, doKeyboard=False)

print(f'Playing {test_midi_file} in 3 second [ctrl+c to stop]')

time.sleep(3)

try:
    for msg in mido.MidiFile(test_midi_file).play():
        if (msg.type == "note_on" or msg.type =="note_off"):
            msg.note = msg.note + transpose
        
        conductor.conduct([msg])
except KeyboardInterrupt:
    print("Exiting..")
finally:
    conductor.silence()
   
