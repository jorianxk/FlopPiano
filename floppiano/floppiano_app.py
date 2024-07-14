from floppiano import VERSION
import floppiano.bus as bus
from floppiano.devices.drives import DEVICE_TYPE_REG, DEVICE_TYPE
from floppiano.UI.app import App
from floppiano.UI.tabs import TabGroup, Tab, TabHeader
from floppiano.UI.content import (
    splash_screen, FloppySaver, SoundTab, SettingsTab, MIDIPlayerTab ,AboutTab)
from floppiano.synths import DriveSynth

from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.exceptions import ResizeScreenError, StopApplication
from asciimatics.widgets.utilities import THEMES

from mido import Message
from mido.ports import BaseInput, BaseOutput

import time
import logging
import sys
import os


class FlopPianoApp(App):

    def __init__(
            self, 
            synth:DriveSynth,            # The DriveSynth to use
            #keyboard = None,             #TODO: add keyboard here
            input_port:BaseInput,
            output_port:BaseOutput, 
            theme: str = 'default',        # The initial asciimatics theme to use
            splash_start: bool = True,     # Start the app with splash screens
            screen_timeout:float = None,   # In seconds and fractions of seconds
            ) -> None:
        
        super().__init__(theme, handle_resize = False)    

        self.logger = logging.getLogger(__name__)


        self._splash_start = splash_start
        self._screen_timeout = screen_timeout

        # The Synth
        self._synth = synth 
        # The keyboard
        self._keyboard = None # TODO keyboard 
        # The MIDI input port
        self._input_port = input_port
        # The MIDI output port
        self._output_port = output_port

        # The scene that was active before the screen saver
        self._last_scene = None 
        # The time that the screen was last drawn
        self._last_draw_time = None
        # A flag to force a redraw
        self._needs_redraw = False
        # A flag to allow the piano keys' midi to be injected
        self._loopback = True

  
    def run(self):
        # Run setup
  
        #self._find_assets()
        #self._config_ports()
        self._synth.reset()
        if self._splash_start:
            #Use asciimatics to play the splash sequence, blocks until done
            Screen.wrapper(splash_screen, catch_interrupt=True)

        while True:
            try:
                self._loop()
            except KeyboardInterrupt as ki:
                # Stop the rendering so that print() works
                self.reset()
                print("ctrl+c stopped")
                break
            except ResizeScreenError as sa:
                # Stop the rendering so that print() works
                self.reset()
                print("Resize not supported")
                break
            except Exception as e:
                # Stop the rendering so that print() works
                self.reset()
                raise
        
        self._synth.reset()


    def _loop(self):
        #forcibly Draw the screen once
        self._draw(force=True)

        while True:            
            # If something requested a redraw and the screen saver is not active
            # force a draw to happen
            
            #st = time.time()            
            if self._draw(self._needs_redraw): self._needs_redraw = False
            #self.screen.print_at(time.time()- st, 0,0)
            #self._draw()

            outgoing:list[Message] = []

            # add the piano key midi to the incoming if the loopback is on
            # TODO add the piano key midi to the stream
            if self._loopback: 
                #outgoing.extend(self._synth.parse(keyboard.update()))
                pass 
            
            if self._input_port is not None:
                #Get the messages from the input port
                if(not self._input_port.closed): 
                    input_msg = self._input_port.receive(block=False)
                    #TODO: input when MIDI player?
                    if input_msg is not None: 
                        # If we have a message parse it
                        outgoing.extend(
                            self._synth.parse([input_msg], "input_port"))
                else: raise RuntimeError("The MIDI input port closed!")


            # write the output
            #TODO: output when MIDI player?
            if self._output_port is not None:
                if (not self._output_port.closed):
                    for msg in outgoing:
                        self._output_port.send(msg)
                else: raise RuntimeError("The MIDI output port closed!")
            

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
                    # put all the scenes back, with the last_scene as the start 
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


