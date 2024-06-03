from mido import Message
from smbus import SMBus

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
# NOTE: If using a potentiometer for the pitch bend the ATmega328p only uses 10-bits for an analog read. That means that technically we have
#   6 unused bits in the pitch bend upper byte(PU)(input_states[5]) in the 6 Most significant bits (MSBs), that we could use for expansion


#TODO: fix/add comments
class FloppyKeyboard:

    key_masks = (
        { # Byte 1
        0b10000000:'KEY_1',
        0b01000000:'KEY_2',
        0b00100000:'KEY_3',
        0b00010000:'KEY_4',
        0b00001000:'KEY_5',
        0b00000100:'KEY_6',
        0b00000010:'KEY_7',
        0b00000001:'KEY_8'
        },
        { # Byte 2
        0b10000000:'KEY_9',
        0b01000000:'KEY_10',
        0b00100000:'KEY_11',
        0b00010000:'KEY_12',
        0b00001000:'KEY_13',
        0b00000100:'KEY_14',
        0b00000010:'KEY_15',
        0b00000001:'KEY_16'
        },
        { # Byte 3
        0b10000000:'KEY_17',
        0b01000000:'KEY_18',
        0b00100000:'KEY_19',
        0b00010000:'KEY_20',
        0b00001000:'KEY_21',
        0b00000100:'KEY_22',
        0b00000010:'KEY_23',
        0b00000001:'KEY_24'
        },
        { # Byte 4
        0b10000000:'KEY_25',
        0b01000000:'KEY_26',
        0b00100000:'KEY_27',
        0b00010000:'KEY_28',
        0b00001000:'KEY_29',
        0b00000100:'KEY_30',
        0b00000010:'KEY_31',
        0b00000001:'KEY_32'
        },
        { # Byte 5
        0b10000000:'KEY_33',
        0b01000000:'KEY_MOD',
        0b00100000:'UNUSED_1',
        0b00010000:'UNUSED_2',
        0b00001000:'UNUSED_3',
        0b00000100:'UNUSED_4',
        0b00000010:'UNUSED_5',
        0b00000001:'UNUSED_6'
        }
    )

    def __init__(self, *, i2c_bus:SMBus, i2c_address:int = 0x77, out_channel:int=0, midi_start_note = 35) -> None:
        self.bus = i2c_bus
        self.address = i2c_address
        self.channel = out_channel
        self.key2MIDI = FloppyKeyboard.genKey2MIDI(midi_start_note)
        self.lastState: list[int] = [0, 0, 0, 0, 0, 0 ,0] 

    def read(self)->list[Message]:
        newState = self.bus.read_i2c_block_data(self.address,0,7)

        # The first five bytes represent the buttons/keys
        newKeyStates = newState[0:5]

        # The last two bytes are the represent the pitch wheel
        newPitchState = newState[5:]

        messages = []

        if(not self.lastState[0:5] == newKeyStates):
            messages.extend(self.keyStatesChanged(newKeyStates))

        if(not self.lastState[5:] == newPitchState):
            messages.append(self.pitchStateChanged(newPitchState))



        #update the state after handling it
        self.lastState = newState

        return messages
    
    def keyStatesChanged(self, newKeyStates:list[int])->list[Message]:
        messages = []
 
        #loop through the key state bytes (the first five) 
        for byteNum in range(0,len(newKeyStates)):
            # XOR-ing the lastState with newState gives us which bits (keys)
            # have changed
            changed_bits = newKeyStates[byteNum] ^ self.lastState[byteNum]

            # print(f'Byte {byteNum+1}',"old state","{:08b}".format(self.lastState[byteNum]))
            # print(f'Byte {byteNum+1}',"new state","{:08b}".format(newKeyStates[byteNum]))
            # print(f'Byte {byteNum+1}',"changes","{:08b}".format(changed_bits))

            #Now we have to compare which key was changed
            for mask in FloppyKeyboard.key_masks[byteNum]:
                # If the mask & the changed bits is True, that key has changed
                # and we need to figure out if was pressed or released
                if (mask & changed_bits):
                    #If the mask & the newState is true then the key was Pressed
                    pressed = mask & newKeyStates[byteNum]
                    message = self.key2msg(FloppyKeyboard.key_masks[byteNum][mask], pressed)
                    messages.append(message)
 
        return messages

    def pitchStateChanged(self, newPitchState:list[int])->Message:
        # the value is the last two bytes of the message
        pitchbend_value = (newPitchState[0]<<8) | (newPitchState[1])

        # Map the [0,1023] arduino adc value to the range [-8191, 8191] for midi
        pitchbend_value  =  (pitchbend_value) * (16382) // (1023) + (-8191)

        return Message('pitchwheel',
                       channel=self.channel,
                       pitch = pitchbend_value,
                       time = 0)        
        

    def key2msg(self, key_code:str, pressed:bool)->Message:
        if key_code.startswith("UNUSED"):
            #An unused key was changed, just send an unused control change
            #https://nickfever.com/music/midi-cc-list
            return Message('control_change',
                            channel = self.channel,
                            control = 102,
                            value = int(pressed),
                            time = 0)
        
        if key_code == 'KEY_MOD':
            #The modulation keystate changed,
            #return the modulation control change message (cc 1)
            #with the value of the pressed state (on/pressed=1 and off/released=0)
            return Message('control_change',
                            channel = self.channel,
                            control = 1,
                            value = int(pressed),
                            time = 0)        

        # If the key string is not 'UNUSED' or 'KEY_MOD' it must be a piano key
        # state change. So the following code should generate 'note on' and 
        # 'note off' midi messages depending on if the key was released or pressed

        if pressed:
            return Message('note_on', 
                            channel = self.channel,
                            note = self.key2MIDI[key_code],
                            velocity = 1, #velocity must be >1 for note on 
                            time = 0)
        else:
            return Message('note_off',
                            channel = self.channel,
                            note = self.key2MIDI[key_code],
                            velocity = 0,
                            time = 0)
    
    @classmethod
    def genKey2MIDI(cls,midi_start_note:int)->dict[str,int]:

        if(type(midi_start_note) is not int 
           or midi_start_note<0 or midi_start_note>94):
            raise ValueError("midi_start_note must an integer in the range [0, 94]")

        key_map = {}
        midi_note = midi_start_note
        for key_number in range(1, 34):
            key_map[f'KEY_{key_number}'] = midi_note
            midi_note = midi_note + 1
        
        return key_map
              

# #Code to test       
# if __name__ == '__main__':          
#     bus = SMBus(1) ## indicates /dev/ic2-1
#     p = FloppyKeyboard(i2c_bus=bus)
#     while True:
#         for msg in p.read():
#             print(msg)        
#         print("-----------------------------")
#         time.sleep(0.3)
