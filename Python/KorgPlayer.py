from FlopPiano import FloppyDrive
from smbus import SMBus
import mido
import time




midi_file = "Testing_MIDI/Beethoven-Moonlight-Sonata.mid"

#print(mido.get_output_names())




i2c_bus = SMBus(1) ## indicates /dev/ic2-1



MIDI_LOOK_UP = {
                0:{"freq":8.176,"name":""},
                1:{"freq":8.662,"name":""},
                2:{"freq":9.177,"name":""},
                3:{"freq":9.723,"name":""},
                4:{"freq":10.301,"name":""},
                5:{"freq":10.913,"name":""},
                6:{"freq":11.562,"name":""},
                7:{"freq":12.25,"name":""},
                8:{"freq":12.978,"name":""},
                9:{"freq":13.75,"name":""},
                10:{"freq":14.568,"name":""},
                11:{"freq":15.434,"name":""},
                12:{"freq":16.352,"name":""},
                13:{"freq":17.324,"name":""},
                14:{"freq":18.354,"name":""},
                15:{"freq":19.445,"name":""},
                16:{"freq":20.602,"name":""},
                17:{"freq":21.827,"name":""},
                18:{"freq":23.125,"name":""},
                19:{"freq":24.5,"name":""},
                20:{"freq":25.957,"name":""},
                21:{"freq":27.5,"name":"A0"},
                22:{"freq":29.135,"name":"A#0/Bb0"},
                23:{"freq":30.868,"name":"B0"},
                24:{"freq":32.703,"name":"C1"},
                25:{"freq":34.648,"name":"C#1/Db1"},
                26:{"freq":36.708,"name":"D1"},
                27:{"freq":38.891,"name":"D#1/Eb1"},
                28:{"freq":41.203,"name":"E1"},
                29:{"freq":43.654,"name":"F1"},
                30:{"freq":46.249,"name":"F#1/Gb1"},
                31:{"freq":48.999,"name":"G1"},
                32:{"freq":51.913,"name":"G#1/Ab1"},
                33:{"freq":55,"name":"A1"},
                34:{"freq":58.27,"name":"A#1/Bb1"},
                35:{"freq":61.735,"name":"B1"},
                36:{"freq":65.406,"name":"C2"},
                37:{"freq":69.296,"name":"C#2/Db2"},
                38:{"freq":73.416,"name":"D2"},
                39:{"freq":77.782,"name":"D#2/Eb2"},
                40:{"freq":82.407,"name":"E2"},
                41:{"freq":87.307,"name":"F2"},
                42:{"freq":92.499,"name":"F#2/Gb2"},
                43:{"freq":97.999,"name":"G2"},
                44:{"freq":103.826,"name":"G#2/Ab2"},
                45:{"freq":110,"name":"A2"},
                46:{"freq":116.541,"name":"A#2/Bb2"},
                47:{"freq":123.471,"name":"B2"},
                48:{"freq":130.813,"name":"C3"},
                49:{"freq":138.591,"name":"C#3/Db3"},
                50:{"freq":146.832,"name":"D3"},
                51:{"freq":155.563,"name":"D#3/Eb3"},
                52:{"freq":164.814,"name":"E3"},
                53:{"freq":174.614,"name":"F3"},
                54:{"freq":184.997,"name":"F#3/Gb3"},
                55:{"freq":195.998,"name":"G3"},
                56:{"freq":207.652,"name":"G#3/Ab3"},
                57:{"freq":220,"name":"A3"},
                58:{"freq":233.082,"name":"A#3/Bb3"},
                59:{"freq":246.942,"name":"B3"},
                60:{"freq":261.626,"name":"C4 (middle C)"},
                61:{"freq":277.183,"name":"C#4/Db4"},
                62:{"freq":293.665,"name":"D4"},
                63:{"freq":311.127,"name":"D#4/Eb4"},
                64:{"freq":329.628,"name":"E4"},
                65:{"freq":349.228,"name":"F4"},
                66:{"freq":369.994,"name":"F#4/Gb4"},
                67:{"freq":391.995,"name":"G4"},
                68:{"freq":415.305,"name":"G#4/Ab4"},
                69:{"freq":440,"name":"A4 concert pitch"},
                70:{"freq":466.164,"name":"A#4/Bb4"},
                71:{"freq":493.883,"name":"B4"},
                72:{"freq":523.251,"name":"C5"},
                73:{"freq":554.365,"name":"C#5/Db5"},
                74:{"freq":587.33,"name":"D5"},
                75:{"freq":622.254,"name":"D#5/Eb5"},
                76:{"freq":659.255,"name":"E5"},
                77:{"freq":698.456,"name":"F5"},
                78:{"freq":739.989,"name":"F#5/Gb5"},
                79:{"freq":783.991,"name":"G5"},
                80:{"freq":830.609,"name":"G#5/Ab5"},
                81:{"freq":880,"name":"A5"},
                82:{"freq":932.328,"name":"A#5/Bb5"},
                83:{"freq":987.767,"name":"B5"},
                84:{"freq":1046.502,"name":"C6"},
                85:{"freq":1108.731,"name":"C#6/Db6"},
                86:{"freq":1174.659,"name":"D6"},
                87:{"freq":1244.508,"name":"D#6/Eb6"},
                88:{"freq":1318.51,"name":"E6"},
                89:{"freq":1396.913,"name":"F6"},
                90:{"freq":1479.978,"name":"F#6/Gb6"},
                91:{"freq":1567.982,"name":"G6"},
                92:{"freq":1661.219,"name":"G#6/Ab6"},
                93:{"freq":1760,"name":"A6"},
                94:{"freq":1864.655,"name":"A#6/Bb6"},
                95:{"freq":1975.533,"name":"B6"},
                96:{"freq":2093.005,"name":"C7"},
                97:{"freq":2217.461,"name":"C#7/Db7"},
                98:{"freq":2349.318,"name":"D7"},
                99:{"freq":2489.016,"name":"D#7/Eb7"},
                100:{"freq":2637.02,"name":"E7"},
                101:{"freq":2793.826,"name":"F7"},
                102:{"freq":2959.955,"name":"F#7/Gb7"},
                103:{"freq":3135.963,"name":"G7"},
                104:{"freq":3322.438,"name":"G#7/Ab7"},
                105:{"freq":3520,"name":"A7"},
                106:{"freq":3729.31,"name":"A#7/Bb7"},
                107:{"freq":3951.066,"name":"B7"},
                108:{"freq":4186.009,"name":"C8"},
                109:{"freq":4434.922,"name":"C#8/Db8"},
                110:{"freq":4698.636,"name":"D8"},
                111:{"freq":4978.032,"name":"D#8/Eb8"},
                112:{"freq":5274.041,"name":"E8"},
                113:{"freq":5587.652,"name":"F8"},
                114:{"freq":5919.911,"name":"F#8/Gb8"},
                115:{"freq":6271.927,"name":"G8"},
                116:{"freq":6644.875,"name":"G#8/Ab8"},
                117:{"freq":7040,"name":"A8"},
                118:{"freq":7458.62,"name":"A#8/Bb8"},
                119:{"freq":7902.133,"name":"B8"},
                120:{"freq":8372.018,"name":"C9"},
                121:{"freq":8869.844,"name":"C#9/Db9"},
                122:{"freq":9397.273,"name":"D9"},
                123:{"freq":9956.063,"name":"D#9/Eb9"},
                124:{"freq":10548.082,"name":"E9"},
                125:{"freq":11175.303,"name":"F9"},
                126:{"freq":11839.822,"name":"F#9/Gb9"},
                127:{"freq":12543.854,"name":"G9"}
                }




