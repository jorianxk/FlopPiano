from UI.app import App
from UI.ascii.tabs import TabGroup, Tab
from UI.content import (
    splash_screen, screen_saver, SoundTab)

from jidi2.synths import DriveSynth
from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.exceptions import ResizeScreenError, StopApplication


import time
import logging
import os

Tab.NEXT_TAB_KEY = Screen.KEY_F2
Tab.PRIOR_TAB_KEY = Screen.KEY_F1


# class ScreenTimeout(Exception):
#     def __init__(self, *args: object) -> None:
#         super().__init__(*args)


VERSION = 2.5
class FlopPiano(App):

    def __init__(
            self, 
            theme: str = 'default',
            handle_resize: bool = False,
            splash_start: bool = True,
            screen_timeout:float = None,
            asset_dir:str = './assets'
            ) -> None:
        
        super().__init__(theme, handle_resize)    

        self.logger = logging.getLogger("FlopPiano")
        self._asset_dir = asset_dir
        self._splash_start = splash_start
        self._screen_timeout = screen_timeout

        self._synth = None 
        # The scene that was active before the screen saver
        self._last_scene = None 
        # The time that the screen was last drawn
        self._last_draw_time = None

  
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
                self.reset()
                print("Resize not supported")
                break
            except Exception as e:
                self.reset()
                raise
        

    def _loop(self):
        #forcably Draw the screen once
        self._draw(force=True)
        self._last_draw_time = time.time()
        needs_redraw = False

        while True:            
            # If something requested a redraw and the screen saver is not active
            # force a draw to happen
            self._draw()
            #if self._draw(needs_redraw): needs_redraw = False
        



    def _draw_init(self, screen:Screen) -> tuple[list[Scene], Scene]:
        tab_group = TabGroup(screen)
        tab_group.add_tab(SoundTab(self, "sound"))
        tab_group.fix()        
        return (tab_group.tabs, None)
     
    def action(self, action: str, args=None):
        return super().action(action, args)
    
    def resource(self, resource: str, args=None):
        if resource == "synth":
            return self._synth
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
                    self.screen.set_scenes(scenes, self._last_scene)
                    # disable the screen saver by setting last_scene to None
                    self._last_scene = None
                    #force the screen to draw once
                    self._last_draw_time = time.time()
                    return super()._draw(True)
        else: #Screen saver is not active

            if force: 
                self._last_draw_time = time.time()
                return super()._draw(force=True)
            # draw only if there is a keyboard event or if the screen resizes
            if super()._draw(): 
                self._last_draw_time = time.time()
                return True #we drew

            #if the screen saving is is enabled, check the screentimeout
            if self._screen_timeout is not None: 
                if time.time() - self._last_draw_time >= self._screen_timeout:
                    #enable the screen saver by setting the last_scene
                    self._last_scene = \
                        self.screen._scenes[self.screen._scene_index]
                    #Force the screen to have only the screen saver as a scene
                    self.screen.set_scenes(screen_saver(self.screen,VERSION))
                    
                    
  

if __name__ == '__main__':  
    #logging.basicConfig(level=logging.DEBUG)
    FlopPiano(
        handle_resize=False,
        splash_start=False, 
        screen_timeout=1).run()
    



