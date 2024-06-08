from FlopPiano.Conductor import Conductor, OutputMode

from threading import Thread, Event
from queue import Queue, Empty


from mido.ports import BaseInput, BaseOutput
from mido import Message
import logging
import time
import mido


def doConduct(stop_flag:Event, input_q:Queue):
    usb_in_interface = None
    for input in mido.get_input_names():
        if input.startswith("USB"):
            usb_in_interface = input
            break
    usb_out_interface = None
    for input in mido.get_output_names():
        if input.startswith("USB"):
            usb_out_interface = input
            break
    if (usb_in_interface is None or usb_out_interface is None):
        raise ValueError("Could not find any usb interfaces!")
    
    usbInPort:BaseInput = mido.open_input(usb_in_interface)
    usbOutPort:BaseOutput = mido.open_output(usb_out_interface)


    conductor = Conductor(loopback=False)
    
    while True:
        if (stop_flag.is_set()): break

        incoming_msgs:list[Message] = []
        outgoing_msgs:list[Message] = []

        try: incoming_msgs.extend(input_q.get_nowait())
        except Empty: pass

        if(not usbInPort.closed):
            usbIn_msg = usbInPort.receive(block=False)
            if usbIn_msg is not None:
                incoming_msgs.append(usbIn_msg)

        outgoing_msgs = conductor.conduct(incoming_msgs)



        if (not usbOutPort.closed and len(outgoing_msgs)>0):
            for msg in outgoing_msgs:
                usbOutPort.send(msg)

    conductor.silence()

    


#test_midi_file = 'Testing_MIDI/Hyrule_Castle_-_Zelda_A_Link_to_the_Past.mid'
#test_midi_file = 'Testing_MIDI/bloody.mid'
#test_midi_file = 'Testing_MIDI/imperial.mid'
#test_midi_file = 'Testing_MIDI/level1.mid'
#test_midi_file = 'Testing_MIDI/Sarias_Song_piano.mid'
test_midi_file = 'Testing_MIDI/CrazyTrain.mid'
transpose = -12



logging.basicConfig(level=logging.DEBUG)
stop_flag = Event()
input_q = Queue()
conductThread = Thread(target=doConduct, daemon= True, args=(stop_flag, input_q))
conductThread.start()

try:    

    # for msg in mido.MidiFile(test_midi_file).play():
    #     if (msg.type == "note_on" or msg.type =="note_off"):
    #         msg.note = msg.note + transpose
    #     input_q.put([msg])
    # input_q.put([Message('control_change', control = 120)])

    while True: 
        time.sleep(1)

except KeyboardInterrupt as ke:
    print("Exiting..")
finally:
    stop_flag.set()
    conductThread.join()
    print("Done.")
