from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.widgets import Frame

class Tab(Scene):
    #that has at least one Frame (the header)
    def __init__(self, screen:Screen, name:str):    
        Scene.__init__(
            self,
            effects=[], 
            duration=-1, 
            clear=True,
            name=name)        

        self.screen = screen
        self.previous_tab_name = None
        self.next_tab_name = None
    
    def fix(self, tab_header:Frame, previous_tab_name:str, next_tab_name:str):
        self.previous_tab_name = previous_tab_name
        self.next_tab_name = next_tab_name
        self.effects.insert(0, tab_header)