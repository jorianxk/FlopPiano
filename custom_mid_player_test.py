import mido
from mido import MetaMessage, Message
from floppiano.midi import MIDIUtil

import time
# self.add_effect(
# PopUpDialog(self.app.screen, 'Polyphony changing is not yet supported', ["OK"]))


transpose = 0
redirect = True

test_midi_file = 'assets/MIDI/level1.mid'
mid_file = mido.MidiFile(test_midi_file)



messages:list[Message] = []

for msg in mid_file:
    if not isinstance(msg, MetaMessage):
        if redirect and MIDIUtil.hasChannel(msg):
            msg.channel = 0 #TODO: redirect to synth channel
       
        if (msg.type == "note_on" or msg.type =="note_off"):
            msg.note = msg.note + transpose
        
        messages.append(msg)


    
start_time = time.time()
input_time = 0.0

msg_index = 0

while True:
    if msg_index > len(messages) -1: break
    playback_time = time.time() - start_time
    duration_to_next_event = input_time - playback_time

    if duration_to_next_event <= 0.0:
        msg = messages[msg_index]
        input_time += msg.time
        # TODO play the message
        print(msg)
        msg_index +=1







# for msg in mid_file:
#     input_time += msg.time

#     playback_time = time.time() - start_time
#     duration_to_next_event = input_time - playback_time

#     if duration_to_next_event > 0.0:
#         time.sleep(duration_to_next_event)

#     if not isinstance(msg, MetaMessage):
#         print(msg)
