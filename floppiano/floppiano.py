from asciimatics.screen import Screen, ResizeScreenError, NextScene
from asciimatics.widgets.utilities import THEMES
from asciimatics.widgets import Frame, Layout, Button, Label, Divider, VerticalDivider, TextBox, PopUpDialog
from asciimatics.effects import BannerText, Cycle, Matrix
from asciimatics.renderers import FigletText
from UIExtensions import Tab, TabGroup, DropDown
from jidi.devices.drive import Drive
from jidi.voices import PitchBendRange, ModulationWave

import sys

app_theme = 'default'

class SoundTab(Tab):
    # Crash Mode = OFF BOW FLIP
    # Spin = ON    OFF
    # Pitch Bend Range = HALF	WHOLE	MINOR 3RD	MAJOR 3RD	FOURTH	FIFTH	OCTAVE
    # Modulation Wave = Sine, Square Saw
    # Reset?

    def __init__(self, screen: Screen, name: str, theme = 'default'):
        super().__init__(screen, name, theme)

        #Frame Setup
        self.frame = Frame(screen,screen.height-12,screen.width,y=2,has_border=False, can_scroll=False)
        self.frame.set_theme(self.theme)
   
        #Layout for table 
        table_layout = Layout([22,1,22],fill_frame=False)
        self.frame.add_layout(table_layout) 

        #Table header and Horizontal Dividers
        table_layout.add_widget(Label('Modifier', align='^'),0)
        table_layout.add_widget(Label("Setting", align='^'),2)
        table_layout.add_widget(Divider(),0)
        table_layout.add_widget(Divider(),2)

        #Modifier Labels
        table_layout.add_widget(Label('Crash Mode', align='<'),0)
        table_layout.add_widget(Label('Drive Spin', align='<'),0)
        table_layout.add_widget(Label('Pitch Bend Range', align='<'),0)
        table_layout.add_widget(Label('Modulation Wave', align='<'),0)
        table_layout.add_widget(Label('Polyphony', align='<'),0)

        

        table_layout.add_widget(VerticalDivider(height=7),1)

        #Crash Mode DropDown
        crash_modes = []
        for mode_name, mode_value in Drive.CrashMode.__members__.items():
            crash_modes.append((mode_name,mode_value))
        crash_mode_dd = DropDown(
            options = crash_modes,
            name = 'crash_mode_dd',
            on_change = self.crash_mode,
            fit = False,
        )       
        table_layout.add_widget(crash_mode_dd, 2)
    
        #Drive Spin DropDown
        drive_spins = (('OFF', False),('ON', True))
        drive_spin_dd = DropDown(
            options = drive_spins,
            name = 'drive_spin_dd',
            on_change = self.drive_spin,
            fit = False
        )  
        table_layout.add_widget(drive_spin_dd, 2)

        #Pitch Bend Range DropDown
        pitch_bend_ranges =[]
        for index, name in enumerate(PitchBendRange.__members__.keys()):
            pitch_bend_ranges.append((name,index))
        pitch_bend_range_dd = DropDown(
            options = pitch_bend_ranges,
            name = 'pitch_bend_range_dd',
            on_change = self.pitch_bend_range,
            fit = False
        )  
        table_layout.add_widget(pitch_bend_range_dd, 2)     
        
        #Modulation Wave DropDown
        modulation_waves = []
        for wave_name, wave_value in ModulationWave.__members__.items():
            modulation_waves.append((wave_name,wave_value))
        modulation_wave_dd = DropDown(
            options = modulation_waves,
            name = 'modulation_wave_dd',
            on_change = self.modulation_wave,
            fit = False
        )  
        table_layout.add_widget(modulation_wave_dd, 2)    

        #Polyphony DropDown
        polyphonies = (('MONO', False),('POLY', True))
        polyphony_dd = DropDown(
            options = polyphonies,
            name = 'polyphonies_dd',
            on_change = self.polyphony,
            fit = False
        )  
        table_layout.add_widget(polyphony_dd, 2)

        reset_layout = Layout([1,1,1],fill_frame=False)
        self.frame.add_layout(reset_layout)
        
        reset_layout.add_widget(Divider(),0)
        reset_layout.add_widget(Divider(),1)
        reset_layout.add_widget(Divider(),2)

        reset_layout.add_widget(Divider(False),0)
        reset_layout.add_widget(Button('Reset Voices', on_click=self.reset_button,add_box=True),1)
        reset_layout.add_widget(Divider(False),2)
        
        reset_layout.add_widget(Divider(),0)
        reset_layout.add_widget(Divider(),1)
        reset_layout.add_widget(Divider(),2)


        

        self.add_effect(Cycle(
            self.screen,    
            FigletText("FlopPiano", font='small'),
            14)
        )

        #Frames must be the last one added to have input focus
        self.frame.fix()
        self.add_effect(self.frame, reset=False)


    def crash_mode(self):
        pass
    
    def drive_spin(self):
        pass

    def pitch_bend_range(self):
        pass

    def modulation_wave (self):
        pass

    def reset_button(self):
        pass
    
    def polyphony (self):
        pass


    
# dropdown:DropdownList = self.frame.find_widget('crash_mode')
# self.add_effect(
#     PopUpDialog(self.screen, f'Crash Mode:{dropdown.value}', ["OK"]))
class AboutTab(Tab):

    def __init__(self, screen: Screen, name: str, theme='default'):
        super().__init__(screen, name, theme)

        #Frame Setup
        self.frame = Frame(screen,screen.height-2,screen.width,y=2,has_border=False, can_scroll=False)
        self.frame.set_theme(self.theme)    

        layout = Layout([1],True)
        self.frame.add_layout(layout)

        about_text = TextBox(10,readonly=True,line_wrap=True)
        layout.add_widget(about_text)
        about_text.value = ['This is some about text', 'This is a newline']

        layout.add_widget(Label('Application Theme:', align='^'))  

        #Theme
        themes =[]    
        for index, name in enumerate(THEMES.keys()):
            themes.append((name,name))
        theme_dd = DropDown(
            options = themes,
            start_option = self.theme,
            name = 'theme_dd',
            on_change = self.set_theme,
            fit = False
        )  
        layout.add_widget(theme_dd)


        self.frame.fix()
        self.add_effect(self.frame, reset=False)

    def set_theme(self):
        dd:DropDown = self.frame.find_widget('theme_dd')
        global app_theme
        app_theme = dd.value
        
        dd.value = "default"
        #Resize error to force all scenes to re-instantiate
        #raise ResizeScreenError("Changed theme", self)

        
    


def demo(screen, scene):

    global app_theme

    tab_group = TabGroup(screen)
    
    tab = SoundTab(screen, "Sound", app_theme)
    tab_group.add_tab(tab)
    
    tab = Tab(screen, "Behavior", app_theme)
    tab_group.add_tab(tab)

    tab = Tab(screen, "MIDI Player", app_theme)
    tab_group.add_tab(tab)

    tab = AboutTab(screen, "About", app_theme)
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


