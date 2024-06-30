


#if defined(MILLIS_USE_TIMERA0) || defined(__AVR_ATtinyxy2__)
  #error "This sketch takes over TCA0, don't use TCA0 for millis()/micros()"
#endif
#include <math.h>
#include <Wire.h>

// Slave I2C of this device
#define I2C_ADDR 8

// The maximimum steps before changing step direction in CRASH_BOW mode
#define STEP_LIMIT 80 
// Value used to calculate the step pulse width.
#define STEP_PULSE_WIDTH 10 // 10 results in ~1 us (Value depends on prescalor)

// GENERAL WARNING: DO NOT USE PBA0/Chip pin 10/ Arduino pin/11
// PBA0 is the UPDI programming pin. if set to be I/O you will need a high
// voltage programmer to reprogram the board.
#define ENABLE_PIN PIN_PA1 // AKA Drive Select pin - CHIP pin 11
#define STEP_PIN   PIN_PB2 // DO NOT CHANGE - CHIP Pin 7 
// This above pin is for WO2 and TCA0 CMP2 (drive step/ frequency generation) 
#define DIR_PIN    PIN_PA6 // Drive Direction pin - CHIP pin 4
#define SPIN_PIN   PIN_PA7 // Drive Spin pin - CHIP Pin 5

// These are bit-masks for decoding the CTRL register I2C commands
#define CTRL_ENABLE_bm 0b00000001
#define CTRL_SPIN_bm   0b00000010 
#define CTRL_CRASH_bm  0b00001100 

//These are for changing the crash mode behavior
//#define CRASH_OFF 0b00
#define CRASH_BOW 0b01
#define CRASH_FLIP 0b10
//#define #CASH_UNUSED 0b11

// A byte to hold incomming I2C state changes
// We can think of this as a single 8-bit register 
// named CTRL (short for control)
volatile byte CTRL = 0b00001000; //By default crash prevention is in FLIP MODE

// Default TOP Value that we count up to. When this value is commaned to change
// via I2C it results in a change of drive note frequency. The math to determine
// what TOP value to use is done on the Raspberry Pi.
volatile unsigned int TOP = 19111; // default value = C4 middle C ~ 261.63 Hz

// A variable to hold the number of pulses or steps sent to the drive.
// if in CRASH_BOW mode when stepCount >= STEP_LIMIT the drive's 
// step direction will be flipped, then stepCount will be reset to zero.
volatile byte stepCount = 0;

//the current direction of the drive
volatile bool dir = false;


//Setup all the things!
void setup() {
  // Setup all the pins
  pinMode(STEP_PIN, OUTPUT);
  pinMode(ENABLE_PIN, OUTPUT);
  pinMode(SPIN_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);

  // Start up pin states
  digitalWrite(ENABLE_PIN, HIGH); // normally high (Active low) drive disabled
  digitalWrite(SPIN_PIN, HIGH);   // normally high (Active low) disk spin off;
  digitalWrite(DIR_PIN, dir);     // Arbitary drive start direction


  // Timer setup - for drive step/note generation
  // Take over the timer as recomended by megatinycore documentation 
  takeOverTCA0();
  // Set Timer A (TCA0) to Dual slope PWM mode, OVF interrupt at BOTTOM, PWM on WO2 (CMP2)
  TCA0.SINGLE.CTRLB = (TCA_SINGLE_CMP2EN_bm | TCA_SINGLE_WGMODE_DSBOTTOM_gc);
  // Set TOP value (The value we count up to)
  TCA0.SINGLE.PER = TOP;
  // This sets the pulse width currently 
  TCA0.SINGLE.CMP2 = TOP - STEP_PULSE_WIDTH;
  // Enable interupt timer to handle crash modes
  TCA0.SINGLE.INTCTRL = TCA_SINGLE_OVF_bm; //enable overflow interrupt
  // Enable timer A (TCA0) with prescaler 4
  TCA0.SINGLE.CTRLA = (TCA_SPLIT_CLKSEL_DIV4_gc | TCA_SINGLE_ENABLE_bm); 

  // Join I2C bus as slave with address I2C_ADDR the second parameter (true)enables
  // receiving general broadcasts to I2C address 0x00. This is so we can command all
  // the drives at once if necessary 
  Wire.begin(I2C_ADDR, true);
  //Call receiveEvent when data received                
  Wire.onReceive(receiveEvent);
}

