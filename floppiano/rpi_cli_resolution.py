"""

A script to run on a headless Raspberry Pi to get terminal columns and lines.
Using these values we can emulate the Pi's display using an ssh terminal.

WARNING: Do not run via ssh. This script must be run on the Pi with a physical
keyboard and display. (If you run this via ssh you will get values that
represent the columns/lines of your host system's terminal and not the headless 
Pi's terminal with a display)

Goal:

We need to determine the terminal/bash/shell character "resolution" (i.e. 
columns and lines) of the headless raspberry pi when using a composite display
with an arbitrary resolution.

We intend to use a composite backup camera screen (like this:
https://www.amazon.com/dp/B0045IIZKU?psc=1&ref=ppx_yo2ov_dt_b_product_details).
Subsequently, the RPi will be operating in composite video mode via the 3.5 mm 
jack.

-The target screen has the resolution: 

320X240 

-The RPi operating in composite mode has the following resolutions:

720x480@60i for NTSC <-- We're likely this because the RPi region is US
720x576@50i for PAL

See: 
https://discourse.osmc.tv/t/composite-sd-resolution-of-osmc-skin-video-output/5445
https://forums.raspberrypi.com/viewtopic.php?t=47527


Since the screen has a lower resolution than the RPi's native composite
resolution, we're not sure how many columns and lines the headless pi will have.

Hence, this script prints the number of columns and lines the the RPi offers
to the display via the "tput" bash command. 

Jorian wrote this script because his display (from amazon) is shit and when 
invoking tput the output is concealed. The shit display crops the RPi's
output so the first few characters of every line are not visible). Jacobs 
goodwill display does not suffer from this - despite being identical. 


Can  we change anything? - Not really, unless we use a different (hdmi) display.
https://learn.adafruit.com/using-a-mini-pal-ntsc-display-with-a-raspberry-pi/configure-and-test

Following the steps from the above link and adjusting the framebuffer and 
the overscan in config.txt did nothing for Jorian's display.

TBH - these settings may only apply when using HDMI?

"""


import subprocess #to get os bash output

columns = subprocess.check_output(['tput', 'cols']) # $ tput cols
columns = columns.decode("utf-8")
columns = columns.strip() # removes cr and or lf

lines = subprocess.check_output(['tput', 'lines'])  # $ tput lines
lines = lines.decode("utf-8")
line = lines.strip()

#The leading spaces prevent the output from being cropped (see above)
print(f'                        Columns: {columns}    Lines: {lines}', end = "")


#Jorian ran this script and got "Columns: 90    Lines:30"