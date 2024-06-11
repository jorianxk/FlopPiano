from floppiano.conductor import Conductor, PitchBendMode, OutputMode
from floppiano.devices import CrashMode
from mido import Message
from time import sleep, time
import logging


def notes_polyphony(c:Conductor, l:logging.Logger)->bool:
    #Test Note on/off and polyphony
    l.info("notes_polyphony---------------------------------------------------")

    note_off_velocity = Message('note_off', note=69, velocity = 0)

    #Turn on notes
    for i in range(0, len(c._notes)):
        c.conduct([Message('note_on', note=69+i, velocity = 1)])
        sleep(0.25)

    #Turn on one more note
    #we should have one message now
    overflow_msg = Message('note_on', note=27, velocity = 1)
    out = c.conduct([overflow_msg])

    #Turn off notes
    for i in range(0, len(c._notes)):
        c.conduct([Message('note_on', note=69+i, velocity = 0)])
        sleep(0.25)
    
    passed = True

    if len(out)!=1:
        passed = False
        l.warning("notes_polyphony: more than one overflow")

    if out[0]!=overflow_msg:
        passed = False 
        l.warning("notes_polyphony: overflow note note the one sent")
    
    if len(c.active_notes) >0:
        passed = False 
        l.warning("notes_polyphony: All drives not off")

    if passed:
        l.info("notes_polyphony:------------------------------------------------PASS")
    else:
        l.info("notes_polyphony:------------------------------------------------FAIL")

    c.silence()
    return passed

def pitch_bend(c:Conductor, l:logging.Logger)->bool:
    l.info("pitch_bend--------------------------------------------------------")
    c.conduct([Message('note_on', note=69, velocity = 1)])

    #-8192, 8192
    for index, mode in enumerate(PitchBendMode):
        c.conduct([Message('control_change', control =71, value = index)])

        sleep(0.25)
        c.conduct([Message('pitchwheel', pitch = 0)])
        sleep(0.25)
        c.conduct([Message('pitchwheel', pitch = -8192)])
        sleep(0.25)
        c.conduct([Message('pitchwheel', pitch = 0)])
        sleep(0.25)
        c.conduct([Message('pitchwheel', pitch = 8191)])

    c.conduct([Message('control_change', control =71, value = 0)])
    c.conduct([Message('note_off', note=69, velocity = 1)])
    l.info("pitch_bend:---------------------------------------------------------PASS")
    c.silence()
    return True

def modulate(c:Conductor, l:logging)->bool:
    l.info("modulate----------------------------------------------------------")
    c.conduct([Message('note_on', note=69, velocity = 1)])
    
    for i in range(1,128):
        c.conduct([Message('control_change', control =1, value = i)])
        start = time()
        while time()-start < 0.08:
            c.conduct()

    c.conduct([Message('control_change', control =1, value = 0)])
    c.conduct([Message('note_off', note=69, velocity = 1)])
    l.info("modulate:-----------------------------------------------------------PASS")
    c.silence()
    return True

def crash_modes(c:Conductor, l:logging)->bool:
    l.info("crash_modes----------------------------------------------------------")
    c.conduct([Message('note_on', note=69, velocity = 1)])

    for index, mode in enumerate(CrashMode):
        c.conduct([Message('control_change', control =70, value = index)])
        sleep(2)

    c.conduct([Message('control_change', control =70, value = 2)])
    c.conduct([Message('note_off', note=69, velocity = 1)])
    l.info("crash_modes:--------------------------------------------------------PASS")
    c.silence()
    return True

def silence(c:Conductor, l:logging)->bool:
    l.info("silence-----------------------------------------------------------")
    c.conduct([Message('note_on', note=69, velocity = 1)])
    sleep(0.5)
    c.conduct([Message('control_change', control =120, value = 0)])
    sleep(0.5)
    c.conduct([Message('note_on', note=69, velocity = 1)])
    sleep(0.5)
    c.conduct([Message('control_change', control =123, value = 0)])
    l.info("silence:------------------------------------------------------------PASS")
    return True

