from asciimatics.screen import Screen, ResizeScreenError
from asciimatics.scene import Scene
from asciimatics.widgets.utilities import THEMES

from UI.app import App
from UI.extentions import Tab, TabGroup
from UI.tabs import SoundTab, AboutTab

import sys
import logging

class FlopPiano(App):

    #Service or Synth?
    #THEME
    #logger, and for Synth?
    def __init__(self, theme='default') -> None:
        super().__init__('FlopPiano', theme)
        self.logger.setLevel(logging.DEBUG)

    def run(self):
        last_scene = None
        while True:
            try:
                Screen.wrapper(self._update_ui, catch_interrupt=False, arguments=[last_scene])
                sys.exit(0)
            except ResizeScreenError as e:
                last_scene = e.scene
            except KeyboardInterrupt as ke:
                break

    def _update_ui(self, screen:Screen, last_scene:Scene):

            tab_group = TabGroup(screen, self)
            
            tab = SoundTab(screen, "Sound",self.theme)
            tab_group.add_tab(tab)
            
            tab = Tab(screen, "Behavior", self.theme)
            tab_group.add_tab(tab)

            tab = Tab(screen, "MIDI Player", self.theme)
            tab_group.add_tab(tab)

            tab = AboutTab(screen, "About", self.logger, self.theme)
            tab_group.add_tab(tab)

            tab_group.fix()

            scenes = tab_group.tabs


            screen.play(scenes, stop_on_resize=True, start_scene=last_scene, allow_int=True)



if __name__ == '__main__':
     FlopPiano().run()

