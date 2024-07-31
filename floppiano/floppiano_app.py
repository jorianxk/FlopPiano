from floppiano import VERSION
from floppiano.UI.app import App
from floppiano.UI.tabs import TabGroup
from floppiano.UI.content import (
    splash_screen, dead_screen, FloppySaver, MainTab, MIDIPlayerTab ,AboutTab)

from floppiano.synths import DriveSynth
from floppiano.devices import MIDIKeyboard
from floppiano.midi import MIDIPlayer

from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.exceptions import StopApplication
from asciimatics.widgets.utilities import THEMES

from mido import Message
from mido.ports import BaseInput, BaseOutput

import time
import logging


class FlopPianoApp(App):

    def __init__(
            self, 
            synth:DriveSynth,
            keyboard:MIDIKeyboard,
            input_port:BaseInput,
            output_port:BaseOutput,
            theme: str = 'default',
            splash_start: bool = True,
            screen_timeout:float = None,
            ) -> None:
        
        super().__init__(theme, handle_resize = False)    

        self.logger = logging.getLogger(__name__)


        self._splash_start = splash_start
        self._screen_timeout = screen_timeout

        # The Synth
        self._synth = synth 
        # The keyboard
        self._keyboard = keyboard 
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

        self._midi_player = MIDIPlayer(on_stop=self._synth.reset)
  
    def run(self) -> bool:
        # Run the splash screens 
        if self._splash_start:
            #Use asciimatics to play the splash sequence, blocks until done
            Screen.wrapper(splash_screen, catch_interrupt=True)

        # Start with a fresh synth
        self._synth.reset()

        # Handle errors and application exit
        try:
            self._loop()
        except KeyboardInterrupt as ki:
            self.reset() # Reset the Screen so print() works
            self._synth.reset() # Stop any synth activity
            print("ctrl+c stopped.")
            return False # Return false to quit the app
        except Exception as e:
            # Show the dead screen error message
            dead_screen(self.screen, error_msg=(
                "Uh-oh! an error occurred. Press 'enter' to restart. "
                f'Error: {str(e)}'
            ))
            #Do not reset the synth incase a BusException caused the crash
            #ie. NO self._synth.reset() call
            self.reset() # Kill the screen
            return True # Return True to restart the app


    def _loop(self):
        # forcibly draw the screen once before looping
        self.draw(force=True)

        while True:            
            # Any output from the synth goes in this list
            outgoing:list[Message] = []

            # Let the synth handle the MIDIKeyboard messages
            if self._loopback and self._keyboard is not None:
                outgoing.extend(
                    self._synth.parse(self._keyboard.update(),'keyboard')) 
            
            # If playing a .mid, let the synth handle the messages
            if self._midi_player.playing:
                msg = self._midi_player.update()
                if msg is not None:
                    outgoing.extend(self._synth.parse([msg], "midi_player"))

            # Handle any incoming MIDI from the input port
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
            if self._output_port is not None:
                if (not self._output_port.closed):
                    for msg in outgoing:
                        self._output_port.send(msg)
                else: raise RuntimeError("The MIDI output port closed!")
            
            # If something requested a redraw force a draw to happen 
            if self.draw(self._needs_redraw): self._needs_redraw = False            
     
    def action(self, action: str, args=None):
        if action == 'theme':
            self.theme = args[0]
            self.reset()
            self._needs_redraw =True
        if action == 'loopback':
            self._loopback = args
    
    def resource(self, resource: str, args=None):
        if resource == 'synth':
            return self._synth
        if resource == 'loopback':
            return self._loopback
        if resource == 'midi_player':
            return self._midi_player
        return None 

    def _draw_init(self, screen:Screen) -> tuple[list[Scene], Scene]:
        tab_group = TabGroup(screen)
        tab_group.add_tab(MainTab(self, 'Main'))
        tab_group.add_tab(MIDIPlayerTab(self, "MIDI Player"))
        tab_group.add_tab(AboutTab(self, 'About'))
        tab_group.fix()        
        return (tab_group.tabs, None)

    def draw(self, force: bool = False) -> bool:
        # overridden to handle the screen saver logic
        # force drawing only works if the screen saver is not active

        #Is the screen saver active? 
        if self._last_scene is not None: # (last_scene will be set if so)
            #force draw the screen saver every 1 second
            if time.time() - self._last_draw_time >=1:
                try:
                    self._last_draw_time = time.time()
                    return super().draw(True)
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
                    return super().draw(True)
                
        else: #Screen saver is not active
            #Draw if forced
            if force: 
                self._last_draw_time = time.time()
                return super().draw(force=True)
            
            # draw only if there is a keyboard event
            if super().draw(): 
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
                            [FloppySaver(self.screen, VERSION)],#[FloppySaver(self.screen, VERSION)],
                            -1,
                            clear=True
                        )]
                    )


