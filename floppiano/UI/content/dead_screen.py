from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.renderers import StaticRenderer
from asciimatics.effects import Effect, Print, _Flake, Snow
from random import randint
import textwrap
from floppiano.UI.util import time2frames


class OffsetFlake(_Flake):

    def __init__(self, screen, y_offset: int = 0):
        """
            An Overridden version of asciimatics.effects._Flake that adds
            the ability to offset the a flakes' spawn position vertically.
        Args:
            screen (Screen): The screen which renders the OffsetFlake 
            y_offset (int, optional): The vertical offset of the Flakes' spawn
                position. Defaults to 0.
        """
        self._start_line = screen.start_line + y_offset
        super().__init__(screen)

    def _reseed(self):
        """
            Overridden to re-set self._y to account for the y offset
        """
        super()._reseed()
        #self._y = self._start_line + randint(0, self._rate)
        self._y = self._start_line + randint(0, self._rate)

class OffsetSnow(Snow):

    def __init__(self, screen, y_offset:int = 0, **kwargs):
        """
            An overridden version of asciimatics.effects.Snow to add the
            ability to vertically offset the snow's spawn position using an
            OffsetFlake.
        Args:
            screen (Screen): The Screen which will render the OffsetSnow
            y_offset (int, optional): The vertical offset of the Flakes' spawn
                position. Defaults to 0.
        """
        self._y_offset = y_offset
        super().__init__(screen, **kwargs)
        

    def _update(self, frame_no):
        """
            Overridden to use an OffsetFlake instead of a _Flake
        """
        if frame_no % 3 == 0:
            if len(self._chars) < self._screen.width // 3:
                self._chars.append(OffsetFlake(self._screen, self._y_offset))

            for char in self._chars:
                char.update((self._stop_frame == 0) or (
                    self._stop_frame - frame_no > 100))

class ErrorBox(Effect):

    def __init__(self, screen,
                 x:int = 0,
                 y:int = 0,
                 height:int = 6,
                 error_text = '', 
                 **kwargs):
        """
            An effect to print an error message in a box
        Args:
            screen (_type_): The screen the ErrorBox will be rendered with
            x (int, optional): The x position of the ErrorBox. Defaults to 0.
            y (int, optional): The y position of the ErrorBox. Defaults to 0.
            height (int, optional): The height of the ErrorBox Defaults to 6.
            error_text (str, optional): The error Text to display. 
                Defaults to ''.
        """

        self._x = x
        self._y = y
        self._height = height

        #Wrap the string into chunks of length screen.width - 2
        self._error_text = textwrap.wrap(error_text, screen.width -2)

        # If we have more chunks then height we need to shorten
        if len(self._error_text) > (self._height - 2):
            self._error_text = self._error_text[0:(self._height-2)]
            # The last chunk should be "..."ed to let the user know the value 
            # was shortened
            self._error_text[-1] = textwrap.shorten(
                self._error_text[-1] + "-" * 100, # Extra text to ensure shorten
                width = (screen.width -2),
                placeholder = '...')
        
        super().__init__(screen, **kwargs)
        


    def _update(self, frame_no):
        screen:Screen = self._screen

        # Draw top of box
        screen.print_at('┌' + '─'*(screen.width -2) + '┐',self._x, self._y)

        # Draw sides of box
        for i in range(self._y+1, self._y+ self._height -1):
            screen.print_at('│' + ' '*(screen.width -2) + '│' , self._x, i)
        
        # Draw bottom of box
        screen.print_at(
            '└' + '─'*(screen.width -2) + '┘',
            self._x, 
            self._y + self._height -1)
        
        # Print the error text
        y = self._y +1
        for line in self._error_text:
            screen.print_at(line, self._x+1, y)
            y+=1    
    

    def reset(self): pass

    @property
    def stop_frame(self): return 0

def dead_screen(screen:Screen, error_msg:str = None , repeat = False):
    # No error message, use a generic one
    if error_msg is None: 
        error_msg = ( 
            "Uh-oh! An unknown error occurred. Press 'enter' to continue...")

    # Read the sad Floppie
    sad_floppie = None
    with open('assets/floppie_sad.txt', encoding="utf8") as file:
        sad_floppie = file.read()

    floppie_renderer = StaticRenderer([sad_floppie])

    effects = [
        Print(
            screen, 
            floppie_renderer,
            (screen.height) - (floppie_renderer.max_height),
            (screen.width // 2) - (floppie_renderer.max_width//2),
            colour=Screen.COLOUR_WHITE), # Print Floppie    
        ErrorBox(screen, height=6, error_text= error_msg), # Error Message
        OffsetSnow(screen, 6)  # Snow to make it tragic 
    ]

    screen.play([Scene(effects,clear=True)], repeat=repeat)