void receiveEvent(int numBytes) {
  // We will always recive at least two bytes - at most three
  /*
   * |------------------------------------------------------------------|
   * |                   The 'FIRST Byte' - CTRL byte                   |
   * |------------------------------------------------------------------|
   * |   0000   |     0      |       0      |      0     |      0       |
   * |----------|------------|--------------|---------------------------|
   * | Not used | Crash Mode |  Crash Mode  | Drive Spin | Drive Enable |
   * |------------------------------------------------------------------| 
   * 
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
   *  
   *  Drive Spin - if the bit is 1, the SPIN_PIN is pulled HIGH. 0 
   *  SPIN_PIN is pulled LOW. This is to turn on/off disc spin.
   *  
   *  Drive Enable - if the bit is high then the drive select/enable 
   *  (ENABLE_PIN) pin is pulled LOW (because the drives are active low) 
   *  and the drive is selected/enabled. If 0, then then the ENABLE_PIN
   *  is pulled HIGH and the drive is de-selected/disabled.
   */
  //Get the 'FIRST Byte' it's the CTRL register write values (see above)
  CTRL = Wire.read(); //Store CTRL register
  
  // Since the enable pin is active low we must 'not' the result with ^(XOR) 
  digitalWrite(ENABLE_PIN, ((CTRL & CTRL_ENABLE_bm) ^ 1));
  // Shift the SPIN bit over by one and active low we must 'not' the result with ^(XOR) 
  digitalWrite(SPIN_PIN,((CTRL & CTRL_SPIN_bm) >> 1) ^1);    
  
  // Note Crash mode is handled in the ISR(TCA0_OVF_vector) function but, this is how
  // We handle it: Shift the Crash bit over by 2 
  // ((CTRL & CTRL_CRASH_bm) >> 2) == CRASH_MODE

  /*  |----------------------------------------------------------------|
   *  |      The 'SECOND Byte' - the number of bytes to follow         |
   *  |----------------------------------------------------------------| 
   */ 

  /* 
   * That is, the 'SECOND Byte's value is the number of bytes that will follow the 
   * 'SECOND Byte'. If we are to recieve two bytes after the 'SECOND Byte', then those 
   * two bytes represent the TOP value that should be used for pulse generation. If the 
   * 'SECOND Byte's value is <0 or >2 then we do nothing.
   */
   
  // 'SECOND Byte's value is 2, we need to use the next two bits as the TOP value
  if(Wire.read() == 2){
    // The first of the bytes following the 'SECOND Byte' is the upper 8 bits
    // of the 16 bit TOP value. The next byte is the lower 8 bits of the TOP value.
    // So we shift the upper bytes, then OR it with the lower byte.
    TOP = (Wire.read()<< 8) | Wire.read();
    // Update the timer's max count value with the new TOP
    TCA0.SINGLE.PER = TOP;
    // Compare two sets the pulse width. According the floppy drive documentation the 
    // Pulse width should be ~0.8us to 3ms. 
    TCA0.SINGLE.CMP2 = TOP - STEP_PULSE_WIDTH;
  }

  //If there are any remaining bytes just read them and do nothing.
  while (Wire.available()){Wire.read();}
}


//This interrupt is fired when a step pulse is generated
ISR(TCA0_OVF_vect) {
  //On a step pulse increment the step count
  //We do this every time regardless of CRASH mode just so we're doing roughly
  //the same mem read/writes regardless of crash mode. it also helps in
  //Transitioning between crash modes
  stepCount++; 

  // If we have reached the step limit we need to reset the step count
  if(stepCount >= STEP_LIMIT){
    stepCount = 0;
    // If the reached the step limit and we;re CRASH bow mode is on, then we need 
    // to flip the drive step direction 
    // (see receiveEvent(int numBytes) - The 'FIRST Byte')
    if (((CTRL & CTRL_CRASH_bm) >> 2) == CRASH_BOW){
      changeDirection(); //Change the direction of the drive
    }   
  }

  //If the drive is in CRASH flip mode we need to just change the direction step
  if (((CTRL & CTRL_CRASH_bm) >> 2) == CRASH_FLIP){
    changeDirection();
  }   
  
  
  // Always remember to clear the interrupt flags, otherwise the interrupt will fire 
  // continually!
  TCA0.SINGLE.INTFLAGS  = TCA_SINGLE_OVF_bm; 
}


// A convenience funtion to change the drive's step direction
void changeDirection(){
  dir = !dir; // Flip the direction
  digitalWrite(DIR_PIN, dir); //Write the direction 
}

// Nothing to see here
void loop() {}
