from floppiano.synths import DriveSynth
from floppiano.midi import MIDIPlayer
import time
import logging




logging.basicConfig(level=logging.DEBUG)

transpose = -12
redirect = True

#test_midi_file = 'assets/MIDI/Beethoven-Moonlight-Sonata.mid'
test_midi_file = 'assets/MIDI/Sarias_Song_piano.mid'

synth = DriveSynth([i for i in range(8,18)])
synth.reset()
    

abs_time = time.time()

try:




    player = MIDIPlayer()
    player.play(test_midi_file, redirect= synth.input_channel, transpose=transpose)

    while player.playing:
        msg = player.update()
        if msg is not None:
            synth.parse([msg], 'midi_player')





except KeyboardInterrupt:
    print("Exiting..")
finally:
    synth.reset()
   







    # msg_index = 0
    # start_time = time.time()
    # next_time = 0.0

    # while True:
    #     elapsed_time = time.time() - start_time

    #     if elapsed_time > next_time:
    #         try:
    #             print(elapsed_time, next_time)
    #             synth.parse([messages[msg_index]])
    #             msg_index +=1    
    #             next_time += messages[msg_index].time          
    #         except IndexError:
    #             break


    #print(time.time()- abs_time)





# for msg in mid_file:
#     input_time += msg.time

#     playback_time = time.time() - start_time
#     duration_to_next_event = input_time - playback_time

#     if duration_to_next_event > 0.0:
#         time.sleep(duration_to_next_event)

#     if not isinstance(msg, MetaMessage):
#         print(msg)



