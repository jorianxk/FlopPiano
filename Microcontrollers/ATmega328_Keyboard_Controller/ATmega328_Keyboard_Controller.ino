/*
 * FlopPiano - Keyboard input controller sketch.
 * Version 0.1
 * 
 * 2024-06-014
 * Jacob Brooks, Jorian Khan
 * 
 *                      
 * This code is intended to run on a ATmega328p (Uno or Nano) and return the input states 
 * of piano keys, modulation,and pitchbend wheel via I2C
 *
 * 
 */


// We need to return these bytes on a I2C Request
// +--------+------------------+------------------+------------------+------------------+------------------+------------------+------------------+------------------+
// |        |                                                                    Bit Number                                                                         |
// + Byte # +------------------+------------------+------------------+------------------+------------------+------------------+------------------+------------------+
// |        |     7 (MSB)      |        6         |        5         |        4         |        3         |        2         |        1         |     0 (LSB)      |
// +--------+------------------+------------------+------------------+------------------+------------------+------------------+------------------+------------------+
// |      0 | KEY_8            | KEY_7            | KEY_6            | KEY_5            | KEY_4            | KEY_3            | KEY_2            | KEY_1            |
// |      2 | KEY_16           | KEY_15           | KEY_14           | KEY_13           | KEY_12           | KEY_11           | KEY_10           | KEY_9            |
// |      3 | KEY_24           | KEY_23           | KEY_22           | KEY_21           | KEY_20           | KEY_19           | KEY_18           | KEY_17           |
// |      4 | KEY_32           | KEY_31           | KEY_30           | KEY_29           | KEY_28           | KEY_27           | KEY_26           | KEY_25           |
// |      5 | NOT USED         | NOT USED         | NOT USED         | NOT USED         | OCTAVE_UP        | OCTAVE_DOWN      | MUTE             | KEY_33           |
// |      6 | PITCH Upper Byte | PITCH Upper Byte | PITCH Upper Byte | PITCH Upper Byte | PITCH Upper Byte | PITCH Upper Byte | PITCH Upper Byte | PITCH Upper Byte |
// |      7 | PITCH Lower Byte | PITCH Lower Byte | PITCH Lower Byte | PITCH Lower Byte | PITCH Lower Byte | PITCH Lower Byte | PITCH Lower Byte | PITCH Lower Byte |
// |      8 | MOD Upper Byte   | MOD Upper Byte   | MOD Upper Byte   | MOD Upper Byte   | MOD Upper Byte   | MOD Upper Byte   | MOD Upper Byte   | MOD Upper Byte   |
// |      9 | MOD Lower Byte   | MOD Lower Byte   | MOD Lower Byte   | MOD Lower Byte   | MOD Lower Byte   | MOD Lower Byte   | MOD Lower Byte   | MOD Lower Byte   |
// +--------+------------------+------------------+------------------+------------------+------------------+------------------+------------------+------------------+




 
#include <Wire.h>

#define SERIAL_DEBUG // if defined, debug information will be printed to serial
#define HANG_DEBUG   // if defined, loop() will hang after one loop() cycle - for debug 


#define I2C_ADDR 0x77 //The I2C for this device, RPi expects to get keyboard data on 

// pin assignments
#define MUX_0_ENA_PIN  2 // enable pin for multiplexer 0 (active LOW)
#define MUX_1_ENA_PIN  3 // enable pin for multiplexer 1 (active LOW)
#define MUX_2_ENA_PIN  4 // enable pin for multiplexer 2 (active LOW)
#define ADDR_0_PIN     5 // address 0 pin for multiplexers
#define ADDR_1_PIN     6 // address 1 pin for multiplexers
#define ADDR_2_PIN     7 // address 2 pin for multiplexers
#define ADDR_3_PIN     8 // address 3 pin for multiplexers
#define INPUT_PIN      9 // pin to read switch state
#define PITCH_PIN     A0 // analog pin for the pitch wheel
#define MOD_PIN       A1 // analog pin for modulation wheel

#define OCTIVE_UP_LED_PIN   10
#define OCTIVE_DOWN_LED_PIN 11
#define MUTE_LED_PIN        12





// Reads all states of a 16 channel multiplexer and stores them in mux_buffer
unsigned int readMux(int);


byte input_states[9] = {0, 0, 0, 0, 0, 0, 0, 0, 0};  //array to to hold all key states
byte mux_buffer[2] = {0,0}; // a buffer to hold the multiplexer states

