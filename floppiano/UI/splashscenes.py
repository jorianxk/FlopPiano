from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.renderers import StaticRenderer
from asciimatics.effects import Print



def jb_splash(screen:Screen, duration:int) -> Scene:
    jb_logo = "Jacob's Splash Screen"
    with open('assets/jb_logo.txt') as file:
        jb_logo = file.read()

    effects = [
        Print(
            screen, 
            StaticRenderer([jb_logo]),
            0,
            0, 
            colour=Screen.COLOUR_WHITE
        )
    ]

    jb_scene = Scene(effects=effects,duration=duration)
    
    return jb_scene

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


    