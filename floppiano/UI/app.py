import logging
from asciimatics.widgets.utilities import THEMES

class App():
    """_summary_
        An abstract class for to do stuff
    """
    def __init__(self, name= 'app', theme='default') -> None:
        self.logger = logging.getLogger(name)

        if theme not in THEMES.keys():
            raise ValueError("Invalid theme")
        
        self.theme = theme

    
    def do_action(self, action:str, args):
        pass       

    def run(self):
        pass

    def quit(self):
        pass
        
