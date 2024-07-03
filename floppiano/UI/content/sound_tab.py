from asciimatics.widgets import ( 
    Frame, Layout, Label, Button, Divider, VerticalDivider, PopUpDialog)

# from floppiano.UI.app import App
from jidi.devices import Drive
from jidi.voices import PitchBendRange, ModulationWave

from ..ascii.tabs import Tab
from ..ascii.widgets import DropDown

class SoundTab(Tab):

    def __init__(self, app, name: str):
        super().__init__(app, name)


        #Frame Setup
        self.frame = Frame(
            self.app.screen,
            self.app.screen.height-2,
            self.app.screen.width,
            y=2,
            has_border=False,
            can_scroll=False,
            reduce_cpu=True)
        self.frame.set_theme(self.app.theme)
   
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
            # if mode_value == start_values['crash_mode']: 
            #     start_crash_mode=mode_name
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
            start_option= None, #'ON' if start_values['spin'] else 'OFF',
            name = 'drive_spin_dd',
            on_change = self.drive_spin,
            fit = False
        )  
        table_layout.add_widget(self.drive_spin_dd, 2)

        #Pitch Bend Range DropDown
        pitch_bend_ranges =[]
        self.start_pitch_bend_range = None
        for index, name in enumerate(PitchBendRange.__members__.keys()):
            # if name == PitchBendRange(start_values['pitch_bend_range']).name:
            #     self.start_pitch_bend_range = name
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
            # if wave_value == start_values['modulation_wave']:
            #     start_modulation_wave = wave_name
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
            start_option =  None ,#'POLY' if start_values['polyphony'] else 'MONO',
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
      

        #Frames must be the last one added to have input focus
        self.frame.fix()
        self.add_effect(self.frame, reset=False)


    def crash_mode(self):
        self.app.action(
            'change_synth',
            ('crash_mode',self.crash_mode_dd.value))
    
    def drive_spin(self):
        self.app.action(
            'change_synth',
            ('spin',self.drive_spin_dd.value))

    def pitch_bend_range(self):
        self.app.action(
            'change_synth',
            ('pitch_bend_range',self.pitch_bend_range_dd.value))


    def modulation_wave (self):
        self.app.action(
            'change_synth',
            ('modulation_wave',self.modulation_wave_dd.value))


    def reset_clicked(self):
        self.app.action(
            'change_synth',
            ('reset',0))
    
    def polyphony (self):
         #TODO update this when polyphone switching support is added to synth
         self.add_effect(
            PopUpDialog(self.app.screen, 'Polyphony changing is not yet supported', ["OK"]))