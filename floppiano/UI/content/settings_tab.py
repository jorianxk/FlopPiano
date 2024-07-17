from asciimatics.widgets import Layout, Label, Button, Divider, VerticalDivider
from asciimatics.widgets.utilities import THEMES

from floppiano.UI.tabs import Tab
from floppiano.UI.widgets import DynamicFrame, DropDown

from floppiano.synths import (PITCH_BEND_RANGES, OUTPUT_MODES, DriveSynth)


class SettingsTab(Tab):


    def __init__(self, app, name: str):
        super().__init__(app, name)

        self.synth:DriveSynth = self.app.resource('synth')
        
        # Frame Setup
        self.frame = DynamicFrame(
            self.app.screen,
            self.app.screen.height-2,
            self.app.screen.width,
            y=2,
            has_border=True,
            can_scroll=False,
            title=self.name,
            on_update=self.update_widgets)
        self.frame.set_theme(self.app.theme)     

       #--------------------Table Layout and Widgets--------------------------#
        #Layout for table 
        table_layout = Layout([1],fill_frame=False)
        self.frame.add_layout(table_layout) 



        b1 = Button("test", on_click=None)
        table_layout.add_widget(b1)

        b2 = Button("test2",on_click=None)
        table_layout.add_widget(b2)


        self.frame.fix()
        self.add_effect(self.frame, reset=False)

    def update_widgets(self):
        pass

