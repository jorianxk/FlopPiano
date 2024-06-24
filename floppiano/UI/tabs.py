from asciimatics.screen import Screen
from asciimatics.effects import Cycle
from asciimatics.renderers import FigletText
from asciimatics.exceptions import ResizeScreenError
from asciimatics.widgets.utilities import THEMES
from asciimatics.widgets import (
    Frame, Layout, Label, Button, TextBox, Divider, VerticalDivider, 
    FileBrowser, Widget, PopUpDialog)


from mido import Message
#from floppiano.UI.app import App
#from floppiano.UI.extentions import TabHeader

from .extentions import Tab, DropDown, LoggerText


from jidi.devices import Drive
from jidi.voices import PitchBendRange, ModulationWave

import logging
import os


# dropdown:DropdownList = self.frame.find_widget('crash_mode')
# self.add_effect(
#     PopUpDialog(self.screen, f'Crash Mode:{dropdown.value}', ["OK"]))



class SoundTab(Tab):
    def __init__(
            self, 
            screen: Screen, 
            name: str, 
            start_values:dict,
            synth_logger:logging.Logger,
            theme = 'default'):
        
        super().__init__(screen, name, theme)

        #Frame Setup
        self.frame = Frame(
            screen,screen.height-2,
            screen.width,y=2,
            has_border=False,
            can_scroll=False)
        self.frame.set_theme(self.theme)
   
        #--------------------Table Layout and Widgets--------------------------#

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
        start_crash_mode = None
        for mode_name, mode_value in Drive.CrashMode.__members__.items():
            if mode_value == start_values['crash_mode']: 
                start_crash_mode=mode_name
            crash_modes.append((mode_name,mode_value))
        self.crash_mode_dd = DropDown(
            options = crash_modes,
            start_option = start_crash_mode,
            name = 'crash_mode_dd',
            on_change = self.crash_mode,
            fit = False,
        )       
        table_layout.add_widget(self.crash_mode_dd, 2)
    
        #Drive Spin DropDown
        drive_spins = (('OFF', False),('ON', True))
        self.drive_spin_dd = DropDown(
            options = drive_spins,
            start_option= 'ON' if start_values['spin'] else 'OFF',
            name = 'drive_spin_dd',
            on_change = self.drive_spin,
            fit = False
        )  
        table_layout.add_widget(self.drive_spin_dd, 2)

        #Pitch Bend Range DropDown
        pitch_bend_ranges =[]
        self.start_pitch_bend_range = None
        for index, name in enumerate(PitchBendRange.__members__.keys()):
            if name == PitchBendRange(start_values['pitch_bend_range']).name:
                self.start_pitch_bend_range = name
            pitch_bend_ranges.append((name,index))

        self.pitch_bend_range_dd = DropDown(
            options = pitch_bend_ranges,
            start_option = self.start_pitch_bend_range,
            name = 'pitch_bend_range_dd',
            on_change = self.pitch_bend_range,
            fit = False
        )  
        table_layout.add_widget(self.pitch_bend_range_dd, 2)     
        
        #Modulation Wave DropDown
        modulation_waves = []
        start_modulation_wave = None
        for wave_name, wave_value in ModulationWave.__members__.items():
            if wave_value == start_values['modulation_wave']:
                start_modulation_wave = wave_name
            modulation_waves.append((wave_name,wave_value))
        self.modulation_wave_dd = DropDown(
            options = modulation_waves,
            start_option = start_modulation_wave,
            name = 'modulation_wave_dd',
            on_change = self.modulation_wave,
            fit = False
        )  
        table_layout.add_widget(self.modulation_wave_dd, 2)    

        #Polyphony DropDown
        polyphonies = (('MONO', False),('POLY', True))
        self.polyphony_dd = DropDown(
            options = polyphonies,
            start_option =  'POLY' if start_values['polyphony'] else 'MONO',
            name = 'polyphonies_dd',
            on_change = self.polyphony,
            fit = False
        )  
        table_layout.add_widget(self.polyphony_dd, 2)

        #-----------------------------Reset button-----------------------------#
        reset_layout = Layout([1,1,1],fill_frame=False)
        self.frame.add_layout(reset_layout)
        
        reset_layout.add_widget(Divider(),0)
        reset_layout.add_widget(Divider(),1)
        reset_layout.add_widget(Divider(),2)

        reset_layout.add_widget(Divider(False),0)
        self.reset_button = Button(
                'Reset Drives',
                on_click=self.reset_clicked,
                add_box=True)
        reset_layout.add_widget(self.reset_button, 1)
        
        reset_layout.add_widget(Divider(False),2)
        
        reset_layout.add_widget(Divider(),0)
        reset_layout.add_widget(Divider(),1)
        reset_layout.add_widget(Divider(),2)

        #----------------------------Synth Log---------------------------------#
        
        log_layout = Layout([1],fill_frame=True)
        self.frame.add_layout(log_layout)

        log_layout.add_widget(Label("Synth Activity:", align='^'))
        self.loggerText = LoggerText(
            height=9, 
            disabled =True, 
            name = "loggerText")
        synth_logger.addHandler(self.loggerText)
        log_layout.add_widget(self.loggerText)
       
        

        #Frames must be the last one added to have input focus
        self.frame.fix()
        self.add_effect(self.frame, reset=False)


    def crash_mode(self):
        self.app.do_action(
            'change_synth',
            ('crash_mode',self.crash_mode_dd.value))
    
    def drive_spin(self):
        self.app.do_action(
            'change_synth',
            ('spin',self.drive_spin_dd.value))

    def pitch_bend_range(self):
        self.app.do_action(
            'change_synth',
            ('pitch_bend_range',self.pitch_bend_range_dd.value))


    def modulation_wave (self):
        self.app.do_action(
            'change_synth',
            ('modulation_wave',self.modulation_wave_dd.value))


    def reset_clicked(self):
        self.app.do_action(
            'change_synth',
            ('reset',0))
    
    def polyphony (self):
         #TODO update this when polyphone switching support is added to synth
         self.add_effect(
            PopUpDialog(self.screen, 'Polyphony changing is not yet supported', ["OK"]))

