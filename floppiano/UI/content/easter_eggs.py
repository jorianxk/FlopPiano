from asciimatics.effects import Print
from asciimatics.renderers import ImageFile
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from floppiano.UI.util import time2frames


def rick_roll_screen(screen:Screen):
    scenes = []
    effects = [
        Print(screen, ImageFile("assets/roll.gif", screen.height - 2, colours=screen.colours),
              1,
              stop_frame=time2frames(60)),
     ]
    scenes.append(Scene(effects))

    # # A thread to play the start up jingle with
    # startup_jingle = Thread(
    #     target=MIDIPlayer.blocking_play, 
    #     args=(synth, 'assets/startup.mid', -6))
    
    # Start playback
    #startup_jingle.start()
    # Start splash scenes
    screen.play(scenes, repeat=False)
    # Ensure the thread stops
    #startup_jingle.join()