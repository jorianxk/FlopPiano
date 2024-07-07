from UI.app import App
from UI.ascii.tabs import TabGroup, Tab, TabHeader
from UI.content import (
    splash_screen, FloppySaver, SoundTab, SettingsTab, MIDIPlayerTab ,AboutTab)

from jidi2.synths import DriveSynth
from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.exceptions import ResizeScreenError, StopApplication
from asciimatics.widgets.utilities import THEMES

import time
import logging
import os

VERSION = 0.0
# Add a frame counter
TabHeader._FRAME_RATE_DEBUG = True

#Remove this theme - it's unsupported on windows and on headless rasp os
THEMES.pop('tlj256', None)

# Changed for Jorian's windows PC
Tab.NEXT_TAB_KEY = Screen.KEY_F2
Tab.PRIOR_TAB_KEY = Screen.KEY_F1


class FlopPiano(App):

    def __init__(
            self, 
            theme: str = 'default',      # The initial asciimatics theme to use
            handle_resize: bool = False, # Allow resizing (experimental)
            splash_start: bool = True,   # Start the app with splash screens
            screen_timeout:float = None, # In seconds and fractions of seconds
            asset_dir:str = './assets',  # The directory for any app assets
            ) -> None:
        
        super().__init__(theme, handle_resize)    

        self.logger = logging.getLogger("FlopPiano")
        self._asset_dir = asset_dir
        self._splash_start = splash_start
        self._screen_timeout = screen_timeout

        # The Synth
        self._synth = None 
        # The scene that was active before the screen saver
        self._last_scene = None 
        # The time that the screen was last drawn
        self._last_draw_time = None
        # A flag to force a redraw
        self._needs_redraw = False
        # A flag to allow the piano keys' midi to be injected
        self._loopback = True


  
    def run(self):
        #setup synth
        self._synth = DriveSynth()
        #self._find_assets()
        #self._config_ports()

        if self._splash_start:
            #Use asciimatics to play the splash sequence, blocks until done
            Screen.wrapper(splash_screen, catch_interrupt=True)

        while True:
            try:
                self._loop()
            except KeyboardInterrupt as ki:
                self.reset()
                print("ctrl+c stopped")
                break
            except ResizeScreenError as sa:
                # Only occurs if handle_resize = False
                self.reset()
                print("Resize not supported")
                break
            except Exception as e:
                self.reset()
                raise
        


    def _loop(self):
        #forcibly Draw the screen once
        self._draw(force=True)

        while True:            
            # If something requested a redraw and the screen saver is not active
            # force a draw to happen
            #self._draw()
            if self._draw(self._needs_redraw): self._needs_redraw = False


            # read the piano keys
            # add the piano key midi to the incoming stream if the loopback is 
            # enabled
            if self._loopback: pass #add the piano key midi to the stream

            # add the incoming port midi to the stream if any
            # let the synth work then get it's output
            # write the output

    def _draw_init(self, screen:Screen) -> tuple[list[Scene], Scene]:
        tab_group = TabGroup(screen)
        tab_group.add_tab(SoundTab(self, 'Sound'))
        tab_group.add_tab(SettingsTab(self, 'Settings'))
        tab_group.add_tab(MIDIPlayerTab(self, "MIDI Player"))
        tab_group.add_tab(AboutTab(self, 'About'))
        tab_group.fix()        
        return (tab_group.tabs, None)
     
    def action(self, action: str, args=None):
        if action == 'theme':
            self.theme = args[0]
            self.reset()
            self._needs_redraw =True
        if action == 'loopback':
            self._loopback = args
        else:
            pass
    
    def resource(self, resource: str, args=None):
        if resource == 'synth':
            return self._synth
        if resource == 'loopback':
            return self._loopback
        else:
            return None
    

    def _find_assets(self):
        self.logger.debug(f"Verifying asset directory: '{self._asset_dir}'")
        if not os.path.isdir(self._asset_dir):
            self.logger.critical(
                f"Asset directory '{self._asset_dir} not'found. exiting...")
            raise RuntimeError("Could not find assets")
        self.logger.debug(f"Found asset directory: '{self._asset_dir}'")

    def _draw(self, force: bool = False) -> bool:
        # overridden to handle the screen saver logic
        # force drawing only works if the screen saver is not active

        #Is the screen saver active? 
        if self._last_scene is not None: # (last_scene will be set if so)
            #force draw the screen saver every 1 second
            if time.time() - self._last_draw_time >=1:
                try:
                    self._last_draw_time = time.time()
                    return super()._draw(True)
                except StopApplication:
                    # Exit the screen saver - a key was pressed
                    # re-init the scenes, ignore the start scene
                    scenes, _ = self._draw_init(self.screen)
                    # put all the scences back, with the last_scene as the start 
                    self.screen.set_scenes(scenes, start_scene=self._last_scene)
                    # disable the screen saver by setting last_scene to None
                    self._last_scene = None
                    #force the screen to draw once
                    self._last_draw_time = time.time()
                    return super()._draw(True)
                
        else: #Screen saver is not active
            #Draw if forced
            if force: 
                self._last_draw_time = time.time()
                return super()._draw(force=True)
            
            # draw only if there is a keyboard event or if the screen resizes
            if super()._draw(): 
                self._last_draw_time = time.time()
                return True #we drew

            #if the screen saving is is enabled, check the screen timeout
            if self._screen_timeout is not None: 
                if time.time() - self._last_draw_time >= self._screen_timeout:
                    #enable the screen saver by setting the last_scene
                    self._last_scene = \
                        self.screen._scenes[self.screen._scene_index]
                    #Force the screen to have only the screen saver as a scene
                    self.screen.set_scenes(
                        [Scene(
                            [FloppySaver(self.screen, VERSION)],
                            -1,
                            clear=True
                        )]
                    )


if __name__ == '__main__':  
    #logging.basicConfig(level=logging.DEBUG)
    FlopPiano(
        theme='default',
        handle_resize=False,
        splash_start=False, 
        screen_timeout=10,
        asset_dir='./assets').run()
    
