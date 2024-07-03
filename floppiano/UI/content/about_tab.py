from asciimatics.screen import Screen
from asciimatics.widgets import ( 
    Frame, Layout, Label, TextBox)
from asciimatics.widgets.utilities import THEMES


from ..ascii.tabs import Tab

import logging


class AboutTab(Tab):

    def __init__(self, screen: Screen, name: str, logger:logging.Logger = None, theme='default'):
        super().__init__(screen, name, theme)

        #Frame Setup
        self.frame = Frame(
            screen,
            screen.height-2,
            screen.width,y=2,
            has_border=False,
            can_scroll=False,
            reduce_cpu=True)
        self.frame.set_theme(self.theme)    

        layout = Layout([1],True)
        self.frame.add_layout(layout)

        layout.add_widget(Label('About The FlopPiano:', align='^'))
        about_text = TextBox(10,readonly=True,line_wrap=True)
        layout.add_widget(about_text)
        about_text.value = ['This is some about text about us', 'Jorian Hates asciimattics','Farts']


        # layout.add_widget(Label("Application Log:", align='^'))
        # loggerText = LoggerText(height=4)
        # if logger is not None:
        #     logger.addHandler(loggerText)
        # layout.add_widget(loggerText)


        self.frame.fix()
        self.add_effect(self.frame, reset=False)