#TODO: update docstring
def send(bus:SMBus,drive:FloppyDrive, justCTRL:bool=True)->None:
    """
    A function to send all set CTRL Register values and TOP values a slave 
    drive, or to broadcast to the bus

    see code firmware and send(self, address:int=None, justCTRL:bool=True)
    Comments for details

    parameters: 
        address:int optional. if none the data is sent bus wide (broadcast)
            to all devices on the bus (address 0x0)
        justCTRL:bool optiona. if true, just the CTRL register is sent
            if false, CTRL plus the TOP value is sent to the address

    raises: 
        Idk some error: If the I2C bus cant sent the message for whatever
        reason          
    """

    # |------------------------------------------------------------------|
    # |                   The 'FIRST Byte' - CTRL byte                   |
    # |------------------------------------------------------------------|
    # |   0000   |     0      |       0      |      0     |      0       |
    # |----------|------------|--------------|---------------------------|
    # | Not used | Crash Mode |  Crash Mode  | Drive Spin | Drive Enable |
    # |------------------------------------------------------------------| 
    # 
    #  Crash mode - the two crash mode bits represent which crash mode the
    #  drive will use. Two bit combined give four possible states:
    #    MSB LSB
    #     0   0  - Crash prevention OFF
    #     0   1  - Crash prevention ON (BOW Mode)
    #     1   0  - Crash prevention ON (FLIP Mode)
    #     1   1  - Not used (results in crash prevention mode off if set)
    #     
    #     BOW mode: The drive will step until end of travel then flip
    #     direction (like a violin bow changing direction at the end of a
    #     bow stroke)
    #     
    #     FLIP mode: THe drive will flip direction after every step/pulse
    #  
    #  Drive Spin - if the bit is 1, the SPIN_PIN is pulled HIGH. 0 
    #  SPIN_PIN is pulled LOW. This is to turn on/off disc spin.
    #  
    #  Drive Enable - if the bit is high then the drive select/enable 
    #  (ENABLE_PIN) pin is pulled LOW (because the drives are active low) 
    #  and the drive is selected/enabled. If 0, then then the ENABLE_PIN
    #  is pulled HIGH and the drive is de-selected/disabled.

    #Prepare the CTRL Register 
    CTRL = (drive.crash_mode.value << 2)     
    CTRL = CTRL | (drive.spin << 1)
    CTRL = CTRL | (drive.enable)

    #print("{:08b}".format(CTRL), CTRL)

    #|----------------------------------------------------------------|
    #|            The second and third bytes - TOP Value              |
    #|----------------------------------------------------------------|
    #|  The second byte is the most significant byte of the TOP value |
    #|  The third byte is the least significant byte of the TOP value |
    #|----------------------------------------------------------------|

    TOP = drive.top.to_bytes(2,'little')

    
    ########################################################################
    #                  Write the values to the address                     #
    ########################################################################



    # #are we just senting the CTRL register?
    if(justCTRL):
        bus.write_block_data(drive.address, CTRL, [])
    else:
        bus.write_block_data(drive.address, CTRL, [TOP[1], TOP[0]])
