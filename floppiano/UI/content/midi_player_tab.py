from asciimatics.widgets import Layout, FileBrowser

from asciimatics.widgets import Button, Divider

from floppiano.UI.tabs import Tab
from floppiano.UI.widgets import DynamicFrame, Setting, ReadOnlyText

import os

class MIDIPlayerTab(Tab):

    def __init__(self, app, name: str):
        super().__init__(app, name)

        self._synth = self.app.resource('synth')
        self._midi_player = self.app.resource('midi_player')

        self._frame = DynamicFrame(
            self.app.screen,
            self.app.screen.height-2,
            self.app.screen.width,
            y=2,
            has_border=False,
            can_scroll=False,
            on_update = self._update_widgets)
        self._frame.set_theme(self.app.theme)

        self._transpose_setting = Setting(
            label_text = 'Transpose', 
            options = range(-12,13), 
            on_update = lambda: 0, # This sets the default value
            on_change = None,
            frame = self._frame)
        
        self._redirect_setting = Setting(
            label_text = 'Redirect', 
            options = ['off', 'on'], 
            on_update = None, 
            on_change = None,
            frame = self._frame)


        layout = Layout([1],fill_frame=False)
        self._frame.add_layout(layout)
        layout.add_widget(Divider())
        #layout.add_widget(Label("MIDI File:", align='^'))
        self._file_browser = FileBrowser(
                            height = 15,#height = Widget.FILL_FRAME,
                            root = os.path.abspath("./assets/MIDI/"),
                            on_select = self.play,
                            on_change = None,
                            file_filter = ".*.mid$")
        layout.add_widget(self._file_browser)

        layout.add_widget(Divider())

        
        layout = Layout([80,20])
        self._frame.add_layout(layout)

        self._details_text = ReadOnlyText(tab_stop = False)
        self._details_text.value = ' '
        layout.add_widget(self._details_text, 0)
        
        self._stop_button = Button(text="Stop", on_click= self.stop)
        layout.add_widget(self._stop_button,1)


        self._frame.fix()
        self.add_effect(self._frame, reset=False)

    def _update_widgets(self):  
        if self._midi_player.playing:
            self._stop_button.disabled = False
            file_display_text = self._midi_player.file_path.split("/")[-1]   
            #length = MidiFile(file).length
            self._details_text.value = f"'{file_display_text}'"
        else:
            self._stop_button.disabled = True
            self._details_text.value = ' '


    def play(self):
        # Don't do anything if the player is already playing
        if self._midi_player.playing: return

        #The path to the file that the user wants to play
        file = self._file_browser.value
        #start playing
        if bool(self._redirect_setting.value):
            # Redirect all the MIDI to the synth's input channel
            self._midi_player.play(
                file = file, 
                redirect = self._synth.input_channel, 
                transpose = self._transpose_setting.value)
        else:
            # Don't redirect
            self._midi_player.play(
                file = file, 
                transpose = self._transpose_setting.value)

    def stop(self):
        self._midi_player.stop()
