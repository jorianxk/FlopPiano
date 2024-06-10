"""
This is a simple script that cycles through all of the available FIGlet fonts
to soo how each looks. using the left and write arrow keys. ctrl+c exits.


"""
from asciimatics.exceptions import StopApplication
from asciimatics.event import KeyboardEvent
from asciimatics.screen import ManagedScreen, Screen
from asciimatics.renderers import FigletText

from time import sleep
import pyfiglet


text = "123456789ABCDEFG"
fonts = pyfiglet.FigletFont.getFonts()

current_font_index = 0

with ManagedScreen() as screen:

    while True:

        font = fonts[current_font_index]

        render = FigletText(text, font=font)

        image, color_map = render.rendered_text

        
        info = f'Font: {font} {current_font_index+1}/{len(fonts)} Height: {render.max_height}'
        screen.centre(info,y=0)

        y = 2
        for line in image:
            screen.centre(line, y)
            y +=1
        
        screen.refresh()
        
        while True:
            event = screen.get_event()
            if event and isinstance(event,KeyboardEvent):
                if event.key_code == screen.KEY_LEFT:
                    #go back a font
                    current_font_index -= 1
                    if current_font_index <0:
                        current_font_index = len(fonts)-1 #loop around
                    break
                if event.key_code == screen.KEY_RIGHT:
                    current_font_index += 1
                    if current_font_index >= (len(fonts)-1): #loop around
                        current_font_index = 0
                    break #go forward


        screen.clear()