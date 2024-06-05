import mido
from FlopPiano.MIDI import MIDIParser
from FlopPiano.Conductor import Conductor

# in_q = Queue()
# stop = Event()

# def play(in_msgs_q)->None:
#     con = Conductor(driveAddresses=(8,9,10,11,12,13,14,15,16,17))
#     parser = MIDIParser(con)
#     while True:
#         if stop.is_set():
#             con.silence()
#             break

#         newMsgList:list[Message] = []
#         try:
#             newMsgList = in_msgs_q.get(block=False)
#             for msg in newMsgList:
#                 parser.parseMessage(msg)
#         except Empty:
#             pass
#         except Exception as e: 
#             print("Thread error", e)
#             raise e
#         finally:
#             out = con.conduct()
#             if len(out)>0: print(out)
     


# print(mido.get_input_names())
# test_midi_file =  'Testing_MIDI/Beethoven-Moonlight-Sonata.mid'
usb_interface = 'USB MIDI Interface:USB MIDI Interface MIDI 1 20:0'
# playerThread = Thread(target=play, daemon= True, args=(in_q,))
# playerThread.start()


conductor = Conductor(driveAddresses=(8,9,10,11,12,13,14,15,16,17))

parser = MIDIParser(conductor)




try:
    # for msg in mido.MidiFile(test_midi_file).play():
    #         in_q.put([msg],block=True)
    
    # in_q.put([Message('note_on', note =40, velocity = 1)])
    # time.sleep(1)
    # in_q.put([Message('control_change', control =70, value = 2)])
    # time.sleep(1)
 

    # while True:
    #     pass

    with mido.open_input(usb_interface) as inport:
        for msg in inport:
            parser.parse(msg)
            conductor.conduct()
            #in_q.put([msg],block=True)

except KeyboardInterrupt:
    print("Exiting..")
finally:
    conductor.silence()
    # stop.set()
    # playerThread.join() #wait for exit