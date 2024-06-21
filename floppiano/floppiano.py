from asciimatics.screen import Screen, ResizeScreenError
from asciimatics.scene import Scene
from asciimatics.widgets import Frame, Layout, Label, Button, RadioButtons, ListBox, Divider

from tab_group import TabGroup
from tab import Tab
import sys



# class Shit():
#     def __init__(self) -> None:
#         self.width = 45

# try:

#     tab_group = ["Sound", "Settings", "MIDI Player", "About"]
#     th = TabHeaders(Shit(), tab_group)
# except Exception as e:
#     pass


# exit(0)

def demo(screen, scene):

    tab_group = TabGroup(screen)

    
    tab = Tab(screen, "Sound")
    tab_group.add_tab(tab)
    
    tab = Tab(screen, "Settings")
    tab_group.add_tab(tab)

    # tab = Tab(screen, "MIDI Player")
    # tab_group.add_tab(tab)

    # tab = Tab(screen, "About")
    # tab_group.add_tab(tab)

    tab_group.fix()


    #tab_group = ["Sound", "Settings", "MIDI Player", "About"]



    scenes = tab_group.tabs()



    screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)


last_scene = None
while True:
    try:
        Screen.wrapper(demo, catch_interrupt=False, arguments=[last_scene])
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene