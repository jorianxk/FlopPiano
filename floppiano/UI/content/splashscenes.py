from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.renderers import StaticRenderer
from asciimatics.effects import Print
from asciimatics.particles import ShootScreen, Explosion, ExplosionFlames
from random import randint

from ..ascii.util import time2frames


def jb_splash(screen:Screen) -> Scene:    
    # Color of the jb_logo
    logo_color = Screen.COLOUR_WHITE 
    # The time in second the logo should be displayed before the bombardment
    logo_duration = time2frames(1) 
    # The number of shots the logo is shot with
    number_of_shots  = 5
    # The time in seconds to wait after the whole sequence is done. 
    # (Black screen time)
    blanking_time = time2frames(1)

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

def jxk_splash(screen:Screen, duration:int) ->Scene:
    pass


def floppiano_splash(screen:Screen, duration:int, txt_file:str) -> Scene:
    floppiano_logo = "FlopPiano Splash Screen"
    with open(txt_file) as file:
        floppiano_logo = file.read()

    effects = [
        Print(
            screen, 
            StaticRenderer([floppiano_logo]),
            0,
            0, 
            colour=Screen.COLOUR_WHITE
        )
    ]

    floppiano_scene = Scene(effects=effects,duration=duration)
    
    return floppiano_scene

def run_splash(screen:Screen):
    scenes = []

    scenes.append(floppiano_splash(screen,50,"assets/logo3.txt"))
    scenes.append(jb_splash(screen))

    screen.play(scenes,repeat=False)
