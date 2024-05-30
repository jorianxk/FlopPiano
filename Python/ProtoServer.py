#from FlopPiano.FloppyDrive import CrashMode
from enum import Enum
from mido import Message
from smbus import SMBus
import time


# We need 7 bytes to represent all the input states. The bytes are stored in an array to facilitate sending via I2C, and are cataloged below:                                                
# 
# |-------------------------------------------------------------------------------------------------------------------------------------------|
# |                                                   An array to hold input states                                                           |
# |----------------------------|-------------------------------------------|------------------------------------------------------------------|
# | Array Position/Byte Number |                 Function                  |      Byte positions [MSB, ..., ..., ..., ..., ..., ..., LSB]     |
# |----------------------------|-------------------------------------------|------------------------------------------------------------------|
# |     input_states[0]        |               keys  1 -  8                | [KEY_01, KEY_02, KEY_03, KEY_04, KEY_05, KEY_06, KEY_07, KEY_08] | 
# |     input_states[1]        |               keys  9 - 16                | [KEY_09, KEY_10, KEY_11, KEY_12, KEY_13, KEY_14, KEY_15, KEY_16] | 
# |     input_states[2]        |               keys 17 - 24                | [KEY_17, KEY_18, KEY_19, KEY_20, KEY_21, KEY_22, KEY_23, KEY_24] | 
# |     input_states[3]        |               keys 25 - 32                | [KEY_25, KEY_26, KEY_26, KEY_28, KEY_29, KEY_30, KEY_31, KEY_32] | 
# |     input_states[4]        | key 33 & modulate(MOD) & extra/unused(UU) | [KEY_33,    MOD,     UU,     UU,     UU,     UU,     UU,     UU] | 
# |     input_states[5]        |           pitch bend upper byte(PU)       | [PU_MSB,    ...,    ...,    ...,    ...,    ...,    ..., PU_LSB] |
# |     input_states[6]        |           pitch bend lower byte(PL)       | [PL_MSB,    ...,    ...,    ...,    ...,    ...,    ..., PL_LSB] |
# |----------------------------|-------------------------------------------|------------------------------------------------------------------|
#   
# NOTE: If using a potientiometer for the pitch bend the ATmega328p only uses 10-bits for an analog read. That means that technically we have
#   6 unused bits in the pitch bend upper byte(PU)(input_states[5]) in the 6 Most significant bits (MSBs), that we could use for expansion
#  
#  






#TODO: fix comments
class FlopKeyboard:

    key_masks = [
        {
        0b10000000:'KEY_1',
        0b01000000:'KEY_2',
        0b00100000:'KEY_3',
        0b00010000:'KEY_4',
        0b00001000:'KEY_5',
        0b00000100:'KEY_6',
        0b00000010:'KEY_7',
        0b00000001:'KEY_8'
        },
        {
        0b10000000:'KEY_9',
        0b01000000:'KEY_10',
        0b00100000:'KEY_11',
        0b00010000:'KEY_12',
        0b00001000:'KEY_13',
        0b00000100:'KEY_14',
        0b00000010:'KEY_15',
        0b00000001:'KEY_16'
        },
        {
        0b10000000:'KEY_17',
        0b01000000:'KEY_18',
        0b00100000:'KEY_19',
        0b00010000:'KEY_20',
        0b00001000:'KEY_21',
        0b00000100:'KEY_22',
        0b00000010:'KEY_23',
        0b00000001:'KEY_24'
        },
        {
        0b10000000:'KEY_25',
        0b01000000:'KEY_26',
        0b00100000:'KEY_27',
        0b00010000:'KEY_28',
        0b00001000:'KEY_29',
        0b00000100:'KEY_30',
        0b00000010:'KEY_31',
        0b00000001:'KEY_32'
        },
        {
        0b10000000:'KEY_33',
        0b01000000:'KEY_MOD',
        0b00100000:'UNUSED_1',
        0b00010000:'UNUSED_2',
        0b00001000:'UNUSED_3',
        0b00000100:'UNUSED_4',
        0b00000010:'UNUSED_5',
        0b00000001:'UNUSED_6'
        }
    ]


    def __init__(self, i2c_bus:SMBus, i2c_address:int = 0x77) -> None:
        self.bus = i2c_bus
        self.address = i2c_address
        self.lastState: list[int] = [0, 0, 0, 0, 0, 0 ,0] 
    



    def update(self)->list[Message]:
        newState = self.bus.read_i2c_block_data(self.address,0,7)
        #if the state has not changed then just return an empty list
        if (newState == self.lastState):
            return
        
        #The state has changed, we need to generate some messages

        # A loop to loop through the first 5 bytes 
        for byteNum in range(0,5):
            # XOR-ing the lastState with newState gives us which bits (keys)
            # have changed
            changed_bits = newState[byteNum] ^ self.lastState[byteNum]

            print(f'Byte {byteNum+1}',"old state","{:08b}".format(self.lastState[byteNum]))
            print(f'Byte {byteNum+1}',"new state","{:08b}".format(newState[byteNum]))
            print(f'Byte {byteNum+1}',"changes","{:08b}".format(changed_bits))

            #Now we have to compare which key was changed
            for mask in FlopKeyboard.key_masks[byteNum]:
                # If the mask & the changed bits is True, that key has changed
                # and we need to figure out if was pressed or released
                if (mask & changed_bits):
                    #If the mask & the newState is true then the key was Pressed
                    pressed = mask & newState[byteNum]
                    message = self.addMessage(FlopKeyboard.key_masks[byteNum][mask], pressed)

        print("---------------------------------------------------------------")

        #update the state after handling it
        self.lastState = newState

        return None

    #TODO: change control change channels
    def addMessage(self, key:str, pressed:bool):

        if key.startswith("UNUSED"):
            return
        
        if key == 'KEY_MOD':
            self.messages.append(
                Message('control_change',
                        channel = 0,
                        control = 99,
                        value = int(pressed))
                        )
            return
        
        if pressed:
            self.messages.append(
                Message('note_on',
                        channel = 0,
                        note = MAP(key),
                        velocity = 0,
                        time = 0)
                        )
        else:
            self.messages.append(
                Message('note_off',
                        channel = 0,
                        note = MAP(key),
                        velocity = 0,
                        time = 0)
                        )

            

        

        
        


bus = SMBus(1) ## indicates /dev/ic2-1
p = FlopKeyboard(i2c_bus=bus)

while True:
    p.update()
    time.sleep(0.3)






























# active_notes = []
# availible_drives= []


# output = ["Keys_only", "rollover"]
# loopback = True



# effect = [CrashMode.BOW,CrashMode.FLIP, CrashMode.OFF]






# def update():
#     #get_incoming_midi()
#         #Sources:
#             #keys
#             #control midi
#             #physical midi
#     #sound_notes()
#         #pitch
#         #modulate
#         #crash modes (effect)
#     #update input states
#     #output midi
    
#     pass