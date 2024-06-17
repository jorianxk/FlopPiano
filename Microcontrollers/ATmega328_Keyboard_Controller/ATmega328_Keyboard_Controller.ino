/*
 * FlopPiano - Keyboard input controller sketch.
 * Version 0.9
 * 
 * 2024-06-014
 * Jacob Brooks, Jorian Khan
 * 
 *                      
 * This code is intended to run on a ATmega328p (Uno or Nano) and return the key input 
 * states and display status LEDs of piano keys, modulation, and pitchbend wheel via I2C
 *
 * 
 */

 
#include <Wire.h>

//#define SERIAL_DEBUG // if defined, debug information will be printed to serial
//#define HANG_DEBUG   // if defined, loop() will hang after one loop() cycle - for debug 
//#define TEST_PATTERN   // if defined key_states will not read, rather a test pattern will be ouput


#define I2C_ADDR 0x77 //The I2C for this device, RPi expects to get keyboard data on 

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
#define MUTE_LED_PIN         10 // Pin for Mute button backlight
#define OCTIVE_UP_LED_PIN    11 // Pin for Octave up button backlight
#define OCTIVE_DOWN_LED_PIN  12 // Pin for Octave down button backlight
#define OCTAVE_LED_SH_CP_PIN 13 // Pin for Octave LED shift register clock
#define OCTAVE_LED_ST_CP_PIN A2 // Pin for Octave LED shift register latch
#define OCTAVE_LED_DS_PIN    A3 // Pin for Octave LED shift register data serial input



// Function prototypes
// Reads all the key states and stores them in key_states
void readInputStates();

// Reads all states of a 16 channel multiplexer and stores them in mux_buffer
unsigned int readMux(int);

// Writes all LED states according to ctrl
void writeOutputStates();

#ifdef TEST_PATTERN
  void testPattern();
  bool toggle_pattern = false;
#endif




// An array to hold the incoming CTRL byte
byte ctrl = 0; 

//array to to hold all input states
byte input_states[9] = {1, 0, 1, 0, 1, 0, 1, 0, 1};  

// a buffer to hold the multiplexer states
byte mux_buffer[2] = {0,0}; 

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

  // Read all the input (button & wheels) states and store them in input_states  
  #ifdef TEST_PATTERN
    testPattern();
  #else
    readInputStates();
  #endif
  
  // Write all the LED states
  writeOutputStates();



  #ifdef SERIAL_DEBUG
    Serial.print("Latest CTRL: "); Serial.println(ctrl, BIN);
    
    Serial.println("Latest Input States: ***************************************************");
    for (int i=0; i<9; i++){
      Serial.println(input_states[i], BIN);
    }
  #endif 
  

  #ifdef HANG_DEBUG
    while(1);
  #endif

}


void recieveEvent(){ctrl = Wire.read();}
void requestEvent(){Wire.write(input_states,9);}

void readInputStates(){
  // Read key states
  readMux(MUX_0_ENA_PIN);
  input_states[0] = mux_buffer[0]; // KEY_1 - KEY_8
  input_states[1] = mux_buffer[1]; // KEY_9 - KEY_16

  readMux(MUX_1_ENA_PIN);
  input_states[2] = mux_buffer[0]; // KEY_17 - KEY_24
  input_states[3] = mux_buffer[1]; // KEY_25 - KEY_32

  readMux(MUX_2_ENA_PIN);
  input_states[4] = mux_buffer[0]; // KEY_33, MUTE, OCTAVE_UP, OCTAVE_DOWN, ..., ..., ..., ...
  //mux_buffer[1] We don't use the second 8 channels on the third multipexer

  // Read pitch wheel
  unsigned int pitch = analogRead(PITCH_PIN);
  input_states[5] = (pitch >> 8); // PITCH upper byte
  input_states[6] = pitch;        // PITCH lower byte
  
  // Read modulation wheel
  unsigned int mod = analogRead(MOD_PIN);
  input_states[7] = (mod >> 8); // MOD upper byte
  input_states[8] = mod;        // MOD lower byte

}

// Reads all states of a 16 channel multiplexer and stores them in mux_buffer
// mux_buffer[0] will contain key states from mux addresses 0-7
// mux_buffer[1] will contain key states from mux addresses 8-15
unsigned int readMux(int mux_pin){
  #ifdef SERIAL_DEBUG 
    Serial.println("************************************");
    Serial.print("Reading multiplexor on pin "); Serial.println(mux_pin);
  #endif
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
      
      #ifdef SERIAL_DEBUG
        Serial.print("Address: "); Serial.print(address);
        Serial.print(", bin: ");
        Serial.print((0b00000001 & address) >> 0, BIN);
        Serial.print((0b00000010 & address) >> 1, BIN);
        Serial.print((0b00000100 & address) >> 2, BIN);
        Serial.print((0b00001000 & address) >> 3, BIN);
        Serial.print(", key_state: "); Serial.println(key_state);
       #endif
    }
 
  }

  #ifdef SERIAL_DEBUG
    Serial.print("mux_buffer[0]: "); Serial.println(mux_buffer[0], BIN);
    Serial.print("mux_buffer[1]: "); Serial.println(mux_buffer[1], BIN);
  #endif

  digitalWrite(mux_pin, HIGH); // Disable the multiplexer
}

void writeOutputStates(){
  // Update simple LEDs
  digitalWrite(MUTE_LED_PIN,        (0b00100000 & ctrl) >> 5);
  digitalWrite(OCTIVE_UP_LED_PIN,   (0b00010000 & ctrl) >> 4);
  digitalWrite(OCTIVE_DOWN_LED_PIN, (0b00001000 & ctrl) >> 3);


  // Update Octave number indicator LEDs
  //Pull the latch pin low, so LED's don't change while shifting
  digitalWrite(OCTAVE_LED_ST_CP_PIN, LOW);
  //octave number   ->(0b00000111 & ctrl)  
  //number to shift -> (1 << octave number)  
  // shift out the bits:  
  shiftOut(OCTAVE_LED_DS_PIN, OCTAVE_LED_SH_CP_PIN, MSBFIRST, 1 << (0b00000111 & ctrl));
  //Pull the latch pin high, so LED's will light  
  digitalWrite(OCTAVE_LED_ST_CP_PIN, HIGH);  
}


#ifdef TEST_PATTERN
void testPattern(){
    if (toggle_pattern){
      input_states[0] = 0b11110000;
      input_states[1] = 0b00001111;
      
      input_states[2] = 0b10101010;
      input_states[3] = 0b01010101;
      
      input_states[4] = 0b11000011;
      
      input_states[5] = 0b00110011;
      input_states[6] = 0b11001100;
      
      input_states[7] = 0b01111110;      
      input_states[8] = 0b10000001;

    }
    else{
      input_states[0] = 0b00001111;
      input_states[1] = 0b11110000;
      
      input_states[2] = 0b01010101;
      input_states[3] = 0b10101010;
      
      input_states[4] = 0b00111100;
      
      input_states[5] = 0b11001100;      
      input_states[6] = 0b00110011;
      
      input_states[7] = 0b10000001;
      input_states[8] = 0b01111110;
    }
    toggle_pattern = !toggle_pattern;
}
#endif
