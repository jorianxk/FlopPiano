#if defined(MILLIS_USE_TIMERA0) || defined(__AVR_ATtinyxy2__)
  #error "This sketch takes over TCA0, don't use TCA0 for millis()/micros()"
#endif

#include <math.h>
#include <Wire.h>


#define I2C_ADDR 8
#define DEVICE_TYPE 69

#define ALPHA 2500000
#define STEP_LIMIT 80
#define STEP_PULSE_WIDTH 10

#define ENABLE_PIN PIN_PA1 
#define STEP_PIN   PIN_PB2
#define DIR_PIN    PIN_PA6 
#define SPIN_PIN   PIN_PA7

#define CTRL_REG 0
#define FREQ_REG 1
#define MOD_RATE_REG 2
#define MOD_FREQ_REG 3
#define DEVICE_TYPE_REG 4

#define CTRL_EN   0b00000001
#define CTRL_SPIN 0b00000010 
#define CTRL_BOW  0b00000100

#define CTRL_EN_MASK   0b00010000
#define CTRL_SPIN_MASK 0b00100000 
#define CTRL_BOW_MASK  0b01000000


// Current crash mode set by I2C
volatile bool bow = false; // true = bow mode, false = flip mode

// A count for how many step pulses have occurred
volatile byte stepCount = 0; // Counts to STEP_LIMIT then resets

// Arbitrary direction for stepping
volatile bool dir = false; // flops when stepCount == STEP_LIMIT


// The commanded frequency received via I2C
volatile union floatToBytes {  
    char bytes[4];
    float toFloat;  
}commandedFreq;


// The frequency that is currently being played
float currentFreq = 440.0;

// Stuff for modulation TODO
volatile byte modRate = 1; // Set via I2C defaults to 1hz
volatile unsigned long modFreq = 0; // Set via I2C
bool modFreqChanged = false;
unsigned long startTime = 0;
bool modFlip = false;




void setup() {
  pinMode(STEP_PIN, OUTPUT);
  pinMode(ENABLE_PIN, OUTPUT);
  pinMode(SPIN_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);


  digitalWrite(ENABLE_PIN, HIGH); // normally high (Active low) drive disabled
  digitalWrite(SPIN_PIN, HIGH);   // normally high (Active low) disk spin off;
  digitalWrite(DIR_PIN, dir);     // Arbitrary drive start direction
  
  takeOverTCA0();
  TCA0.SINGLE.CTRLB = (TCA_SINGLE_CMP2EN_bm | TCA_SINGLE_WGMODE_DSBOTTOM_gc);
  //Setup TCA0 to play the staring frequency
  updateFreq(currentFreq);

  TCA0.SINGLE.INTCTRL = TCA_SINGLE_OVF_bm; //enable overflow interrupt
  TCA0.SINGLE.CTRLA = (TCA_SPLIT_CLKSEL_DIV4_gc | TCA_SINGLE_ENABLE_bm); 

  Wire.begin(I2C_ADDR, true);              
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
}

void loop() {

  // Check to see we've been commanded to change frequency
  if (currentFreq != commandedFreq.toFloat){
    if(updateFreq(commandedFreq.toFloat)){
      // The frequency was successfully set, so update the current frequency
      currentFreq = commandedFreq.toFloat;
    }
  }

  // Do modulation with a simple triangle wave generator
  if (modFreq!=0){
     if ((micros() - startTime) >= modFreq){
      if (modFlip){
        updateFreq(currentFreq);
      }else{
        updateFreq(currentFreq+modRate);
      }
      modFlip = (!modFlip);
      modFreqChanged = true; 
      startTime = micros();
    }
  }else{
    // ensures that after modulation is disabled the frequency returns back to 
    // normal
    if (modFreqChanged){
      updateFreq(currentFreq);
      modFreqChanged = false;
    }
  }
  
}


