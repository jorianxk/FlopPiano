from FlopPiano.FloppyDrive import FloppyDrive
from smbus import SMBus
import time






i2c_bus = SMBus(1) ## indicates /dev/ic2-1
addr = 0x77



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



availible_drives =[FloppyDrive(address = 0x08),
                   FloppyDrive(address = 0x09),
                   FloppyDrive(address = 0x0a),
                   FloppyDrive(address = 0x0b),
                   FloppyDrive(address = 0x0c),
                   FloppyDrive(address = 0x0d),
                   FloppyDrive(address = 0x0e),
                   FloppyDrive(address = 0x0f),
                   FloppyDrive(address = 0x10),
                   FloppyDrive(address = 0x11)]

input_controller_addr = 0x77




def testAll():
    print("Testing all drives sequentially...")
    global availible_drives
    time.sleep(1)
    for drive in availible_drives:
        print(drive.address)
        drive.enable =1
        send(i2c_bus, drive, justCTRL=False)
        time.sleep(0.5)
        drive.enable =0
        send(i2c_bus, drive, justCTRL=True)
    print("Done.")

def timingTest():

    totalTime = time.time()

    print ("Turning on all drives...")
    startTime = time.time()
    for drive in availible_drives:
        drive.setFrequency(38.891)
        drive.enable =1

        send(i2c_bus, drive, justCTRL=False)
    print("Time to turn on drives:",time.time()- startTime)   #Finished 0.005172252655029297 s
    #Time to turn on drives: 0.005036115646362305

    print ("Waiting 1 second ...")
    time.sleep(1)

    print ("Turning off all drives...")
    startTime = time.time()
    for drive in availible_drives:
        drive.enable =0
        send(i2c_bus, drive, justCTRL=True)
    print("Time to turn off drives:",time.time()- startTime)   
    #Time to turn off drives: 0.005103349685668945

    print ("Waiting 1 second ...")
    time.sleep(1)

    print ("Reading inputs...")
    startTime = time.time()
    data = i2c_bus.read_i2c_block_data(input_controller_addr,0,7)
    for byt in data:    
        print("{:08b}".format(byt))
        print(type(byt))
    print("Time to get inputs:",time.time()- startTime)   



    print("Total Time:",(time.time()- totalTime)-2)   


timingTest()
#testAll()

































# while True:
#     print("--------------------")
#     data = i2c_bus.read_i2c_block_data(addr,0,7)
    
#     for byt in data:
        
#         print("{:08b}".format(byt))
        
    
#     print("--------------------")
#     time.sleep(0.3)

# // We need 7 bytes to represent all the input states. THey bytes are stored in an array to facilitate sending via I2C, and are cataloged below:                                                
# /*
#  * |-------------------------------------------------------------------------------------------------------------------------------------------|
#  * |                                                   An array to hold input states                                                           |
#  * |----------------------------|-------------------------------------------|------------------------------------------------------------------|
#  * | Array Position/Byte Number |                 Function                  |      Byte positions [MSB, ..., ..., ..., ..., ..., ..., LSB]     |
#  * |----------------------------|-------------------------------------------|------------------------------------------------------------------|
#  * |     input_states[0]        |               keys  1 -  8                | [KEY_01, KEY_02, KEY_03, KEY_04, KEY_05, KEY_06, KEY_07, KEY_08] | 
#  * |     input_states[1]        |               keys  9 - 16                | [KEY_09, KEY_10, KEY_11, KEY_12, KEY_13, KEY_14, KEY_15, KEY_16] | 
#  * |     input_states[2]        |               keys 17 - 24                | [KEY_17, KEY_18, KEY_19, KEY_20, KEY_21, KEY_22, KEY_23, KEY_18] | 
#  * |     input_states[3]        |               keys 25 - 32                | [KEY_25, KEY_26, KEY_26, KEY_28, KEY_29, KEY_30, KEY_31, KEY_32] | 
#  * |     input_states[4]        | key 33 & modulate(MOD) & extra/unused(UU) | [KEY_33,    MOD,     UU,     UU,     UU,     UU,     UU,     UU] | 
#  * |     input_states[5]        |           pitch bend upper byte(PU)       | [PU_MSB,    ...,    ...,    ...,    ...,    ...,    ..., PU_LSB] |
#  * |     input_states[6]        |           pitch bend lower byte(PL)       | [PL_MSB,    ...,    ...,    ...,    ...,    ...,    ..., PL_LSB] |
#  * |----------------------------|-------------------------------------------|------------------------------------------------------------------|
#  * 
#  * NOTE: If using a potientiometer for the pitch bend the ATmega328p only uses 10-bits for an analog read. That means that technically we have
#  *       6 unused bits in the pitch bend upper byte(PU)(input_states[5]) in the 6 Most significant bits (MSBs), that we could use for expansion
#  * 
#  */


#msg = mido.Message('note_on', note = 60)

# print(mido.get_input_names())


# with PortServer('localhost', 8080) as server:
#     while True:
#         client = server.accept()
#         for message in client:
#             print(message)

#print(mido.get_output_names())


# #Handle main
# if __name__ == '__main__':
#     s = {-8:"sadfds",7:"asdasd"}
#     print(s[-8])
