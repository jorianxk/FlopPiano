import mido
from mido import Message
from mido.sockets import PortServer, SocketPort, connect



test_midi_file =  'Testing_MIDI/Beethoven-Moonlight-Sonata.mid'

output = connect('localhost', 8080)

for msg in mido.MidiFile(test_midi_file).play():
    output.send(msg)

output.close()