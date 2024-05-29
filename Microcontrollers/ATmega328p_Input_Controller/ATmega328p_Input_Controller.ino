/*
 * FlopPiano - Keys and input sketch.
 * Version 0.5
 * 
 * 2024-05-27
 * Jacob Brooks, Jorian Khan
 * 
 *                      
 * This code is intended to run on a ATmega328p (Uno or Nano) and return the input states 
 * of piano keys, modulation,and pitchbend wheel via I2C
 *
 * 
 */

#include <Wire.h>


//The I2C for this device, Pi expects to get keyboard data on 
#define I2C_ADDR 0x77

//Example pin defines
//#define pitchbend_pin XX
//#define MUX_Z_pin    XX
//#define MUX_A_pin    xx
//#define MUX_B_pin    xx
//#define MUX_C_pin    xx
//#define MUX_D_pin    xx
//#define MUX1_INH_pin xx
//#define MUX2_INH_pin xx
//#define MUX3_INH_pin xx



// We need 7 bytes to represent all the input states. The bytes are stored in an array to facilitate sending via I2C, and are cataloged below:                                                
/*
 * |-------------------------------------------------------------------------------------------------------------------------------------------|
 * |                                                   An array to hold input states                                                           |
 * |----------------------------|-------------------------------------------|------------------------------------------------------------------|
 * | Array Position/Byte Number |                 Function                  |      Byte positions [MSB, ..., ..., ..., ..., ..., ..., LSB]     |
 * |----------------------------|-------------------------------------------|------------------------------------------------------------------|
 * |     input_states[0]        |               keys  1 -  8                | [KEY_01, KEY_02, KEY_03, KEY_04, KEY_05, KEY_06, KEY_07, KEY_08] | 
 * |     input_states[1]        |               keys  9 - 16                | [KEY_09, KEY_10, KEY_11, KEY_12, KEY_13, KEY_14, KEY_15, KEY_16] | 
 * |     input_states[2]        |               keys 17 - 24                | [KEY_17, KEY_18, KEY_19, KEY_20, KEY_21, KEY_22, KEY_23, KEY_18] | 
 * |     input_states[3]        |               keys 25 - 32                | [KEY_25, KEY_26, KEY_26, KEY_28, KEY_29, KEY_30, KEY_31, KEY_32] | 
 * |     input_states[4]        | key 33 & modulate(MOD) & extra/unused(UU) | [KEY_33,    MOD,     UU,     UU,     UU,     UU,     UU,     UU] | 
 * |     input_states[5]        |           pitch bend upper byte(PU)       | [PU_MSB,    ...,    ...,    ...,    ...,    ...,    ..., PU_LSB] |
 * |     input_states[6]        |           pitch bend lower byte(PL)       | [PL_MSB,    ...,    ...,    ...,    ...,    ...,    ..., PL_LSB] |
 * |----------------------------|-------------------------------------------|------------------------------------------------------------------|
 * 
 * NOTE: If using a potientiometer for the pitch bend the ATmega328p only uses 10-bits for an analog read. That means that technically we have
 *       6 unused bits in the pitch bend upper byte(PU)(input_states[5]) in the 6 Most significant bits (MSBs), that we could use for expansion
 * 
 */

//Set all inputs to zero by default
//byte input_states[7] = {0, 0, 0, 0, 0, 0, 0};

//TEST Pattern: remove before real use
byte input_states[7] = {0b11110000, 0b00001111, 0b11001100, 0b00110011, 0b10000001, 0b10101010, 0b01010101};
//TEST a var to hold time for a non-blocking delay - remove 
long oldTime = 0;


void setup() {
  /*
   * Setup Pins here
   */

  //Setup I2C
  Wire.begin(I2C_ADDR); // join i2c bus with address #I2C_ADDR
  Wire.onRequest(requestEvent); //Register requestEvent

  
}

void loop() {
  
  /*
   * Read all the inputs here. i.e. shift in values from the Muxs and read pitch bend/ modulate values
   */

   //------------------------------------TESTING CODE-------------------------------------------------//
   //Remove after writing the actual code

   //A loop that flips all the bits in every byte
   for(int idx =0; idx<sizeof(input_states); idx++){
      input_states[idx] = (input_states[idx]) ^ (0b11111111); //Just flip all the bits 
   } 

   //non-blocking delay for 100ms
   oldTime = millis();

   while (millis() < oldTime + 100){
      //do nothing
   }
   //------------------------------------ End TESTING CODE---------------------------------------------//

}



void requestEvent(){
  //When we get a request send all the input states
  Wire.write(input_states,7);
}
