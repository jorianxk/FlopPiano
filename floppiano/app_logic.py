from UI.app import App
from UI.splashscenes import jb_splash, floppiano_splash
from UI.extensions import TabGroup
from UI.tabs import SoundTab, SettingsTab, MIDIPlayerTab, AboutTab

from asciimatics.screen import Screen
from asciimatics.event import KeyboardEvent


from floppiano_synth import FlopPianoSynth
from jidi.devices import Keyboard
from jidi.voices import DriveVoice

import time


#TODO: unhandled input handler

class FlopPiano(App):

    def __init__(self) -> None:
        super().__init__()
        self._screen = None

        self._theme = 'default'

        voices = [DriveVoice(i) for i in range(8,18)]
        self._synth = FlopPianoSynth(voices, Keyboard(), loopback = False)

    def run(self, splash:bool=False):        
        if splash: # play the startup screens
            Screen.wrapper(self.play_splash,catch_interrupt=True)
        
        #prep scenes, open screen
        self._screen = Screen.open(catch_interrupt=False)

        tab_group = TabGroup(self._screen, self)            
        tab = SoundTab(
            self._screen, 
            "Sound", 
            {'crash_mode':self._synth.crash_mode,
                'spin':self._synth.spin,
                'pitch_bend_range':self._synth.pitch_bend_range,
                'modulation_wave':self._synth.modulation_wave,
                'polyphony': True}, #TODO update this when polyphony support is added
            self._theme)
        
        tab_group.add_tab(tab)
        
        tab = SettingsTab(
            self._screen, 
            "Settings",
            {'input_channel': self._synth.input_channel,
                'output_channel': self._synth.output_channel,
                'output_modes':self._synth.output_modes, 
                'output_mode':self._synth.output_mode,
                'loopback': self._synth.loopback}, 
            self._synth.logger,
            self._theme)
        tab_group.add_tab(tab)

        tab = MIDIPlayerTab(self._screen, "MIDI Player", self._theme)
        tab_group.add_tab(tab)

        tab = AboutTab(self._screen, "About", self._theme)
        tab_group.add_tab(tab)

        tab_group.fix()

        scenes = tab_group.tabs

        self._screen.set_scenes(scenes)

        self._main(self._screen)
        self._screen.close()

     
    def play_splash(self, screen:Screen):
        scenes = []
        scenes.insert(0, floppiano_splash(screen, 50, 'assets/logo3.txt'))
        #scenes.insert(0, floppiano_splash(screen, 50, 'assets/logo2.txt'))
        #scenes.insert(0, floppiano_splash(screen, 50, 'assets/logo2b.txt'))
        #scenes.insert(0, floppiano_splash(screen, 50, 'assets/logo1.txt'))
        scenes.append(jb_splash(screen))
        screen.play(scenes,False,repeat=False)

    def _main(self, screen:Screen):
        # Draw once
        App.draw(screen)

        while True:
            event = screen.get_event()
            # only draw on keyboard events
            if event is not None and isinstance(event, KeyboardEvent):
                App.draw(screen,event, repeat=True)
        

    def do_action(self, action: str, args=None):
        pass


if __name__ == '__main__':
     FlopPiano().run(False)