def input_channel(c:Conductor, l:logging)->bool:
    l.info("input_channel-----------------------------------------------------")
    passed = True
    for i in range(0,17):
        input_channel_msg = Message('sysex', data=[123,0,i])
        out = c.conduct([input_channel_msg])
        if len(out)!=1:
            passed = False
            l.warning("input_channel: more than echo")
        if out[0]!=input_channel_msg:
            passed = False 
            l.warning("input_channel: wrong echo")
    
    #check ignore
    input_channel_msg = Message('sysex', data=[123,0,30])
    out = c.conduct([input_channel_msg])
    if len(out)!=1:
        passed = False
        l.warning("input_channel: more than echo on ignore")
    if out[0]!=input_channel_msg:
        passed = False 
        l.warning("input_channel: wrong echo on ignore")

    #set back to all
    input_channel_msg = Message('sysex', data=[123,0,0])
    out = c.conduct([input_channel_msg])
    if passed:
        l.info("input_channel:--------------------------------------------------PASS")
    else:
        l.info("input_channel:--------------------------------------------------FAIL")

    return passed

def output_channel(c:Conductor, l:logging)->bool:
    l.info("output_channel----------------------------------------------------")
    passed = True
    for i in range(0,16):
        output_channel_msg = Message('sysex', data=[123,1,i])
        out = c.conduct([output_channel_msg])
        if len(out)!=1:
            passed = False
            l.warning("output_channel: more than echo")
        if out[0]!=output_channel_msg:
            passed = False 
            l.warning("output_channel: wrong echo")
    
    #check ignore
    output_channel_msg = Message('sysex', data=[123,1,30])
    out = c.conduct([output_channel_msg])
    if len(out)!=1:
        passed = False
        l.warning("output_channel: more than echo on ignore")
    if out[0]!=output_channel_msg:
        passed = False 
        l.warning("output_channel: wrong echo on ignore")
    


    #set back to 0
    output_channel_msg = Message('sysex', data=[123,1,0])
    out = c.conduct([output_channel_msg])
    if passed:
        l.info("output_channel:-------------------------------------------------PASS")
    else:
        l.info("output_channel:-------------------------------------------------FAIL")

    return passed

def output_mode(c:Conductor, l:logging)->bool:
    l.info("output_mode-------------------------------------------------------")

    for index, mode in enumerate(OutputMode):
        output_mode_msg = Message('sysex', data=[123,2,index])
        out = c.conduct([output_mode_msg])
    
    #check ignore
    output_mode_msg = Message('sysex', data=[123,2,30])
    out = c.conduct([output_mode_msg])

    
    #set back to rollover
    output_mode_msg = Message('sysex', data=[123,2,0])
    out = c.conduct([output_mode_msg])

    l.info("output_mode:--------------------------------------------------------PASS")

    return True

def loopback(c:Conductor, l:logging)->bool:
    l.info("loopback----------------------------------------------------------")

    loopback_msg = Message('sysex', data=[123,3,1])
    out = c.conduct([loopback_msg])
    sleep(1)

    loopback_msg = Message('sysex', data=[123,3,0])
    out = c.conduct([loopback_msg])
    sleep(1)
    l.info("loopback:-----------------------------------------------------------PASS")
    return True



logging.basicConfig(level=logging.INFO)

l = logging.getLogger(__name__)
c = Conductor(loopback=False)

try:
    notes_polyphony(c,l)
    sleep(0.5)
    pitch_bend(c,l)
    sleep(0.5)
    modulate(c,l)
    sleep(0.5)
    crash_modes(c,l)
    sleep(0.5)
    silence(c,l)
    sleep(0.5)
    input_channel(c,l)
    sleep(0.5)
    output_channel(c,l)
    sleep(0.5)
    output_mode(c,l)
    sleep(0.5)
    loopback(c,l)
except KeyboardInterrupt as ke:
    print("Exiting...")
finally:
    c.silence()
    print("Done.")