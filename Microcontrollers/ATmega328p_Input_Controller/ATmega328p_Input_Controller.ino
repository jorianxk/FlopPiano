/*
 * FlopPiano - Keys and input sketch.
 * Version 0.9
 * 
 * 2024-06-03
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

// debug toggles
#define verboseSerial // if this is defined, write key states to serial along with other bullshit
#define onetimeonly // if this is defined, will stop after only one loop to make the serial easier to read

// pin assignments
#define chip0ena 2 // enable pin for multiplexer 0 (active LOW)
#define chip1ena 3 // enable pin for multiplexer 1 (active LOW)
#define chip2ena 4 // enable pin for multiplexer 2 (active LOW)
#define add0pin 5 // address 0 pin
#define add1pin 6 // address 1 pin
#define add2pin 7 // address 2 pin
#define add3pin 8 // address 3 pin
#define inpin 9 // pin to read switch state
#define potpin A0 // pin for the potentiometer

// We need 7 bytes to represent all the input states. The bytes are stored in an array to facilitate sending via I2C, and are cataloged below:                                                
/*
 * |-------------------------------------------------------------------------------------------------------------------------------------------|
 * |                                                   An array to hold input states                                                           |
 * |----------------------------|-------------------------------------------|------------------------------------------------------------------|
 * | Array Position/Byte Number |                 Function                  |      Byte positions [MSB, ..., ..., ..., ..., ..., ..., LSB]     |
 * |----------------------------|-------------------------------------------|------------------------------------------------------------------|
 * |     input_states[0]        |               keys  1 -  8                | [KEY_01, KEY_02, KEY_03, KEY_04, KEY_05, KEY_06, KEY_07, KEY_08] | 
 * |     input_states[1]        |               keys  9 - 16                | [KEY_09, KEY_10, KEY_11, KEY_12, KEY_13, KEY_14, KEY_15, KEY_16] | 
 * |     input_states[2]        |               keys 17 - 24                | [KEY_17, KEY_18, KEY_19, KEY_20, KEY_21, KEY_22, KEY_23, KEY_24] | 
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

// function prototypes
unsigned int readChip(int,int);


//Set all inputs to zero by default
byte input_states[7] = {0, 0, 0, 0, 0, 0, 0};
bool binAdd[4] = {0}; // bool array to hold multiplexer address

void setup() {

  // set up pins
  pinMode(chip0ena, OUTPUT); digitalWrite(chip0ena, HIGH);
  pinMode(chip1ena, OUTPUT); digitalWrite(chip1ena, HIGH);
  pinMode(chip2ena, OUTPUT); digitalWrite(chip2ena, HIGH);
  pinMode(add0pin, OUTPUT); digitalWrite(add0pin, LOW);
  pinMode(add1pin, OUTPUT); digitalWrite(add1pin, LOW);
  pinMode(add2pin, OUTPUT); digitalWrite(add2pin, LOW);
  pinMode(add3pin, OUTPUT); digitalWrite(add3pin, LOW);
  pinMode(inpin, INPUT_PULLUP);
  
  //Setup I2C
  Wire.begin(I2C_ADDR); // join i2c bus with address #I2C_ADDR
  Wire.onRequest(requestEvent); //Register requestEvent

  // start serial if necessary
  #ifdef verboseSerial
    Serial.begin(115200);
    Serial.println("Serial starting...");
  #endif
}

void loop() {
  
  #ifdef verboseSerial
    Serial.println("------------------------ NEW LOOP TIME -------------------------");
    Serial.println("=^..^=   =^..^=   =^..^=    =^..^=    =^..^=    =^..^=    =^..^=");
    Serial.println("----------------------------------------------------------------");
  #endif

 // loop through each chip, pack into keystate array
  readChip(2,0);
  readChip(3,2);
  readChip(4,4);

  // read in potentiometer
  unsigned int pot = analogRead(potpin); // variable to hold ADC read for potentiometer
  input_states[5] = pot >> 8;
  input_states[6] = pot;

  Serial.println(pot);

  #ifdef verboseSerial
    Serial.println("Input states: ***************************************************");
    for (int i=0; i<7; i++){
      Serial.println(input_states[i], BIN);
    }
  #endif

  #ifdef onetimeonly
    while(1);
  #endif

}

void requestEvent(){
  //When we get a request send all the input states
  Wire.write(input_states,7);
}

unsigned int readChip(int pin, int arrayIndex){
  #ifdef verboseSerial // if writing to serial, tell it which pin we are interested in reading from
    Serial.println("************************************");
    Serial.print("Reading chip on pin "); Serial.println(pin);
  #endif
  digitalWrite(pin, LOW); // turn on whichever chip enable is required

  unsigned int states = 0;

  for (int address=0; address<=15; address++) // loops through each combination of address pins
  {
    // convert address to binary array
    for (int i = 3; i >= 0; i--) 
    {
      binAdd[i] = (address & (1 << i)) != 0;
    }
 
    #ifdef verboseSerial // if serial enabled, write the address shit there
      Serial.print("Address "); Serial.print(address);
      Serial.print(", bin: ");
      for (int i=0; i<=3; i++)
      {
        Serial.print(binAdd[i]);
      }
      Serial.println(" ");
    #endif

    // write address to appropriate pins
    digitalWrite(add0pin, binAdd[0]);
    digitalWrite(add1pin, binAdd[1]);
    digitalWrite(add2pin, binAdd[2]);
    digitalWrite(add3pin, binAdd[3]);

    states = (states << 1) | (!digitalRead(inpin)); // move the bits to the left 1 spot, put the new bit in the first position
  }
  
  digitalWrite(pin, HIGH); // turn the chip off
  
  input_states[arrayIndex] = (states >> 8); // write input states to array index
  input_states[arrayIndex + 1] = states; // write the rest of the input states to array index + 1

  #ifdef verboseSerial // if verbose serial defined, write the keystate there
    Serial.print("Keystates: ");
    Serial.println(states, BIN);
  #endif
  return(states);
}