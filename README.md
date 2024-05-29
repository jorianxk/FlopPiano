# FlopPiano
The Floppy drive piano project.  Using a Raspberry Pi, AVR Micro-controllers and MIDI to play tunes on 3.5" floppy drives. 



# The 3.5" Floppy Drives (Firmware)

The arduino code to run on the Target ATtiny1604 is located in:

>FlopPiano/Microcontrollers/1604_Floppy_Drive_Controller/1604_Floppy_Drive_Controller.ino

This code is intended to run on a ATTINY1604 and generates pulses
to control the SOUND that a floppy drive makes. 
 
We use the 1604's TCA0 timer in single (16 bit) mode with a single
compare (CMP2 & WO2) to generate a dual slope pwm with a pulse width
sutible for the floppy drive (see code comments for details).

The firmware recieves I2C commands from a raspberry pi and reacts
accordingly. (See the onRecieve I2C interupt for details). 
equires megatinycore (see below)
 
 For context see
 - megatinycore https://github.com/SpenceKonde/megaTinyCore
 - ATTINY1604 https://www.microchip.com/en-us/product/attiny1604
 
## Flashing the firmware to an ATtiny1604

1) [Follow the directions for installing Aruino IDE 1.8.13 and megatinycore](https://github.com/SpenceKonde/megaTinyCore#installation)
2) Ensure the megatinycore board manager is selected
    - Tools > Board: > ATtiny1614/1604/...
3) Ensure the chip selection is correct
   - Tools > Chip: > Attiny1604
4) Disable millis()/micros()
    - Tools > millis()/micros(): > Disabled
5) Select the programmer
   1) If using a Uno/Tiny etc as a programmer
      - Tools > Programmer: > jtag3updi
   2) If using a [Adafruit UPDI programmer](https://www.adafruit.com/product/5893)
      - Tools > Programmer > Serial UPDI
6) Select the port of the programmer
   1)  Tools > Port: > [your port here]

Then upload as usual.

**Note: be sure to change the I2C define if you care about the I2c address of the Floppy Controller**


## Helpful Resources
- [Programming the new ATtiny from Arduino using UPDI [Beginner Tutorial]](https://www.youtube.com/watch?v=AL9vK_xMt4E&t=372s)
  
## Notes on the I2C communication (Pi -> Floppy Drive Firmware)

The floppy drive firmware will always receive at least two bytes - at most three

Here is a brief summary of the bytes and what they mean:

### The 'FIRST' Byte

| Upper Nibble | Bit 3 | Bit 2 | Bit 1 | Bit (0) (Least significant bit) |
| :---: | :---: | :---: | :---: | :---: |
| 0000 | 0 | 0 | 0 | 0 |
| Not used | Crash Mode | Crash Mode | Drive Spin | Drive Enable |

**Crash mode** - The two crash mode bits represent which crash mode the drive will use. Two bits combined give four possible states:

| MSB | LSB | Description |
| :---: | :---: | :--- |
| 0 | 0 | Crash prevention OFF |
| 0 | 1 | Crash prevention ON (BOW Mode) |
| 1 | 0 | Crash prevention ON (FLIP Mode) |
| 1 | 1 | Not used (results in crash prevention mode off if set) |
  

**BOW mode**: The drive will step until end of travel then flip direction (like a violin bow changing direction at the end of a bow stroke)

**FLIP mode**: The drive will flip direction after every step/pulse

### The 'SECOND' Byte

The 'SECOND Byte's value is the number of bytes that will follow the 'SECOND Byte'. If we are to recieve two bytes after the 'SECOND Byte', then those two bytes represent the TOP value that should be used for pulse generation. If the 'SECOND Byte's value is <0 or >2 then we do nothing.


### The 'THIRD' and 'FOURTH' byte

The 'THIRD' byte is the upper 8 bits of the 16 bit TOP value. The 'FOURTH' byte is the lower 8 bits of the TOP value.


### I2C General Call

> "In slave mode, it is possible to respond to the general call (0x00) address as well as it's own address (Thanks [@LordJakson](https://github.com/LordJakson)!). This is controlled by the optional second argument to Wire.begin(); If the argument is supplied and true, it will also react to general call commands. These parts"

https://github.com/SpenceKonde/megaTinyCore/blob/master/megaavr/libraries/Wire/README.md

This has been implemented in the Wire.begin() of the floppy firmware. Drives will react to address at 0x00. 


# The Raspberry Pi

## Pi Setup

1) Enable I2C from raspi-confi
2) Enable conposite out from raspi-config
3) Install i2c-tools for i2cdetect
    ```
    $ sudo apt install i2c-tools
    ```
4) Follow [this guide](https://learn.adafruit.com/python-virtual-environment-usage-on-raspberry-pi/basic-venv-usage) to setup and activate python virtual environment. Then:
   1) Install smbus
        ```
        $ pip install smbus
        ```
    2) Install mido 
        ```
        4 pip intall mido
        ```
## Drive Commander 

This module is a utiliy to talk with FlopPiano floppy drive controllers via I2C on a raspberry pi. Using */dev/ic2-1*

### Wiring

**YOU MUST use a [logic level converter](https://www.amazon.com/HiLetgo-Channels-Converter-Bi-Directional-3-3V-5V/dp/B07F7W91LC/ref=sr_1_3?dib=eyJ2IjoiMSJ9.92krL0BEhVOZMobccgCIF2-iXZTiCzICxa8Nt06aO_sNbVFK1Oz6nCSNY72n2sEx6NEhJth2LV3IJX7t-V7cplGsY79Lx85P2MploTMfsoyzvV6U5LPkUiBe5PnCJAeUpOpBa2k1aR3krtMtUJwhVGM0bFVJMPx0rvdaLltg5xUFWOsYj9bxGNCTSFlLrlFFHoKEBlQUfqguuAu9IRG-h12ABkqhTYox_0ysdtGF1RY.LQv_WvZ9BuFQepbX-Qc017OZmLjl5BjVKPrrFXyEJn8&dib_tag=se&keywords=level+shifter&qid=1717016419&sr=8-3)**

Pi Pins
 - GPIO2 (Pin 3) as SDA -> Logic level converter LV1
 - GPIO3 (Pin 5) as SDC -> Logic level converter LV2
 - 3v -> Logic converter level LV
 - GND -> Logic converter level LV GND
  
Attiny1604 pins
 - PB1 as SDA -> Logic level converter HV1
 - PB0 as SDC -> Logic level converter HV2
 - 5v -> Logic converter level HV
 - GND -> Logic converter level HV GND


### Usage
Example:

```
$ python DriveCommader.py
```

Then type the command "help" for more details


# Scratch area


https://asciimatics.readthedocs.io/en/stable/


https://en.wikipedia.org/wiki/Piano_key_frequencies


midi

https://mido.readthedocs.io/
https://www.cs.cmu.edu/~music/cmsip/readings/davids-midi-spec.htm

config and logging

https://docs.python.org/3/library/configparser.html
https://docs.python.org/3/library/logging.html#logging-levels


keys

https://python-evdev.readthedocs.io/en/latest/apidoc.html#module-evdev.ecodes


threading

https://stackoverflow.com/questions/27435284/multiprocessing-vs-multithreading-vs-asyncio



midi over serial:

https://www.youtube.com/watch?v=RbdNczYovHQ&list=PLdo8Yy3t6I_aRZ5J5XFXvSiB4jupAClke&index=4
