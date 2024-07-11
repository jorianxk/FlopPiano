from asciimatics.widgets import Layout, Label, TextBox
from asciimatics.widgets.utilities import THEMES

from floppiano.UI.ascii.tabs import Tab
from floppiano.UI.ascii.widgets import DynamicFrame

class AboutTab(Tab):

    def __init__(self, app, name: str):
        super().__init__(app, name)

        #Frame Setup
        self.frame = DynamicFrame(
            self.app.screen,
            self.app.screen.height-2,
            self.app.screen.width,
            y=2,
            has_border=False,
            can_scroll=False,
            on_update=self.update_widgets)
        self.frame.set_theme(self.app.theme)   

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
    
    def update_widgets(self):
        pass