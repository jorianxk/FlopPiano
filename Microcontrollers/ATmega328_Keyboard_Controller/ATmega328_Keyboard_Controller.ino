/*
 * FlopPiano - Keyboard input controller sketch.
 * Version 1.0
 * 
 * 2024-07-26
 * Jacob Brooks, Jorian Khan
 * 
 *                      
 * This code is intended to run on a ATmega328p (Uno or Nano) and return the key input 
 * states and display status LEDs of piano keys, modulation, and pitchbend wheel via I2C
 *
 * 
 */

 
#include <Wire.h>


#define I2C_ADDR 0x77  // The I2C for this device
#define DEVICE_TYPE 55 // The Device Type 

#define CTRL_REG 0 
#define INPUT_REG 1
#define DEVICE_TYPE_REG 4

#define POT_HYSTERESIS  25  // A threshold value for detecting changes in wheels
#define PITCH_MAX       215 // Max analog read for pitch wheel
#define PITCH_MIN       800 // Min analog read for pitch wheel
#define PITCH_DEAD_ZONE 30  // The half-width of the pitch wheel dead zone
#define MOD_MAX         215 // Max analog read for mod wheel
#define MOD_MIN         800 // Min analog read for mod wheel

// Input pin assignments
#define MUX_0_ENA_PIN  2 // enable pin for multiplexer 0 (active LOW)
#define MUX_1_ENA_PIN  3 // enable pin for multiplexer 1 (active LOW)
#define MUX_2_ENA_PIN  4 // enable pin for multiplexer 2 (active LOW)
#define MUX_ADDR_0_PIN 5 // address 0 pin for multiplexers
#define MUX_ADDR_1_PIN 6 // address 1 pin for multiplexers
#define MUX_ADDR_2_PIN 7 // address 2 pin for multiplexers
#define MUX_ADDR_3_PIN 8 // address 3 pin for multiplexers
#define MUX_INPUT_PIN  9 // pin to read switch state
#define PITCH_PIN     A0 // analog pin for the pitch wheel
#define MOD_PIN       A1 // analog pin for modulation wheel


// Output pin assignments
#define MUTE_LED_PIN         12 // Pin for Mute button backlight
#define OCTIVE_UP_LED_PIN    11 // Pin for Octave up button backlight
#define OCTIVE_DOWN_LED_PIN  10 // Pin for Octave down button backlight
#define OCTAVE_LED_SH_CP_PIN 13 // Pin for Octave LED shift register clock
#define OCTAVE_LED_ST_CP_PIN A2 // Pin for Octave LED shift register latch
#define OCTAVE_LED_DS_PIN    A3 // Pin for Octave LED shift register data serial input



// Function prototypes
// Reads all the key states and stores them in key_states
void readInputStates();

// Reads all states of a 16 channel multiplexer and stores them in mux_buffer
unsigned int readMux(int);

// Writes all LED states according to the CTRL register/byte
void writeOutputStates();

// The register which the Pi wants to read/write from/to
byte reg = 0;

// The incoming CTRL byte
byte ctrl = 0; 

//array to to hold all input states
byte input_states[9] = {0, 0, 0, 0, 0, 0, 0, 0, 0};  

// a buffer to hold the multiplexer states
byte mux_buffer[2] = {0,0}; 

// buffers for detecting wheel changes
unsigned int last_pitch = 0;
unsigned int last_mod = 0;

void setup() {
  // Setup Multiplexer pins (Input)
  pinMode(MUX_0_ENA_PIN, OUTPUT);       digitalWrite(MUX_0_ENA_PIN, HIGH);
  pinMode(MUX_1_ENA_PIN, OUTPUT);       digitalWrite(MUX_1_ENA_PIN, HIGH);
  pinMode(MUX_2_ENA_PIN, OUTPUT);       digitalWrite(MUX_2_ENA_PIN, HIGH);
  pinMode(MUX_ADDR_0_PIN, OUTPUT);      digitalWrite(MUX_ADDR_0_PIN, LOW);
  pinMode(MUX_ADDR_1_PIN, OUTPUT);      digitalWrite(MUX_ADDR_1_PIN, LOW);
  pinMode(MUX_ADDR_2_PIN, OUTPUT);      digitalWrite(MUX_ADDR_2_PIN, LOW);
  pinMode(MUX_ADDR_3_PIN, OUTPUT);      digitalWrite(MUX_ADDR_3_PIN, LOW);
  pinMode(MUX_INPUT_PIN, INPUT_PULLUP);

  // Setup Analog Reads  
  // PITCH_PIN -> analog in no pinMode()
  // MOD_PIN   -> analog in no pinMode()

  
  // Setup LEDs and Octave LED Shift Register pins (Output)
  pinMode(MUTE_LED_PIN, OUTPUT);         digitalWrite(MUTE_LED_PIN, LOW);
  pinMode(OCTIVE_UP_LED_PIN, OUTPUT);    digitalWrite(OCTIVE_UP_LED_PIN, LOW);
  pinMode(OCTIVE_DOWN_LED_PIN, OUTPUT);  digitalWrite(OCTIVE_DOWN_LED_PIN, LOW);
  pinMode(OCTAVE_LED_SH_CP_PIN, OUTPUT); 
  pinMode(OCTAVE_LED_ST_CP_PIN, OUTPUT); 
  pinMode(OCTAVE_LED_DS_PIN, OUTPUT); 

  
  // Setup I2C
  Wire.begin(I2C_ADDR);        // Join i2c bus with address I2C_ADDR   
  Wire.onReceive(recieveEvent);// Register recieveEvent 
  Wire.onRequest(requestEvent);// Register recieveEvent 

}

