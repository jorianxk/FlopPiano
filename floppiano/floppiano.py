from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.widgets.utilities import THEMES
from asciimatics.exceptions import StopApplication, ResizeScreenError





from mido import Message
from UI.app import App, AppException
from UI.splashscenes import jb_splash, floppiano_splash
from UI.screensavers import FloppySaver
from UI.extensions import Tab, TabGroup, InactivityError
from UI.tabs import SoundTab, SettingsTab, MIDIPlayerTab, AboutTab

from jidi.voices import DriveVoice
from jidi.devices import Keyboard
from floppiano_synth import FlopPianoSynth


import logging
import traceback




class FlopPiano(App):

    #TODO update app logging?
    #TODO what if synth service or midi player service fail to start/ instantiate?
    def __init__(self) -> None:
        super().__init__()

        #TODO better startup

        self._theme = 'default'
        
        self.logger = logging.getLogger("FlopPiano")
        self.logger.setLevel(logging.INFO)


        voices = [DriveVoice(i) for i in range(8,18)]
        self._synth = FlopPianoSynth(voices, Keyboard(), loopback = False)

  
        self._sysex_map = self._synth.sysex_map
        self._control_change_map = self._synth.control_change_map



    def run(self):
        restart_reason = None
        start_scene = None

        while True:
            try:                    
                Screen.wrapper(
                    self._ui_init, 
                    catch_interrupt=False, 
                    arguments=[restart_reason, start_scene])
            except ResizeScreenError as e:
                restart_reason = "resized"
                start_scene = e.scene
            except InactivityError as ie:
                restart_reason = "inactivity"
                start_scene = ie.scene
            except KeyboardInterrupt as ke:
                break #quits
            except StopApplication as sa:
                break #quits
            except AppException as ae:
                self.logger.error(ae)
            except Exception as e:
                print(traceback.format_exc())
                break #quits
  

    def do_action(self, action: str, args=None):
        match action:
            case 'change_theme':
                # arg[0] = the theme name
                # arg[1] = the scene that requested the change
                self._change_theme(args[0], args[1])
            case 'change_synth':
                # arg[0] = the synth's attribute to change
                # arg[1] = the value to change the attribute to                
                self._change_synth(args[0], args[1])
            case 'play_mid_file':
                # arg[0] = the path of the file to play
                # arg[1] = any note transposition to apply to the file
                self._play_mid_file(args[0],args[1])
            case 'stop_mid_file':
                # no args needed
                self._stop_mid_file()
            case 'drive_test':
                #no args needed
                self._drive_test()
            case _:
                pass
    
    def _ui_init(self, screen:Screen, restart_reason:str, start_scene:Scene):
            tab_group = TabGroup(screen, self)            
            tab = SoundTab(
                screen, 
                "Sound", 
                {'crash_mode':self._synth.crash_mode,
                 'spin':self._synth.spin,
                 'pitch_bend_range':self._synth.pitch_bend_range,
                 'modulation_wave':self._synth.modulation_wave,
                 'polyphony': True}, #TODO update this when polyphony support is added
                self._theme)
            
            tab_group.add_tab(tab)
            
            tab = SettingsTab(
                screen, 
                "Settings",
                {'input_channel': self._synth.input_channel,
                 'output_channel': self._synth.output_channel,
                 'output_modes':self._synth.output_modes, 
                 'output_mode':self._synth.output_mode,
                 'loopback': self._synth.loopback}, 
                self._synth.logger,
                self._theme)
            tab_group.add_tab(tab)

            tab = MIDIPlayerTab(screen, "MIDI Player", self._theme)
            tab_group.add_tab(tab)

            tab = AboutTab(screen, "About", self.logger, self._theme)
            tab_group.add_tab(tab)

            tab_group.fix()

            scenes = tab_group.tabs

            # scenes.insert(0, floppiano_splash(screen, 50,'assets/logo3.txt'))
            # scenes.insert(0, floppiano_splash(screen, 50,'assets/logo2.txt'))
            # scenes.insert(0, floppiano_splash(screen, 50,'assets/logo2b.txt'))
            # scenes.insert(0, floppiano_splash(screen, 50,'assets/logo1.txt'))

            scenes.insert(0, jb_splash(screen, 300))
            
            screen_saver = Scene([FloppySaver(screen, start_scene)],-1,True,"screensaver")
            scenes.append(screen_saver)

            if restart_reason == 'inactivity':
                screen.play(scenes, True, None, screen_saver, True, True)
            else:
                screen.play(scenes, True, None, start_scene, True, True)

    def _change_theme(self, theme:str, scene:Scene):
        #Only change the theme if it's a valid theme
        if theme in THEMES.keys():
            self._theme = theme
            #pass the scene so after the change that scene will be shown
            raise ResizeScreenError("theme change", scene)

    def _change_synth(self, attr:str, attr_value:int):
        # #don't change anything if the port service is not running
        # if self._port_service.is_alive():
        #     # is the attribute in the sysex map?
        #     if attr in self._sysex_map.names():
        #         msg = Message(
        #             type='sysex',
        #             data = [self._synth.sysex_id, 
        #                     self._sysex_map.code(attr), 
        #                     attr_value]
        #         )
        #         self._port_service.put([msg])
        #     # is the attribute in the control change map?
        #     elif attr in self._control_change_map.names():
        #         msg = Message(
        #             type='control_change',
        #             control = self._control_change_map.code(attr),
        #             value = attr_value,
        #             channel = self._synth.input_channel
        #         )
        #         self._port_service.put([msg])
        #     # attribute is unknown
        #     else:
        #         #do nothing
        #         pass
        # else:
        #     raise DeadPortService("port_service dead on _change_synth()")
        pass

    def _play_mid_file(self, mid_file:str, transpose:int):
        # if self._port_service.is_alive():
        #     #don't play if the mid player is already in use
        #     if (self._mid_player is None) or (not self._mid_player.is_alive()):
        #         self._mid_player = MIDPlayerService(
        #             self._port_service,
        #             mid_file,
        #             transpose)
                
        #         self._mid_player.start()
        # else:
        #     raise DeadPortService("port_service dead on _play_mid_file")
        pass
    
    def _stop_mid_file(self):
        # if self._mid_player is not None:
        #     if self._mid_player.is_alive():
        #         self._mid_player.quit() #request stop
        #         self._mid_player.join() #wait for stop
        #     self._mid_player = None
        pass

    def _drive_test(self):
        # #Stop the active service so that we can control the drives manually
        # self._stop_port_service()

        # # Play two notes on each drive
        # for voice in self._synth.voices:
        #     voice.note = 40 # C4
        #     voice.update(make_noise=True)
        #     time.sleep(0.5)
        #     voice.note = 69 # A4
        #     voice.update(make_noise=True)
        #     time.sleep(0.5)
        #     voice.update(make_noise=False) #Turn the drive off
        #     time.sleep(0.5)       


        # #Restart the active service
        # self._start_port_service(PortService(self._synth))
        pass
    

if __name__ == '__main__':
     FlopPiano().run()