class AboutTab(Tab):

    def __init__(self, screen: Screen, name: str, logger:logging.Logger = None, theme='default'):
        super().__init__(screen, name, theme)

        #Frame Setup
        self.frame = Frame(screen,screen.height-2,screen.width,y=2,has_border=False, can_scroll=False)
        self.frame.set_theme(self.theme)    

        layout = Layout([1],True)
        self.frame.add_layout(layout)

        layout.add_widget(Label('About The FlopPiano:', align='^'))
        about_text = TextBox(10,readonly=True,line_wrap=True)
        layout.add_widget(about_text)
        about_text.value = ['This is some about text about us', 'Jorian Hates asciimattics','Farts']


        layout.add_widget(Label("Application Log:", align='^'))
        loggerText = LoggerText(height=4)
        if logger is not None:
            logger.addHandler(loggerText)
        layout.add_widget(loggerText)


        self.frame.fix()
        self.add_effect(self.frame, reset=False)


class MIDIPlayerTab(Tab):

    def __init__(self, screen: Screen, name: str, theme='default'):
        super().__init__(screen, name, theme)

        # Frame Setup
        self.frame = Frame(screen,screen.height-2,screen.width,y=2,has_border=False, can_scroll=False)
        self.frame.set_theme(self.theme)

        #Layout for Frame
        layout = Layout([1],fill_frame=True)
        self.frame.add_layout(layout) 

        layout.add_widget(Label("Transpose:", align='^'))
        transposes = []
        for i in range(-12,13):
            transposes.append((str(i),i))
        self.transpose_dd = DropDown(options=transposes, start_option="0")

        layout.add_widget(self.transpose_dd)

        layout.add_widget(Label("MIDI File:", align='^'))
        self.file_browser = FileBrowser(Widget.FILL_FRAME,
                            os.path.abspath("./assets/Testing_MIDI/"),
                            name="mc_list",
                            on_select=self.popup,
                            on_change=None,
                            file_filter=".*.mid$")
        layout.add_widget(self.file_browser)
        
        #Frames must be the last one added to have input focus
        self.frame.fix()
        self.add_effect(self.frame, reset=False)
    
    def play(self, file:str, transpose:int):
        self.app.do_action('play_mid_file', (file, transpose))

    def stop(self, button):
        self.app.do_action('stop_mid_file')
    
    def popup(self):
        #TODO: fix int() below
        self.play(self.file_browser.value, int(self.transpose_dd.value))

        file_display_text = str(self.file_browser.value).split("/")[-1]
        self.add_effect(
            PopUpDialog(self.screen, f'Playing {file_display_text}', ["STOP"],on_close=self.stop))


class SettingsTab(Tab):

    def __init__(self, screen: Screen, name: str, theme='default'):
        super().__init__(screen, name, theme)

        #Frame Setup
        self.frame = Frame(screen,screen.height-2,screen.width,y=2,has_border=False, can_scroll=False)
        self.frame.set_theme(self.theme)       

        layout = Layout([1],True)
        self.frame.add_layout(layout)

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
        self.app.do_action('change_theme', dd.value)

    