void loop() {
  // Read all the input (button & wheels) states and store them in input_states  
  readInputStates();  
  // Write all the LED states
  writeOutputStates();
}


void recieveEvent(){
  // What register does the Pi want to read/write?
  reg = Wire.read();

  if (reg == CTRL_REG){
    // There should only be one byte if writing to the CTRL Register
    if(Wire.read() ==1){
      // Update the LED states with the new values
      ctrl = Wire.read();
    }
  }
  
  // If there are any remaining bytes just read them and do nothing.
  while (Wire.available()){Wire.read();}
}
void requestEvent(){
  // reg was set during a recieveEvent()
  
  if (reg == INPUT_REG){
    // The Pi wants the input states
    Wire.write(input_states,9);   
  }else if (reg == DEVICE_TYPE_REG){
    // The Pi wants the device type
    Wire.write(DEVICE_TYPE);
  }else{
    // Do Nothing
  }

}

void readInputStates(){
  // Read key states
  readMux(MUX_0_ENA_PIN);
  input_states[0] = mux_buffer[0]; // KEY_3 - KEY_10
  input_states[1] = mux_buffer[1]; // KEY_11 - KEY_18

  readMux(MUX_1_ENA_PIN);
  input_states[2] = mux_buffer[0]; // KEY_19 - KEY_26
  input_states[3] = mux_buffer[1]; // KEY_27 - KEY_34

  readMux(MUX_2_ENA_PIN);
  // KEY_35, MUTE, OCTAVE_UP, OCTAVE_DOWN, KEY_1, KEY_2, KEY_UNUSED, KEY_UNUSED
  input_states[4] = mux_buffer[0]; 
  //mux_buffer[1] We don't use the second 8 channels on the third multipexer

  // Read pitch wheel
  // Force the analog read to be in the normal 10-bit range
  unsigned int pitch = map(analogRead(PITCH_PIN), PITCH_MIN, PITCH_MAX, 0, 1023);

  // Clamp the reading if it's in the deadzone
  if (pitch >= (511 - PITCH_DEAD_ZONE) && pitch <= (511 + PITCH_DEAD_ZONE)){
    pitch = 511;
  }

  // Avoid jitter
  if(abs(pitch - last_pitch) > POT_HYSTERESIS){
    last_pitch = pitch;
    input_states[5] = (pitch >> 8); // PITCH upper byte
    input_states[6] = pitch;        // PITCH lower byte   
  }


  // Read modulation wheel
  // Force the analog read to be in the normal 10-bit range
  unsigned int mod = map(analogRead(MOD_PIN), MOD_MIN, MOD_MAX, 0, 1023);
  // Avoid Jitter
  if(abs(mod - last_mod) > POT_HYSTERESIS){
    last_mod = mod;
    input_states[7] = (mod >> 8); // MOD upper byte
    input_states[8] = mod;        // MOD lower byte    
  }


}

// Reads all states of a 16 channel multiplexer and stores them in mux_buffer
// mux_buffer[0] will contain key states from mux addresses 0-7
// mux_buffer[1] will contain key states from mux addresses 8-15
unsigned int readMux(int mux_pin){
  digitalWrite(mux_pin, LOW); // Enable the multiplexer

  // Outer loop 'banks' the mux's addresses into low/high range
  // bank = 0 -> mux adresses 0-7
  // bank = 1 -> mux adresses 8-15
  for (byte bank = 0; bank <2; bank++){

    // Inner loop counts to  0-7 in each bank    
    for (byte count = 0; count<8; count++){
      byte address = (bank << 3) | count;
      digitalWrite(MUX_ADDR_0_PIN, (0b00000001 & address) >> 0);
      digitalWrite(MUX_ADDR_1_PIN, (0b00000010 & address) >> 1);
      digitalWrite(MUX_ADDR_2_PIN, (0b00000100 & address) >> 2);
      digitalWrite(MUX_ADDR_3_PIN, (0b00001000 & address) >> 3);

      bool key_state  = !digitalRead(MUX_INPUT_PIN);
      mux_buffer[bank] = (mux_buffer[bank] << 1) | key_state; 

    }
 
  }

  digitalWrite(mux_pin, HIGH); // Disable the multiplexer
}

void writeOutputStates(){
  // Update simple LEDs
  digitalWrite(OCTIVE_UP_LED_PIN,   (0b00100000 & ctrl) >> 5);
  digitalWrite(OCTIVE_DOWN_LED_PIN, (0b00010000 & ctrl) >> 4);
  digitalWrite(MUTE_LED_PIN,        (0b00001000 & ctrl) >> 3);


  // Update Octave number indicator LEDs
  // Pull the latch pin low, so LED's don't change while shifting
  digitalWrite(OCTAVE_LED_ST_CP_PIN, LOW);
  // octave number   ->(0b00000111 & ctrl)  
  // number to shift -> (1 << octave number)  
  // shift out the bits:  
  shiftOut(OCTAVE_LED_DS_PIN, OCTAVE_LED_SH_CP_PIN, MSBFIRST, 1 << (0b00000111 & ctrl));
  // Pull the latch pin high, so LED's will light  
  digitalWrite(OCTAVE_LED_ST_CP_PIN, HIGH);  
}

