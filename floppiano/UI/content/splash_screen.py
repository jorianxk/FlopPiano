from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.renderers import StaticRenderer
from asciimatics.effects import Effect, Print
from asciimatics.particles import ShootScreen, Explosion
from random import randint

from floppiano.UI.util import time2frames
from floppiano.midi import MIDIPlayer
from threading import Thread

"""
    A collection of functions that assist in the splash screens of the 
    FlopPiano App 
"""

class SlidingFloppie(Effect):

    def __init__(self, screen, **kwargs):        
        super().__init__(screen, **kwargs)       

        self._floppie = None
        with open('assets/floppie_screensaver.txt', encoding="utf8") as file:
            self._floppie = file.readlines()

        self._floppie = self._floppie[0:-2] # We don't use the las few lines
        self.reset()

    def _update(self, frame_no):
        screen:Screen = self.screen
        if len(self._remaining_lines) >0:
            if frame_no %6 ==0 :            
                y = self._line
                for line in self._print_lines:
                    screen.print_at(line, 2, y)
                    y+=1

                self._line -= 1
                self._print_lines.append(self._remaining_lines.pop(0))
        else:
            if frame_no %3 ==0:
                screen.print_at('^', 7, self._line+1)
                screen.print_at('^', 13, self._line+1)
            else:
                screen.print_at('~', 7, self._line+1)
                screen.print_at('~', 13, self._line+1)                

    def reset(self):
        self._remaining_lines = self._floppie.copy()
        self._line = self.screen.height-2
        self._print_lines = [self._remaining_lines.pop(0)]

    @property
    def stop_frame(self): return 0


def jb_splash(screen:Screen) -> Scene: 
    """
        Generates Jacob's Splash Screen as a Scene
    """   
    # Color of the jb_logo
    logo_color = Screen.COLOUR_WHITE 
    # The time in second the logo should be displayed before the bombardment
    logo_duration = time2frames(0.5) 
    # The number of shots the logo is shot with
    number_of_shots  = 2
    # The time in seconds to wait after the whole sequence is done. 
    # (Black screen time)
    blanking_time = time2frames(0.1)

    #Read the jb_logo text from file
    jb_logo = "Jacob's Splash Screen"
    with open('assets/jb_logo.txt',encoding="utf8") as file:
        jb_logo = file.read()

    effects = []

    #The jb logo effect
    logo_effect = Print(
        screen, 
        StaticRenderer([jb_logo]),
        0,
        0, 
        colour=logo_color,
        stop_frame = logo_duration
    )
    effects.append(logo_effect)

    #The individual shots
    for i in range(1, number_of_shots+1):
        x_pos = randint(screen.width // 3, screen.width * 2 // 3)
        y_pos = randint(screen.height // 4, screen.height * 3 // 4)

        explosion = Explosion(
            screen,
            x_pos,
            y_pos,
            15,
            start_frame = logo_duration + (i * 19)
        )

        shot = ShootScreen(
            screen,
            x_pos,
            y_pos,
            100,
            diameter=randint(5, 10),
            start_frame= logo_duration + (i * 20)
        )


        effects.append(explosion)
        effects.append(shot)

    #The Explosion (explodes the rest of the logo)
    effects.append(Explosion(
        screen,
        screen.width // 2, 
        screen.height // 2,
        15,
        start_frame = logo_duration+(number_of_shots*20)+10
    ))

    #The Final Shot (explodes the rest of the logo)
    effects.append(ShootScreen(
            screen, 
            screen.width // 2, 
            screen.height // 2, 
            100, 
            start_frame=logo_duration+(number_of_shots*20)+15
    ))

    duration = logo_duration + (number_of_shots*20)+ 30 + blanking_time

    return Scene(effects=effects,duration=duration, name="jb_splash")

def jxk_splash(screen:Screen) -> Scene:
    effects = [
        Print(
            screen, 
            StaticRenderer(["Jorian wrote the code lol"]),
            10,
            10,
            colour=Screen.COLOUR_WHITE)
    ]

    return Scene(effects=effects,duration=time2frames(4), name="jxk_splash")

def floppiano_splash(screen:Screen, duration:int) -> Scene:
    """
        Generates the FlopPiano's splash screen as a Scene
    Args:
        screen (Screen): The Screen that will render the Scene
        duration (int):  The duration in number of frames
        txt_file (str): The path the the FlopPiano logo

    Returns:
        Scene: The FlopPiano splash screen as a Scene
    """

    # Read the logo
    floppiano_logo = "FlopPiano Splash Screen"
    with open('assets/floppiano_logo.txt', encoding="utf8") as file:
        floppiano_logo = file.read()
    logo_renderer = StaticRenderer([floppiano_logo])
    # Simple Effect to do the rendering 

    effects = [
        Print(
            screen, 
            logo_renderer,
            0,
            (screen.width//2) - (logo_renderer.max_width//2), 
            colour=Screen.COLOUR_WHITE
        ),
        SlidingFloppie(screen,start_frame = 10)
    ]

    floppiano_scene = Scene(effects=effects,duration=duration)
    
    return floppiano_scene

def splash_screen(screen:Screen, synth):
    """
        Uses the Screen to render a set of splash screen Scenes using 
        native asciimatics.
    Args:
        screen (Screen): The Screen used to render the splash screens
        synth: The synth used to play the startup jingle
    """
    # A list of all the splash screen scenes
    scenes = []
    # Add Jacob's Splash
    scenes.append(jb_splash(screen))
    # Add Jorian's Splash
    scenes.append(jxk_splash(screen))
    # Play the Scenes
    # Add the FlopPiano Splash
    scenes.append(floppiano_splash(screen, time2frames(4)))

    # A thread to play the start up jingle with
    startup_jingle = Thread(
        target=MIDIPlayer.blocking_play, 
        args=(synth, 'assets/startup.mid', -6))
    
    # Start playback
    startup_jingle.start()
    # Start splash scenes
    screen.play(scenes, repeat=False)
    # Ensure the thread stops
    startup_jingle.join()

