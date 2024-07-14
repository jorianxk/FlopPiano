# FlopPiano #
An electronic keyboard that makes music using 3.5" floppy drives.  
Using a Raspberry Pi, AVR Micro-controllers and MIDI to play tunes on 3.5" floppy drives. 

**TODO: Photos and videos**

## Why? ##
**TODO: update link**

Read Jacob Brooks' rational [here]()

## How? ##
The FlopPiano is built using attiny1604s that generate waveforms that make 3.5" floppy drives sound notes. 

The attiny drive firmware (arduino sketch) supports setting drive frequency, modulation frequency, and modulation attack (or rate) via I2C (via python module Smbus2)

A simple python module (floppiano) orchestrates controlling floppy drives, handling reading/writing to MIDI interfaces, interpreting/playing .mid files on drives, and serves a simple (yet vintage inspired) command line interface.

# Getting Started #

<!-- TOC -->

- [FlopPiano](#floppiano)
    - [Why?](#why)
    - [How?](#how)
- [Getting Started](#getting-started)
    - [Required Materials](#required-materials)
    - [Hardware and Wiring](#hardware-and-wiring)
        - [Flashing the Drive Controllers](#flashing-the-drive-controllers)
        - [Preparing the Keyboard](#preparing-the-keyboard)
        - [Configuring the Raspberry Pi](#configuring-the-raspberry-pi)
            - [A Full Installation with HyperPixel display](#a-full-installation-with-hyperpixel-display)
            - [A minimal installation No HyperPixel display](#a-minimal-installation-no-hyperpixel-display)
    - [Configuring Python and floppiano](#configuring-python-and-floppiano)
        - [Quick installation Linux only](#quick-installation-linux-only)
        - [Manual installation](#manual-installation)
    - [Startup](#startup)
        - [Full installations With HyperPixel Display](#full-installations-with-hyperpixel-display)
        - [Minimal installations No HyperPixel Display](#minimal-installations-no-hyperpixel-display)
        - [Usage Warnings & Usage FAQ](#usage-warnings--usage-faq)
            - [Running via ssh or in windowed terminal](#running-via-ssh-or-in-windowed-terminal)
            - [Failing to find floppy drives](#failing-to-find-floppy-drives)
            - [Failing to find a keyboard](#failing-to-find-a-keyboard)
            - [Failing to find MIDI Interfaces](#failing-to-find-midi-interfaces)
            - [I don't want to use a keyboard or MIDI interfaces](#i-dont-want-to-use-a-keyboard-or-midi-interfaces)
            - [See the CLI help menu for more startup flags](#see-the-cli-help-menu-for-more-startup-flags)
    - [See Also](#see-also)
        - [Python Dependencies](#python-dependencies)
        - [About MIDI](#about-midi)

<!-- /TOC -->

## Required Materials ##

**TODO: Complete this**

1) A Rasberry Pi single board computer
2) A attiny1604 and [driver board]() per floppy drive desired
3) If you intend to send MIDI from a DAW or MIDI device, a [USB MIDI Interface](https://www.amazon.com/dp/B0B2JZL5LW?psc=1&ref=ppx_yo2ov_dt_b_product_details)
4) A (logic level converter) [https://www.amazon.com/gp/product/B0CKCQDH7N/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1]
5) An approrate [power supply]()
6) If running a full installation a display. ([HyperPixel 4 Square](https://learn.pimoroni.com/article/getting-started-with-hyperpixel-4) is recommended)


## Hardware and Wiring ##

**TODO: All wiring and board documentation below is old documentation**

**Use a [logic level converter](https://www.amazon.com/HiLetgo-Channels-Converter-Bi-Directional-3-3V-5V/dp/B07F7W91LC/ref=sr_1_3?dib=eyJ2IjoiMSJ9.92krL0BEhVOZMobccgCIF2-iXZTiCzICxa8Nt06aO_sNbVFK1Oz6nCSNY72n2sEx6NEhJth2LV3IJX7t-V7cplGsY79Lx85P2MploTMfsoyzvV6U5LPkUiBe5PnCJAeUpOpBa2k1aR3krtMtUJwhVGM0bFVJMPx0rvdaLltg5xUFWOsYj9bxGNCTSFlLrlFFHoKEBlQUfqguuAu9IRG-h12ABkqhTYox_0ysdtGF1RY.LQv_WvZ9BuFQepbX-Qc017OZmLjl5BjVKPrrFXyEJn8&dib_tag=se&keywords=level+shifter&qid=1717016419&sr=8-3)**

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


### Flashing the Drive Controllers ###

The arduino code to run on the target ATtiny1604 is located in:

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
 

Flashing:

1) [Follow the directions for installing Aruino IDE 1.8.13 and megatinycore](https://github.com/SpenceKonde/megaTinyCore#installation)
2) Ensure the megatinycore board manager is selected
    - Tools > Board: > ATtiny1614/1604/...
3) Ensure the chip selection is correct
   - Tools > Chip: > Attiny1604
4) Set millis()/micros() to TCB0
    - Tools > millis()/micros(): > TCB0
5) Select the programmer
   1) If using a Uno/Tiny etc as a programmer
      - Tools > Programmer: > jtag3updi
   2) If using a [Adafruit UPDI programmer](https://www.adafruit.com/product/5893)
      - Tools > Programmer > Serial UPDI
6) Select the port of the programmer
   1)  Tools > Port: > [your port here]
7) Change the I2C address to a valid, unique address (range [8-119]) 
```
 #define I2C_ADDR [ADDRESS HERE]
```
8) Then upload as usual.

**Note: be sure to change the I2C define. Each drive must have a valid non-conflicting I2C Address**

### Preparing the Keyboard ###

**TODO:**

### Configuring the Raspberry Pi ###

The **floppiano** python module is intended to run on a *headless* Raspberry Pi equipped with a [HyperPixel](https://learn.pimoroni.com/article/getting-started-with-hyperpixel-4) square display. That's right a *headless* installation *with* a  display. 

It's because the 'GUI' is actually built upon [asciimattics](https://asciimatics.readthedocs.io/en/stable/) to provide a vintage computing feel. 

However, floppiano can be configured to run via ssh or in a standard desktop OS installation. 

After flashing Raspberry Pi OS with your desired settings see the sections below to configure the Raspberry Pi.

>Tip: Be sure to pull the latest software via apt before continuing

```
$ sudo apt update
$ sudo apt upgrade
```

#### A Full Installation (with HyperPixel display) ####

1) Follow the directions on [Pimorroni](https://learn.pimoroni.com/article/getting-started-with-hyperpixel-4) to setup up the display ([see also](https://github.com/pimoroni/hyperpixel4/issues/177))
2) After getting the display working we need to enable, then disable the I2C bus in raspiconfig **via ssh**. This allows us to use the alternative I2C the HyperPixel Display. 
   1) ```$sudo raspi-config```
   2) Interface Options>I2C>Enable. THIS WILL BREAK the display.
   3) ```$sudo reboot now```
   4) After reboot re-disable the I2C Bus
   5) ```$sudo raspi-config```
   6) Interface Options>I2C>Disable.
   7) ```$sudo reboot now```
   8) After reboot verify that the alternative I2C bus is working.
      ```
      $ ls /dev
      ```
      Should show:
      ```
      i2c-20
      i2c-21
      i2c-22
      ```
      From our experience devices connect to the HyperPixel display show up on bus number 22

      >Tip: The software package 'i2c-tools' is usefully for troubleshooting the I2C bus. Specifically the "i2cdetect" command

      Should yield all the devices visible on the bus ex:
      ```
      $ sudo apt install i2c-tools
      $ i2cdetect -y 22
         0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
      00:                         08 09 0a 0b 0c 0d 0e 0f 
      10: 10 11 -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
      20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
      30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
      40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
      50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
      60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
      70: -- -- -- -- -- -- -- -- 
      ``` 
3) (Optional) Enable a larger console font.
   ```
   $ sudo dpkg-reconfigure console-setup
   ```
   Our recommendation is to pick a UTF-8 font that is easily visible to you

#### A minimal installation (No HyperPixel display) ####

A minimal installation is much easier. After setting up the Pi just enable the I2C bus and reboot

   1) ```$sudo raspi-config```
   2) Interface Options>I2C>Enable. 
   3) ```$sudo reboot now```

>Tip: Its a good idea to check the I2C bus for your devices. Using any method described above to do so

## Configuring Python and floppiano ##

Raspberry Pi OS really wants python users to use virtual environments so we must first make sure that the python3-venv package is installed:

```
$sudo apt install python3-venv
```

After installing venv we can clone the Floppiano repo to get the floppiano package

```
$git clone git@github.com:jorianxk/FlopPiano.git
Cloning into 'FlopPiano'...
```

### Quick installation (Linux only) ###

If you aren't familiar with python virtual environments there is a convenient install script to setup the virtual environment and install python dependencies 

After cloning the repo:
```
~$ cd FlopPiano
~/FlopPiano$ ./install.sh
```
You should see an output like:

```
[FlopPiano Install]: Creating environment in ~/FlopPiano/env...
[FlopPiano Install]: Done.
[FlopPiano Install]: Activating environment...
[FlopPiano Install]: Done.
[FlopPiano Install]: Installing dependency smbus2...
...
[FlopPiano Install]: Done.
[FlopPiano Install]: Installing dependency mido[ports-rtmidi]...
...
[FlopPiano Install]: Done.
[FlopPiano Install]: Installing dependency asciimatics...
...
[FlopPiano Install]: Done.
```

### Manual installation ###

After cloning the repo:

1) Create the python virtual environment in FlopPiano/env/ then activate it
   ```
   ~$ cd FlopPiano
   ~/FlopPiano$ python3 -m venv env
   ~/FlopPiano$ source env/bin/activate
   (env):~/FlopPiano$
   ```

2) Install the dependencies in the virtual environment via pip
   ```
   (env):~/FlopPiano$ pip install smbus2
   ...
   (env):~/FlopPiano$ pip install mido[ports-rtmidi]
   ...
   (env):~/FlopPiano$ pip install asciimatics
   ...
   ```

## Startup ##

***Since Raspberry Pi OS really wants python users to use virtual environments, the virtual environment need to be activated before running the floppiano.main python entry point.***

If you are on linux a convenience script is available that starts everything up for you. For example we can show the floppiano help menu by:

```
~/FlopPiano$ ./run.sh -h
usage: main.py [-h] [-nk] [-db] [-bn BUSNUM] [-np]
               [-t {default,monochrome,green,bright,warning}] [-ns] [-st TIME] [-lf FILE]
               [-ll LEVEL]

options:
  -h, --help            show this help message and exit
  -nk, --nokeyboard     Disables the piano keys
  -db, --debugbus       Use the dummy (debug) I2C bus
  -bn BUSNUM, --busnumber BUSNUM
                        Specifies The I2C Bus number (effective only if -db is not given)
  -np, --noports        Disables MIDI interfaces
  -t {default,monochrome,green,bright,warning}, --theme {default,monochrome,green,bright,warning}
                        Specifies the UI theme
  -ns, --nosplash       Disables the splash screen
  -st TIME, --screentimeout TIME
                        Specifies screensaver timeout in seconds. 0=off
  -lf FILE, --logfile FILE
                        Specifies a logfile to use
  -ll LEVEL, --loglevel LEVEL
                        Specifies a loglevel to use (effective only if -lf is given).
```

You can also run the main entry point of the floppiano module via python after the environment is activated:

```
~/FlopPiano$ source env/bin/activate
(env):~/FlopPiano$ python -m floppiano.main -h
```

The output will be the same help message as previous.


### Full installations (With HyperPixel Display) ###

If you're running a full installation, no special arguments are necessary.

Simply run floppiano via the convenience script or via "python -m" (The default arguments should work if your system is configured correctly.)

For example:
```
~/FlopPiano$ ./run.sh
```

**OR**
```
~/FlopPiano$ source env/bin/activate
(env):~/FlopPiano$ python -m floppiano.main
```

### Minimal installations (No HyperPixel Display) ###

For a minimal installation a special argument must be given. That is we must tell the floppiano module to use the i2c bus /dev/i2c-1.

This can be done by using the --busnumber argument with run.sh or python.



For example:
```
~/FlopPiano$ ./run.sh --busnumber 1
```

**OR**

```
~/FlopPiano$ source env/bin/activate
(env):~/FlopPiano$ python -m floppiano.main --busnumber 1
```

### Usage Warnings & Usage FAQ ###

#### Running via ssh or in windowed terminal ###
- Resizing the terminal window will force floppiano to exit

#### Failing to find floppy drives ####
- By default the floppiano startup routine will attempt to find both drives and the keyboard on the I2C bus. If no drives are found the floppiano startup will ask/prompt to use a dummy (debug) I2C bus. While using the debug bus, floppiano won't actually read/write to the real I2C bus (including not reading the keyboard state). But the 'UI' will run and a warning will be shown

#### Failing to find a keyboard ####
- If no keyboard is auto-detected, floppiano will prompt to continue without it. Continuing will not affect I2C communication with drives (just the keyboard will not work). If you intend to run floppiano without a keyboard use the startup argument '--nokeyboard' and the floppiano startup will skip the keyboard check

#### Failing to find MIDI Interfaces ####
- If no input/output MIDI interfaces are detected on startup floppiano will prompt to continue without them. If it's your intention not to use the MIDI interface then use the startup argument --noports and floppiano will skip the interface check. 

#### I don't want to use a keyboard or MIDI interfaces ####

Likely you'd like to just play .mid files or just test drive sound.

You can skip using MIDI interfaces and/or the keyboard using startup arguments. 

For example, to skip MIDI interface and keyboard checks use floppiano with:

```
~/FlopPiano$ ./run.sh --noports --nokeyboard
```

OR

```
~/FlopPiano$ source env/bin/activate
(env):~/FlopPiano$ python -m floppiano.main --noports --nokeyboard
```

#### See the CLI help menu for more startup flags ####

Many other useful startup flags can be set. Use -h or --help for details.

```
~/FlopPiano$ ./run.sh --help
```
OR

```
~/FlopPiano$ source env/bin/activate
(env):~/FlopPiano$ python -m floppiano.main --help
```


## See Also ##


### Python Dependencies ###
1) [mido](https://mido.readthedocs.io/) - a wonderful midi library that made this project possible
2) [asciimatics](https://asciimatics.readthedocs.io/en/stable/) - an interesting python module for displaying stuff to the console
3) [Smbus2](https://smbus2.readthedocs.io/en/latest/) - an I2C library for python

### About MIDI ###

https://en.wikipedia.org/wiki/Piano_key_frequencies

https://www.cs.cmu.edu/~music/cmsip/readings/davids-midi-spec.htm

https://nickfever.com/music/midi-cc-list


