from UI.app import App
from UI.ascii.util import event_draw
from UI.ascii.tabs import TabGroup
from UI.content import (
    run_splash, SoundTab)



from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import ResizeScreenError, StopApplication


import traceback
import logging
import os


class FlopPiano(App):

    def __init__(
            self, 
            asset_dir:str = './assets',
            port_type:str = 'physical', 
            splash_start = False) -> None:
        

        self.logger = logging.getLogger("FlopPiano")

        self._asset_dir = asset_dir

        self._splash_start = splash_start

        super().__init__()


    def action(self, action: str, args=None):
        return super().action(action, args)
    
    def resource(self, resource: str, args=None):
        return super().resource(resource, args)
    
    def run(self):
        #self._find_assets()
        #self._config_ports()

        if self._splash_start:
            #Use asciimatics to play the splash sequence
            Screen.wrapper(run_splash, catch_interrupt=True)

        self._screen = Screen.open(catch_interrupt=False)


        #TODO: remove erorrs
        try:
            self._init_ui()
        except Exception as e:
            self.screen.close()
            print(traceback.format_exc())
            exit(1)
        #init_ui
        self._loop()


    def _loop(self):
        #draw once
        event_draw(self._screen)
        while True:
            try:
                keyboard_event = self._keyboard_event()
                if keyboard_event is not None: #we got a keyboard event
                    event_draw(self._screen, keyboard_event)

                # if piano keys:
                #     midi_stream.append(piano_key_midi) 

                # if playing_midfile:
                #     midi_stream.append(mid_file_message) [if any]
                # else:
                #     midi_stream.append(midi_input_message) [if any]

                # output = synth.parse(midi_stream)

                # outputmidi(output)

                # draw() #To update UI based on synth changes / app changes
                

            except KeyboardInterrupt as ki:
                self._close()
                break # exit
            except StopApplication as sa:
                self._close()
                break # exit
            except ResizeScreenError as rse:
                self._close()
                print("Screen resized")
                break
            except Exception as e:
                #self.logger.error(e)
                self._close()
                print(traceback.format_exc())
                break # exit
                

        
    

    def _find_assets(self):
        self.logger.debug(f"Verifying asset directory: '{self._asset_dir}'")   

        if not os.path.isdir(self._asset_dir):
            self.logger.critical(
                f"Asset directory '{self._asset_dir} not'found. exiting...")
            raise RuntimeError("Could not find assets")

        self.logger.debug(f"Found asset directory: '{self._asset_dir}'")

    def _keyboard_event(self) -> KeyboardEvent:
        event = self._screen.get_event()
        #ignore mouse events
        if isinstance(event, KeyboardEvent):
            return event
        
        return None

    def _init_ui(self):

        tab_group = TabGroup(self._screen)
        tab_group.add_tab(SoundTab(self, "sound"))

        tab_group.fix()

        self._screen.set_scenes(tab_group.tabs)

        


    def _close(self):
        self._screen.close()

if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    FlopPiano().run()


