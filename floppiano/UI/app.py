from asciimatics.screen import Screen
from asciimatics.widgets.utilities import THEMES

class App():
    """_summary_
        An abstract class to do app stuff
    """
    def __init__(self) -> None:
        self._screen = None
        self.theme = 'default'

    @property
    def screen(self) -> Screen:
        return self._screen

    def action(self, action:str, args=None):
        pass       
    
    def resource(self, resource:str, args=None):
        pass

    def run(self):
        pass
    
    @property
    def theme(self):
        return self._theme

    @theme.setter
    def theme(self, theme):
        """
        Shamelessly stolen from asciimatics to support theming

        Pick a palette from the list of supported THEMES.

        :param theme: The name of the theme to set.
        """
        if theme in THEMES:
            self._theme = theme
            self.palette = THEMES[theme]
        else:
            self._theme = 'default'