void setup() {
  // Setup pins
  pinMode(MUX_0_ENA_PIN, OUTPUT);   digitalWrite(MUX_0_ENA_PIN, HIGH);
  pinMode(MUX_1_ENA_PIN, OUTPUT);   digitalWrite(MUX_1_ENA_PIN, HIGH);
  pinMode(MUX_2_ENA_PIN, OUTPUT);   digitalWrite(MUX_2_ENA_PIN, HIGH);
  pinMode(ADDR_0_PIN, OUTPUT);      digitalWrite(ADDR_0_PIN, LOW);
  pinMode(ADDR_1_PIN, OUTPUT);      digitalWrite(ADDR_1_PIN, LOW);
  pinMode(ADDR_2_PIN, OUTPUT);      digitalWrite(ADDR_2_PIN, LOW);
  pinMode(ADDR_3_PIN, OUTPUT);      digitalWrite(ADDR_3_PIN, LOW);
  pinMode(INPUT_PIN, INPUT_PULLUP);

  // Setup I2C
  Wire.begin(I2C_ADDR);         // Join i2c bus with address I2C_ADDR
  Wire.onRequest(requestEvent); // Register requestEvent 

  // Start Serial if we're debuging
  #ifdef SERIAL_DEBUG
    Serial.begin(115200);
    Serial.println("Serial starting...");
  #endif

}

void loop() {
  #ifdef SERIAL_DEBUG
    Serial.println("------------------------ NEW LOOP TIME -------------------------");
    Serial.println("=^..^=   =^..^=   =^..^=    =^..^=    =^..^=    =^..^=    =^..^=");
    Serial.println("----------------------------------------------------------------");
  #endif


  // Read key states
  readMux(MUX_0_ENA_PIN);
  input_states[0] = mux_buffer[0];
  input_states[1] = mux_buffer[1];

  readMux(MUX_1_ENA_PIN);
  input_states[2] = mux_buffer[0];
  input_states[3] = mux_buffer[1];

  readMux(MUX_2_ENA_PIN);
  input_states[4] = mux_buffer[0];
  //mux_buffer[1] We don't uses the second 8 channels on the third mux

  // Read pitch wheel
  unsigned int pitch = analogRead(PITCH_PIN);
  input_states[5] = (pitch >> 8);
  input_states[6] = pitch;
  
  // Read modulation wheel
  unsigned int mod = analogRead(MOD_PIN);
  input_states[7] = (mod >> 8);
  input_states[8] = mod;


  #ifdef SERIAL_DEBUG
    Serial.println("Input states: ***************************************************");
    for (int i=0; i<7; i++){
      Serial.println(input_states[i], BIN);
    }
  #endif

  #ifdef HANG_DEBUG
    while(1);
  #endif

}

void requestEvent(){
  //When we get a request send all the input states
  Wire.write(input_states,9);
}

// Reads all states of a 16 channel multiplexer and stores them in mux_buffer
unsigned int readMux(int mux_pin){
  #ifdef SERIAL_DEBUG 
    Serial.println("************************************");
    Serial.print("Reading multiplexor on pin "); Serial.println(mux_pin);
  #endif
  digitalWrite(mux_pin, LOW); // Enable the multiplexer
  

 
  for (byte i = 0; i <2; i++){
    
    for (byte nibble = 0; nibble<8; nibble++){
      byte address = i<<3 | nibble;
      digitalWrite(ADDR_0_PIN, (0b00000001 & address) >> 0);
      digitalWrite(ADDR_1_PIN, (0b00000010 & address) >> 1);
      digitalWrite(ADDR_2_PIN, (0b00000100 & address) >> 2);
      digitalWrite(ADDR_3_PIN, (0b00001000 & address) >> 3);

      bool state  = !digitalRead(INPUT_PIN);
      mux_buffer[i] = (mux_buffer[i] << 1) | state; 
      
      #ifdef SERIAL_DEBUG
        Serial.print("Address: "); Serial.print(address);
        Serial.print(", bin: ");
        Serial.print((0b00000001 & address) >> 0, BIN);
        Serial.print((0b00000010 & address) >> 1, BIN);
        Serial.print((0b00000100 & address) >> 2, BIN);
        Serial.print((0b00001000 & address) >> 3, BIN);
        Serial.print(", state: "); Serial.println(state);
       #endif
    }
 
  }

  #ifdef SERIAL_DEBUG
    Serial.print("mux_buffer[0]: "); Serial.println(mux_buffer[0], BIN);
    Serial.print("mux_buffer[1]: "); Serial.println(mux_buffer[1], BIN);
  #endif

  digitalWrite(mux_pin, HIGH); // Disable the multiplexer
  
}
