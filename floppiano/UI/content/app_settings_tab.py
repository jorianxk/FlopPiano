from asciimatics.widgets import Layout, Label, Button
from floppiano import VERSION
from floppiano.UI.tabs import Tab
from floppiano.UI.widgets import DynamicFrame
import textwrap





class SettingsTab(Tab):
    """
        A tab for displaying information about the FlopPiano
    """

    def __init__(self, app, name: str):
        super().__init__(app, name)

        #Frame Setup
        self.frame = DynamicFrame(
            self.app.screen,
            self.app.screen.height-2,
            self.app.screen.width,
            y=2,
            has_border=False,
            can_scroll=True)
        self.frame.set_theme(self.app.theme)   

        layout = Layout([1],False)
        self.frame.add_layout(layout)

        # layout.add_widget(Label(f'Settings', align='^'),0)
        layout.add_widget(Button('AI Auto-Calibration', on_click=lambda: self.app.action('rick_roll')))

                

        self.frame.fix()
        self.add_effect(self.frame, reset=False)
    

