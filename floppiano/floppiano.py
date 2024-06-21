from asciimatics.screen import Screen, ResizeScreenError
from asciimatics.widgets import Frame, Layout, RadioButtons, CheckBox, Label, Divider, DropdownList, PopUpDialog
from tabs import Tab, TabGroup

import sys


class SoundTab(Tab):
    # Crash Mode = OFF BOW FLIP
    # Spin = ON    OFF
    # Pitch Bend Range = HALF	WHOLE	MINOR 3RD	MAJOR 3RD	FOURTH	FIFTH	OCTAVE
    # Modulation Wave = Sine, Square Saw
    # Reset?

    def __init__(self, screen: Screen, name: str):
        super().__init__(screen, name)

        self.frame = Frame(screen,screen.height-2,screen.width,y=2,has_border=False)
        layout = Layout([1],fill_frame=True)
        self.frame.add_layout(layout)

        # layout.add_widget(Button("Button 1",self.button_clicked))
        # layout.add_widget(Button("Button 2", self.button_clicked))

        crash_modes = [
            ("OFF", 0),
            ("BOW", 1),
            ("FLIP", 2)
        ]

        # self.radButts = RadioButtons(crash_modes,"Crash Modes",on_change=self.button_clicked)
        # layout.add_widget(self.radButts)
        layout.add_widget(DropdownList(crash_modes,"Crash Mode","crash_mode",self.crash_mode,True))

        layout.add_widget(Divider())
        #layout.add_widget(Label("Crash Mode:"))
        layout.add_widget(CheckBox('OFF'))
        # layout.add_widget(CheckBox('BOW'),2)
        # layout.add_widget(CheckBox('FLIP'),3)





        self.frame.fix()
        self.add_effect(self.frame, reset=False)
    
    def crash_mode(self):
        dropdown:DropdownList = self.frame.find_widget('crash_mode')
        self.add_effect(
            PopUpDialog(self.screen, f'Crash Mode:{dropdown.value}', ["OK"]))





def demo(screen, scene):

    tab_group = TabGroup(screen)
    
    tab = SoundTab(screen, "Sound" )
    tab_group.add_tab(tab)
    
    tab = Tab(screen, "Settings")
    tab_group.add_tab(tab)

    tab = Tab(screen, "MIDI Player")
    tab_group.add_tab(tab)

    tab = Tab(screen, "About")
    tab_group.add_tab(tab)

    tab = Tab(screen, "Another")
    tab_group.add_tab(tab)

    tab = Tab(screen, "And Another")
    tab_group.add_tab(tab)

    tab = Tab(screen, "And Another Another")
    tab_group.add_tab(tab)

    tab_group.fix()

    scenes = tab_group.tabs


    screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)


last_scene = None
while True:
    try:
        Screen.wrapper(demo, catch_interrupt=False, arguments=[last_scene])
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene
    except KeyboardInterrupt as ke:
        break


