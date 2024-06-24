import logging
from asciimatics.widgets.utilities import THEMES

class AppException(Exception):
    pass

class App():
    """_summary_
        An abstract class for to do stuff
    """
    def __init__(self) -> None:
        pass

    
    def do_action(self, action:str, args=None):
        pass       

    def run(self):
        pass

