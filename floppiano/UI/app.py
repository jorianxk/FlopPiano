from abc import ABC, abstractmethod
from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.widgets.utilities import THEMES
from asciimatics.exceptions import ResizeScreenError
from floppiano.UI.util import keyboard_event_draw


class App(ABC):
    """
        An abstract class to handle simple App attributes, logic, and 
        bastardized asciimatics rendering in a single threaded way.
    """
    def __init__(
            self,
            theme:str = 'default',
            handle_resize:bool = False) -> None:
        """
            Insatiate an App
        Args:
            theme (str, optional):The asciimatics theme the app will use.
                Defaults to 'default'.
            handle_resize (bool, optional): If the app should attempt to handle
                window resizing. (Experimental) Defaults to False.
        """
        
        self._screen:Screen = None
        self.theme = theme
        self._handle_resize = handle_resize

    @property
    def screen(self) -> Screen:
        # No setter for screen on purpose, screen is initialized on first draw
        return self._screen
    
    @property
    def theme(self) -> str:
        return self._theme

    @theme.setter
    def theme(self, theme:str) -> None:
        """
            Sets the App theme.
        Args:
            theme (str): If the theme is not a valid ascii theme the default
                theme will be used 
        """
        if theme in THEMES:
            self._theme = theme
        else:
            self._theme = 'default'
    
    @abstractmethod
    def run(self):
        """
            Should be called to start the app
        """

    @abstractmethod
    def _draw_init(self, screen:Screen) -> tuple[list[Scene], Scene]:
        """
            Will be called by the draw routine. Expects a return value 
            of tuple[list[Scene], Scene]. Where the list of Scenes is a set
            of the Scenes to be rendered and the singular Scene is the starting
            Scene
        """

    @abstractmethod
    def action(self, action:str, args=None):
        """
            Used by other UI Elements to perform some user defined App-wide 
            action/function.
        """
    
    @abstractmethod
    def resource(self, resource:str, args=None):
        """
            Used by other UI Elements to get some user defined App-wide 
            resource/object.
        """
    
    def reset(self):
        """
            Forces the App's screen to clear then close so that it may be
            restarted on the next draw() call.
        """
        self.screen.clear()
        self.screen.close()
        self._screen = None
 
    def draw(self, force:bool = False) -> bool:
        """
            Renders the Scenes obtained via a _draw_init() call only on keyboard
            events or if forced.
        Args:
            force (bool, optional): If true, forces the asciimatics Screen to 
                render regardless of if a keyboard event occured. Defaults to 
                False.
        Raises:
            ResizeScreenError: If the App's attribute handle_resize was not set
                during instantiation a ScreenResizeError will be raised upon 
                screen resizes.

        Returns:
            bool: True if the screen actually drew, false otherwise.
        """
        #returns true if a draw actually occurred
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

