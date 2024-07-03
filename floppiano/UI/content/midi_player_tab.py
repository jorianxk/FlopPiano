from asciimatics.screen import Screen
from asciimatics.widgets import ( 
    Frame, Layout, Label, PopUpDialog , FileBrowser, TextBox)
from asciimatics.widgets.utilities import THEMES
from asciimatics.widgets import Widget

from ..ascii.tabs import Tab
from ..ascii.widgets import DropDown

import logging
import os

class MIDIPlayerTab(Tab):

    def __init__(self, screen: Screen, name: str, theme='default'):
        super().__init__(screen, name, theme)

        # Frame Setup
        self.frame = Frame(
            screen,screen.height-2,
            screen.width,
            y=2,
            has_border=False,
            can_scroll=False,
            reduce_cpu=True)
        self.frame.set_theme(self.theme)

        #Layout for Frame
        layout = Layout([1],fill_frame=True)
        self.frame.add_layout(layout) 

        layout.add_widget(Label("Transpose:", align='^'))
        transposes = []
        for i in range(-12,13):
            transposes.append((str(i),i))
        self.transpose_dd = DropDown(options=transposes, start_option="0")

        layout.add_widget(self.transpose_dd)

        layout.add_widget(Label("MIDI File:", align='^'))
        self.file_browser = FileBrowser(Widget.FILL_FRAME,
                            os.path.abspath("."),
                            name="mc_list",
                            on_select=self.play,
                            on_change=None,
                            file_filter=".*.mid$")
        layout.add_widget(self.file_browser)
        
        #Frames must be the last one added to have input focus
        self.frame.fix()
        self.add_effect(self.frame, reset=False)
    
    def play(self):
        file = self.file_browser.value
        transpose = self.transpose_dd.value

        #prevent paging
        self.page = False

        #start playing
        self.app.do_action('play_mid_file', (file, transpose))

        #pop up to stop playing
        file_display_text = str(file).split("/")[-1]        
        self.add_effect(
            PopUpDialog(
                self.screen,
                f'Playing {file_display_text} {type(self.transpose_dd.value)}',
                ["Stop"],on_close=self.stop))

    def stop(self, button):
        self.app.do_action('stop_mid_file')
        #re-enable paging
        self.page = True


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
