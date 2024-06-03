'''
Messages to handle
    Start/Stop/Reset? or does this handle songs?
        start -> 
        stop -> 
        reset -> clear all active notes, stop sounding, refresh config?
    Note messages
        'note_on' velocity > 0 -> note on
        'note_on' velocity = 0 -> note off
        'note_off' -> note off
    control_change
        1 -> modulation on/off (wave form control?)
        64 -> sustain (can we handle this?)
        71 -> Sound Controller 1 -> CRASH MODES? and spin
        72 -> control pitch bend range?
        120, 123 -> Mute all sounding notes drives (123 maintains sustain)
    pitchwheel 
        do the pitch bend
    Sysex messages
        LISTENING current channel 
            specific 
            all channels
        OUTPUT channel 
            specific 
            all channels
        OUTPUT Mode 
            Keyboard
            rollover
        LOOPBACK (do I do anything with the keyboard input?)
            On/off    
'''