void receiveEvent(int numBytes) {
  // The first byte is the number of the register that the master wants to write
  // to
  byte regNumber = Wire.read(); 

  if (regNumber == CTRL_REG){
    // There should only be one byte to read (for the CTRL register). If not do 
    // nothing
    if (Wire.read() == 1){
      byte CTRL = Wire.read();

      // Should act on the the enable bit? 
      if (CTRL & CTRL_EN_MASK){        
        // Immediately update the enable pin
        // Since the enable pin is active low we must 'not' the result with 
        // ^(XOR)
        digitalWrite(ENABLE_PIN, ((CTRL & CTRL_EN) ^ 1));  
      }

      // Should act on the the spin bit? 
      if (CTRL & CTRL_SPIN_MASK){
        // Immediately update the spin pin
        // Shift the SPIN bit over by one and active low we must 'not' the 
        // result with ^(XOR)
        digitalWrite(SPIN_PIN, ((CTRL & CTRL_SPIN) >> 1) ^ 1); 
        
      }

      // Should act on the the bow bit? 
      if (CTRL & CTRL_BOW_MASK){
        // Set the bow state
        bow = bool((CTRL & CTRL_BOW) >> 2);
      }
    }    
    
  }
  else if (regNumber == FREQ_REG){
    // There should be 4 bytes to read (for the frequency register). If not do 
    // nothing
    if (Wire.read() == 4){
      //Read the bytes and store them in commandFreq
      commandedFreq.bytes[0] = Wire.read();
      commandedFreq.bytes[1] = Wire.read();
      commandedFreq.bytes[2] = Wire.read();
      commandedFreq.bytes[3] = Wire.read();
    }
    
  }
  else if (regNumber == MOD_RATE_REG){
     // There should only be one byte to read (for the mod rate register). If 
     // not do nothing
     if (Wire.read() == 1){
        byte proposedRate = Wire.read();
        //Don't let modRate be zero - it won't sound like modulation if == 0
        if (proposedRate != 0){
          modRate = proposedRate;
        }
     }
  }
  else if (regNumber == MOD_FREQ_REG){
     // There should only be one byte to read (for the mod freq register). If 
     // not do nothing
     if (Wire.read() == 1){
        byte proposedFreq = Wire.read();
        //Start/Restart the modulation
        if (proposedFreq == 0){
          modFreq = 0;
        }
        else{
          modFreq = 1000000 / (2*proposedFreq);
          startTime = micros();
        }
     }
    
  }else{
    //Do nothing
  }

  //If there are any remaining bytes just read them and do nothing.
  while (Wire.available()){Wire.read();}
}


void requestEvent(){
  // The first byte is the number of the register that the master wants to read 
  // from
  byte regNumber = Wire.read();
  Wire.write(DEVICE_TYPE);
  //Only reply when the master wants to read from register 4
  if (regNumber == DEVICE_TYPE_REG){
    Wire.write(DEVICE_TYPE);    
  }
}


//This interrupt is fired when a step pulse is generated
ISR(TCA0_OVF_vect) {
  // On a step pulse increment the step count
  // We do this every time regardless of CRASH mode just so we're doing roughly
  // the same mem read/writes regardless of crash mode. it also helps in
  // Transitioning between crash modes
  stepCount++; 

  // If we have reached the step limit we need to reset the step count
  if(stepCount >= STEP_LIMIT){
    stepCount = 0;
    // If we reached the step limit and bow mode is on then we need 
    // to flip the drive step direction 
    if (bow){changeDirection();}        
  }

  //If the drive not in bow mode just change the direction
  if (!bow){changeDirection();}   

  //Always clear the interupt flags
  TCA0.SINGLE.INTFLAGS  = TCA_SINGLE_OVF_bm; 
}


// A convenience funtion to change the drive's step direction
void changeDirection(){
  dir = !dir; // Flip the direction
  digitalWrite(DIR_PIN, dir); //Write the direction 
}


/* Sets up the TCA0 to generate the correct pulses so that the drive 
 * plays the frequency specified in by the freq parameter.
 * 
 *  Returns true if the freq given resulted in a valid TCA0 configuration.
 *    Meaning the frequency was successfully changed and will play.
 *  Returns false if the freq given resulted in an invalid TCA0 configuration.
 *    Meaning the frequency was not updated and no change will occur. 
*/ 
bool updateFreq(float freq){
  // Calculate the proposed top for the timer must be 16 bit value
  unsigned int TOP = round(ALPHA/freq);
  
  // Check to see if the top is valid (will not break the step pulse width or 
  // be larger than a 16 bit value)
  if (TOP < (STEP_PULSE_WIDTH+1) || TOP > 65535){return false;}

  // Don't change the top if we're already set to that value. But return true
  // to indicate that the frequency is playing
  if (TOP == TCA0.SINGLE.PER){return true;}
  
  // Update the timer's max count value with the new TOP (Changes the frequency)
  TCA0.SINGLE.PER = TOP;
  // Compare two sets the pulse width. According the floppy drive documentation 
  // the pulse width should be ~0.8us to 3ms. 
  TCA0.SINGLE.CMP2 = TOP - STEP_PULSE_WIDTH;
  // TCA0 setup correctly 
  return true;
}