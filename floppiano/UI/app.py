from abc import ABC, abstractmethod
from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.widgets.utilities import THEMES
from asciimatics.exceptions import ResizeScreenError
from .ascii.util import keyboard_event_draw

#TODO Docstrings
class App(ABC):
    """_summary_
        An abstract class to do app stuff
    """
    def __init__(
            self,
            theme:str = 'default',
            handle_resize:bool = False) -> None:
        
        self._screen:Screen = None
        self.theme = theme
        self._handle_resize = handle_resize

    @property
    def screen(self) -> Screen:
        #No setter for screen on purpose, screen is initialized on first draw
        return self._screen
    
    @property
    def theme(self) -> str:
        return self._theme

    @theme.setter
    def theme(self, theme) -> None:
        if theme in THEMES:
            self._theme = theme
        else:
            self._theme = 'default'
    
    @abstractmethod
    def run(self):
        """
        """

    @abstractmethod
    def _draw_init(self, screen:Screen) -> tuple[list[Scene], Scene]:
        """
        """

    @abstractmethod
    def action(self, action:str, args=None):
        """
        """
    
    @abstractmethod
    def resource(self, resource:str, args=None):
        """
        """
    
    def reset(self):
        self.screen.clear()
        self.screen.close()
        self._screen = None
 
    def _draw(self, force:bool = False) -> bool:
        #returns true if a draw actually occured
        if self.screen is None: #The the first draw call
            # Open the screen
            self._screen = Screen.open(catch_interrupt=False)
            #clear the screen 
            self.screen.clear()
            # init the scenes and get the first scene
            scenes, start_scene = self._draw_init(self.screen)
            # Set the scenes with the start scene first
            self.screen.set_scenes(scenes, start_scene)
            #Force the screen to draw
            return keyboard_event_draw(self.screen, True)

        elif self.screen.has_resized(): #The screen resized
            # Don't handle the resize if it's not enabled
            if not self._handle_resize: 
                raise ResizeScreenError("Screen Resized")
            # save the last scene
            last_scene = self.screen._scenes[self.screen._scene_index] 
            # Close the screen
            self.screen.close(restore=False) 
            # Re-open the screen (at new size)
            self._screen = Screen.open(catch_interrupt=False)
            #clear the screen
            self.screen.clear()
            # Re-init the scenes (but we ignore the start scene)
            scenes, _ = self._draw_init(self.screen) 
            # Set the scenese and starting with the scene before the resize
            self.screen.set_scenes(scenes, last_scene)
            # Force the screen to draw
            return keyboard_event_draw(self.screen, True) 

        else: # A normal draw call
            # Only draw if forced or if a keyboard event occurs
            return keyboard_event_draw(self.screen, force)  

