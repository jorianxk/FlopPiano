import mido
from FlopPiano.MIDI import MIDIParser
from FlopPiano.Conductor import *

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

# playerThread = Thread(target=play, daemon= True, args=(in_q,))
# playerThread.start()


logging.basicConfig(level=logging.INFO)

conductor = Conductor(loopback=False)
korg_or_file = False #True = Korg, False = Play a midi file


test_midi_file = 'Testing_MIDI/Sarias_Song_piano.mid'
#test_midi_file = 'Testing_MIDI/Hyrule_Castle_-_Zelda_A_Link_to_the_Past.mid'
#test_midi_file =  'Testing_MIDI/Beethoven-Moonlight-Sonata.mid'
#test_midi_file = 'Testing_MIDI/Backstreet_Boys_I Want_It_That_Way.mid'
#test_midi_file = 'Testing_MIDI/the_imperial_march.mid'
transpose = -12


#injections:list[Message] =[Message('sysex', data = [123,1,15])] 



def korg(conductor:Conductor)->None:
    #get the USB midi interface
    usb_interface = None
    for input in mido.get_input_names():
        if input.startswith("USB"):
            usb_interface = input
            break
    
    #We could not find the interface - Exit
    if usb_interface is None: raise Exception("Could not find MIDI USB Interface!")
    print("Begin Playing! [ctrl+c to exit]")

    #Handle playing
    with mido.open_input(usb_interface) as inport:
        for msg in inport:
            output = conductor.conduct([msg])
            # for out_msg in output:
            #         print("Response:",out_msg)

def midi_file(conductor:Conductor, file2play:str, transpose:int = 0)->None:
    print(f'Playing {file2play}...')
    for msg in mido.MidiFile(file2play).play():
        if (msg.type == "note_on" or msg.type =="note_off"):
            msg.note = msg.note + transpose
        
        output = conductor.conduct([msg])

        # for out_msg in output:
        #     print("Response:", out_msg)





try:
    #  responses = conductor.conduct(injections)
    #  for resp in responses:
    #      print("Response:",resp)

    #  responses = conductor.conduct([])
    #  for resp in responses:
    #      print("Response:",resp)

    #  exit(0)     
     if (korg_or_file):korg(conductor)
     else: midi_file(conductor,test_midi_file,transpose)
except KeyboardInterrupt:
    print("Exiting..")
finally:
    conductor.silence()
    print("Done.")







