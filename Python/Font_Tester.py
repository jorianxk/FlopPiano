"""
This is just a simple script to display a FIGlet font on screen, just to 
see how it looks.  ctrl+c exits.
"""


from asciimatics.screen import ManagedScreen
from asciimatics.renderers import FigletText
import time






#twopoint - NO
#dos_rebel
#ansi_shadow
#short
#colossal
#bloody
#delta_corps_priest_1
#univers
#roman

text = "123456789 ABCDEFGH"
font = "3x5"

with ManagedScreen() as screen:

    render = FigletText(text, font=font)

    image, color_map = render.rendered_text
    
    while True:
        screen.print_at(font,x=0,y=0)
        screen.centre("Height:"+str(render.max_height), 0)

        y = screen.height//2
        for line in image:
            screen.centre(line, y)
            y +=1
            
            screen.refresh()
        
        time.sleep(0.05)
                
