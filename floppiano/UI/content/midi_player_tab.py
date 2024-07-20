from asciimatics.widgets import Layout, Label, PopUpDialog , FileBrowser

from asciimatics.widgets import Widget

from floppiano.UI.tabs import Tab
from floppiano.UI.widgets import DynamicFrame, DropDown

import os

class MIDIPlayerTab(Tab):

    def __init__(self, app, name: str):
        super().__init__(app, name)

        self._synth = self.app.resource('synth')
        self._midi_player = self.app.resource('midi_player')

        # Frame Setup
        self._frame = DynamicFrame(
            self.app.screen,
            self.app.screen.height-2,
            self.app.screen.width,
            y=2,
            has_border=False,
            can_scroll=False,
            on_update=self.update_widgets)
        self._frame.set_theme(self.app.theme)

        #Layout for Frame
        layout = Layout([1],fill_frame=True)
        self._frame.add_layout(layout) 

        layout.add_widget(Label("Transpose:", align='^'))
        transposes = []
        for i in range(-12,13):
            transposes.append((str(i),i))
        self._transpose_dd = DropDown(options=transposes, start_index=0)

        layout.add_widget(self._transpose_dd)

        layout.add_widget(Label("MIDI File:", align='^'))
        self._file_browser = FileBrowser(Widget.FILL_FRAME,
                            os.path.abspath("./assets/MIDI/"),
                            name="mc_list",
                            on_select=self.play,
                            on_change=None,
                            file_filter=".*.mid$")
        layout.add_widget(self._file_browser)
        

        self._frame.fix()
        self.add_effect(self._frame, reset=False)
    
    def update_widgets(self):
        pass

    def play(self):
        file = self._file_browser.value
        transpose = self._transpose_dd.value

        #prevent paging
        self.page = False

        #start playing
        self._midi_player.play(file, self._synth.input_channel, transpose)

        #pop up to stop playing
        file_display_text = str(file).split("/")[-1]        
        self.add_effect(
            PopUpDialog(
                self.app.screen,
                f'Playing {file_display_text}',
                ["Stop"],on_close=self.stop))

    def stop(self, button):
        self._midi_player.stop()
        #re-enable paging
        self.page = True


