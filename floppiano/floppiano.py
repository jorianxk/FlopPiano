from asciimatics.screen import Screen, ResizeScreenError
from asciimatics.scene import Scene
from asciimatics.widgets.utilities import THEMES
from asciimatics.exceptions import StopApplication

from mido import Message

from UI.app import App, AppException
from UI.extentions import Tab, TabGroup
from UI.tabs import SoundTab, SettingsTab, MIDIPlayerTab, AboutTab

from jidi.voices import DriveVoice
from jidi.devices import Keyboard
from floppiano_synth import FlopPianoSynth

from jidi.services import SynthService, MIDIPlayerService
from jidi.midi import MIDIParser

import logging

import traceback

class FlopPiano(App):

    #Service or Synth?
    #THEME
    #logger, and for Synth?
    def __init__(self) -> None:
        super().__init__()

        #TODO better startup

        self._theme = 'default'
        
        self.logger = logging.getLogger("FlopPiano")
        self.logger.setLevel(logging.INFO)


        #TODO better setup on all the things
        voices = [DriveVoice(i) for i in range(8,18)]
        self.synth = FlopPianoSynth(voices, Keyboard(), loopback = False)
        self.synth.logger.setLevel(logging.DEBUG)

        self._sysex_map = self.synth.sysex_map
        self._control_change_map = self.synth.control_change_map

        self.synth_service = SynthService(self.synth)

        self._mid_player = None

    def run(self):
        last_scene = None
        self.synth_service.start()
        while True:
            try:
                Screen.wrapper(self._ui_init, catch_interrupt=False, arguments=[last_scene])
            except ResizeScreenError as e:
                last_scene = e.scene
                #stop any mid file that might be playing
                self._stop_mid_file()
            except KeyboardInterrupt as ke:
                break
            except StopApplication as sa:
                break
            except AppException as ae:
                self.logger.error(ae)
            except Exception as e:
                print(traceback.format_exc())
                break
        
        #TODO: graceful quit and stop synth service
        self.synth_service.quit()
        self.synth_service.join()

    def do_action(self, action: str, args=None):
        match action:
            case 'change_synth':
                self._change_synth(args[0],args[1])
            case 'change_theme':
                self._change_theme(args)
            case 'change_synth':
                self._change_synth(args[0], args[1])
            case 'play_mid_file':
                self._play_mid_file(args[0],args[1])
            case 'stop_mid_file':
                self._stop_mid_file()
            case _:
                pass

    def _ui_init(self, screen:Screen, last_scene:Scene):

            tab_group = TabGroup(screen, self)
            
            tab = SoundTab(
                screen, 
                "Sound", 
                {'crash_mode':self.synth.crash_mode,
                 'spin':self.synth.spin,
                 'pitch_bend_range':self.synth.pitch_bend_range,
                 'modulation_wave':self.synth.modulation_wave,
                 'polyphony': True}, #TODO update this when polyphony support is added
                self.synth.logger,
                self._theme)
            
            tab_group.add_tab(tab)
            
            tab = SettingsTab(screen, "Settings", self._theme)
            tab_group.add_tab(tab)

            tab = MIDIPlayerTab(screen, "MIDI Player", self._theme)
            tab_group.add_tab(tab)

            tab = AboutTab(screen, "About", self.logger, self._theme)
            tab_group.add_tab(tab)

            tab_group.fix()

            scenes = tab_group.tabs

            screen.play(scenes, stop_on_resize=True, start_scene=last_scene, allow_int=True)

    def _change_theme(self, theme:str):
        if theme in THEMES.keys():
            self._theme = theme
            raise ResizeScreenError("theme change")

    def _play_mid_file(self, mid_file:str, transpose:int):
        if self._mid_player is None and self.synth_service.is_alive():
            self.logger.info(f"playing a .mid file...")
            
            self._mid_player = MIDIPlayerService(
                self.synth_service, 
                mid_file, 
                transpose)
            
            self._mid_player.start()
    
    def _stop_mid_file(self):
        if self._mid_player is not None:
            self.logger.info("stopping a .mid file from playing...")
            self._mid_player.quit()
            self._mid_player.join()
            #TODO remove hard coded below
            reset_msg = Message('control_change', control = 120, channel=self.synth.input_channel, value =0)
            self.synth_service.put([reset_msg])
            self._mid_player = None

    def _change_synth(self, attr:str, attr_value:int):
        if attr in self._sysex_map.names():
            msg = Message(
                type='sysex',
                data = [self.synth.sysex_id, 
                        self._sysex_map.code(attr), 
                        attr_value]
            )
            self.synth_service.put([msg])
        elif attr in self._control_change_map.names():
            msg = Message(
                type='control_change',
                control = self._control_change_map.code(attr),
                value = attr_value,
                channel = self.synth.input_channel
            )
            self.synth_service.put([msg])
        else:
            #do nothing
            pass


if __name__ == '__main__':
     FlopPiano().run()

