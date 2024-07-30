from asciimatics.widgets import Layout, Label
from floppiano import VERSION
from floppiano.UI.tabs import Tab
from floppiano.UI.widgets import DynamicFrame, ReadOnlyText
import textwrap

class AboutTab(Tab):
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

        layout = Layout([99,1],False)
        self.frame.add_layout(layout)

        layout.add_widget(Label(f'FlopPiano version {VERSION}', align='^'),0)
        
        # Phantom Text to add a tabstop at the top of the page
        header = ReadOnlyText()
        header.value = ""
        layout.add_widget(header,1)

        layout = Layout([1],True)
        self.frame.add_layout(layout)

        layout.add_widget(Label('Jacob Brooks & Jorian Khan', align='^'))

        # Read the text
        with open('assets/about.txt', encoding="utf8") as file:
            for line in file:
                # Add a blank label at each line break
                layout.add_widget(Label(''))
                # Make the text wrap 
                chunks = textwrap.wrap(line,43, initial_indent='    ')
                for chunk in chunks:
                    text = ReadOnlyText()
                    text.value = chunk
                    layout.add_widget(text)
                

        self.frame.fix()
        self.add_effect(self.frame, reset=False)
    