def kill_all():
    kill_list =[FloppyDrive(address= 8),
                FloppyDrive(address= 9),
                FloppyDrive(address= 10),
                FloppyDrive(address= 11),
                FloppyDrive(address= 12),
                FloppyDrive(address= 13),
                FloppyDrive(address= 14),
                FloppyDrive(address= 15),
                FloppyDrive(address= 16),
                FloppyDrive(address= 17)]

    for drive in kill_list:
        drive.enable = False
        print(drive)
        send(i2c_bus, drive, justCTRL=True)




bow = False
availible_drives =[]
active_notes = dict()



print(mido.get_input_names())


if (bow):

    availible_drives =[FloppyDrive(address= 8, crash_mode=FloppyDrive.CrashMode.BOW),
                    FloppyDrive(address= 9, crash_mode=FloppyDrive.CrashMode.BOW),
                    FloppyDrive(address= 10, crash_mode=FloppyDrive.CrashMode.BOW),
                    FloppyDrive(address= 11, crash_mode=FloppyDrive.CrashMode.BOW),
                    FloppyDrive(address= 12, crash_mode=FloppyDrive.CrashMode.BOW),
                    FloppyDrive(address= 13, crash_mode=FloppyDrive.CrashMode.BOW),
                    FloppyDrive(address= 14, crash_mode=FloppyDrive.CrashMode.BOW),
                    FloppyDrive(address= 15, crash_mode=FloppyDrive.CrashMode.BOW),
                    FloppyDrive(address= 16, crash_mode=FloppyDrive.CrashMode.BOW),
                    FloppyDrive(address= 17, crash_mode=FloppyDrive.CrashMode.BOW)]
else:

    availible_drives =[FloppyDrive(address= 8),
                        FloppyDrive(address= 9),
                        FloppyDrive(address= 10),
                        FloppyDrive(address= 11),
                        FloppyDrive(address= 12),
                        FloppyDrive(address= 13),
                        FloppyDrive(address= 14),
                        FloppyDrive(address= 15),
                        FloppyDrive(address= 16),
                        FloppyDrive(address= 17)]


def main():
    with mido.open_input('USB MIDI Interface:USB MIDI Interface MIDI 1 20:0') as inport:
        for msg in inport:
                if (msg.type == 'note_on' or msg.type == 'note_off'):
                    
                    #Make sure we only play notes that are possible
                    #allowable range is midi# 7 - 127
                    if(not (msg.note <27 or msg.note>127)):

                        #print(msg)
                        if ((msg.type == 'note_off') or (msg.velocity == 0)):
                            #handle note off
                            #note_on velocity 0 is the same as note off
                            #print('Found note off',msg.note ,MIDI_LOOK_UP[msg.note])
                            #Get the drve that was playing the note

                            try:
                                sounding_drive:FloppyDrive = active_notes.pop(msg.note)

                                #stop the drive from playing
                                sounding_drive.enable = False
                                send(i2c_bus,sounding_drive, justCTRL=True)
                                print("Stopped", msg.note, "on address", sounding_drive.address)

                                #add the drive back to the avaailible drives
                                availible_drives.append(sounding_drive)
                            except KeyError as ke:
                                print("Commanded to stop", msg.note, "but it's not playing")

                        else:
                            #This is a note_on 

                            #Cant play a note if all drives are busy
                            if (len(availible_drives)==0):
                                print("Can't play", msg.note, "no availible drives")
                                print("    ", len(availible_drives))
                            else:
                                #get an availible drive
                                next_drive:FloppyDrive = availible_drives.pop()
                                #set up the drive to play the note 
                                next_drive.setFrequency(MIDI_LOOK_UP[msg.note]['freq'])
                                next_drive.enable = True

                                #tell the drive to play the note
                                send(i2c_bus,next_drive, justCTRL=False)
                                print("Playing", msg.note, "on address", next_drive.address)

                                #add the note to the active notes
                                active_notes[msg.note] = next_drive
                    else:
                        print("Can't sound:" ,msg)
                elif (msg.type == 'control_change'):
                    print("CC:", msg)
                    #stop_all()
                elif (msg.type == 'clock'):
                    #print("Clock"")
                    pass

                else:
                    print("Ignoring message:" ,msg)



#Handle main
if __name__ == '__main__':
    try:
        main()
    except:
        kill_all()
        