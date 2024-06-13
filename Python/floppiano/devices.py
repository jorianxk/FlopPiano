from enum import IntFlag
from . import bus
from mido import Message

class CrashMode (IntFlag):
    """
    A Enum to hold Floppy drive crash modes

    *  Crash mode - the two crash mode bits represent which crash mode the
    *  drive will use. Two bit combined give four possible states:
    *    MSB LSB
    *     0   0  - Crash prevention OFF
    *     0   1  - Crash prevention ON (BOW Mode)
    *     1   0  - Crash prevention ON (FLIP Mode)
    *     1   1  - Not used (results in crash prevention mode off if set)
    *     
    *     BOW mode: The drive will step until end of travel then flip
    *     direction (like a violin bow changing direction at the end of a
    *     bow stroke)
    *     
    *     FLIP mode: THe drive will flip direction after every step/pulse
    """
    __order__ = 'OFF BOW FLIP'
    OFF = 0b00
    BOW = 0b01
    FLIP = 0b10

class Drive:
    """
    A class that represents a floppy drive
    """
    #clock speed of the attiny1604
    CLK_FREQ = 20000000 
    #prescaler setting on attiny1604
    PRESCALAR = 4
    #TOP = alpha/f
    #alpha = C_f/(2*N)
    #the alpha constant for frequency calculation
    ALPHA = CLK_FREQ / (2 * PRESCALAR)
    
    #minimum frequency that can be sounded
    MIN_FREQUENCY = 38.891

    #maximum frequency that can be sounded
    MAX_FREQUENCY = 12543.854

    #init with default values of the firmware
    def __init__(self,
                 address:int,
                 enable:bool = False, 
                 spin:bool = False,
                 top: int = 19111,
                 crash_mode:CrashMode = CrashMode.FLIP) -> None:
        """Constructor for a FloppyDrive

            Default arguments represent the defaults state of the drive's 
            firmware.

        Args:
            address (int, optional): The I2C address for the drive. Defaults to
                8.
            enable (bool, optional): The drive's  select/enable state. Defaults
                to False.
            spin (bool, optional): The drive select/enable state. Defaults to
                False.
            top (int, optional): The TOP value of the drive. Defaults to 19111.
            crash_mode (CrashMode, optional): The crash mode of the drive. 
                Defaults to CrashMode.FLIP.
        """
        self.address = address
        self._top = top #Top value of the drive 
        self.enable = enable #Drive enable state
        self.spin = spin #Drive spin state
        self.crash_mode = crash_mode #Crash prevention mode

    #TODO: update docstring
    def update(self, just_CTRL:bool=False)->None:
        """
        A function to send all set CTRL Register values and TOP values a slave 
        drive, or to broadcast to the bus

        see code firmware and send(self, address:int=None, justCTRL:bool=True)
        Comments for details

        parameters: 
            address:int optional. if none the data is sent bus wide (broadcast)
                to all devices on the bus (address 0x0)
            justCTRL:bool optional. if true, just the CTRL register is sent
                if false, CTRL plus the TOP value is sent to the address

        raises: 
            OSError: If the I2C bus cant sent the message for whatever
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
        CTRL = (self.crash_mode << 2)     
        CTRL = CTRL | (self.spin << 1)
        CTRL = CTRL | (self.enable)

        #print("{:08b}".format(CTRL), CTRL)

        #|----------------------------------------------------------------|
        #|            The second and third bytes - TOP Value              |
        #|----------------------------------------------------------------|
        #|  The second byte is the most significant byte of the TOP value |
        #|  The third byte is the least significant byte of the TOP value |
        #|----------------------------------------------------------------|

        TOP = self._top.to_bytes(2,'little')

        
        ########################################################################
        #                  Write the values to the address                     #
        ########################################################################



        # #are we just sending the CTRL register?
        if just_CTRL:
            bus.write(self.address, CTRL, [])
        else:
            bus.write(self.address, CTRL, [TOP[1], TOP[0]])

    #TODO: update docstring
    def silence(self)->None:
        self.enable = False
        self.update()

    @property
    def top(self)->int:
        return self._top
    
    @top.setter
    def top(self, frequency:float):# -> int:
        """_summary_
            A function to set the frequency of the drive by setting the drive 
            TOP

            A valid frequency results in TOP value that is a unsigned 16 bit 
            integer [0-65535].

            TOP = round(alpha / frequency)

            where,
                alpha = C_f / (2 * N) 
                C_f is the attiny's clock speed  = 20000000
                N is the attiny's prescaler  = 4

        Args:
            frequency (float): The desired frequency of the drive

        Raises:
            ValueError: If the frequency value given results in a TOP value 
                that is not a 16bit unsigned int
            ZeroDivisionError: if frequency is zero             

        Returns:
            int: The the resultant TOP value from the desired frequency
        """
        #TODO: DO we really need the max/min freq check?
        #if the frequency cant be sounded, dont change anything
        if (frequency >= Drive.MIN_FREQUENCY and 
            frequency<= Drive.MAX_FREQUENCY):

            proposed_top = round(Drive.ALPHA/frequency)

            if((proposed_top < 0) or (proposed_top > 65535)):
                raise ValueError (f'Frequency resulted in illegal TOP. '
                                  f'Given frequency: {frequency}, '
                                  f'Resultant TOP: {proposed_top}')
            
            self._top = proposed_top
            #return int(Drive.ALPHA/proposed_top)
    
    def __repr__(self) -> str:
        """_summary_
            Returns a string representation of the Drive
        Returns:
            str: A string representation of the Drive
        """
                
        return ('Drive: '
                f'[Address: {self.address} | '
                f'Enable: {self.enable} | '
                f'Spin: {self.spin} | '
                f'Crash Prevent: {self.crash_mode} | '
                f'TOP: {self._top}]')



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
class Keyboard:

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

    def __init__(self, *, address:int = 0x77, out_channel:int=0, midi_start_note = 35) -> None:
        self.address = address
        self.channel = out_channel
        self.key2MIDI = Keyboard.genKey2MIDI(midi_start_note)
        self.lastState: list[int] = [0, 0, 0, 0, 0, 0 ,0] 

    def read(self)->list[Message]:
        messages = []

        newState = bus.read(self.address,0,7)

        # The first five bytes represent the buttons/keys
        newKeyStates = newState[0:5]

        # The last two bytes are the represent the pitch wheel
        newPitchState = newState[5:]

        

        if(not self.lastState[0:5] == newKeyStates):
            messages.extend(self.keyStatesChanged(newKeyStates))
            #pass

        if(not self.lastState[5:] == newPitchState):
            messages.append(self.pitchStateChanged(newPitchState))
            #pass



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
            for mask in Keyboard.key_masks[byteNum]:
                # If the mask & the changed bits is True, that key has changed
                # and we need to figure out if was pressed or released
                if (mask & changed_bits):
                    #If the mask & the newState is true then the key was Pressed
                    pressed = mask & newKeyStates[byteNum]
                    message = self.key2msg(Keyboard.key_masks[byteNum][mask], pressed)
                    messages.append(message)
 
        return messages

    def pitchStateChanged(self, newPitchState:list[int])->Message:
        # the value is the last two bytes of the message
        pitchbend_value = (newPitchState[0]<<8) | (newPitchState[1])
        #todo update with Utils.map range
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
    
    @staticmethod
    def genKey2MIDI(midi_start_note:int)->dict[str,int]:

        if(type(midi_start_note) is not int 
           or midi_start_note<0 or midi_start_note>94):
            raise ValueError("midi_start_note must an integer in the range [0, 94]")

        key_map = {}
        midi_note = midi_start_note
        for key_number in range(1, 34):
            key_map[f'KEY_{key_number}'] = midi_note
            midi_note = midi_note + 1
        
        return key_map
