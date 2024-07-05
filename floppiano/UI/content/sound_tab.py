from asciimatics.widgets import ( 
    Layout, Label, Button, Divider, VerticalDivider, PopUpDialog)

from ..ascii.tabs import Tab
from ..ascii.widgets import DynamicFrame, DropDown


from jidi2.synths import (PITCH_BEND_RANGES, MODULATION_WAVES, DriveSynth)


# self.add_effect(
# PopUpDialog(self.app.screen, 'Polyphony changing is not yet supported', ["OK"]))


class SoundTab(Tab):

    def __init__(self, app, name: str):
        super().__init__(app, name)

        #Frame Setup
        self.frame = DynamicFrame(
            self.app.screen,
            self.app.screen.height-2,
            self.app.screen.width,
            y=2,
            has_border=False,
            can_scroll=False,
            on_update=self.update_widgets)
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
        table_layout.add_widget(Label('Bow', align='<'),0)
        table_layout.add_widget(Label('Drive Spin', align='<'),0)
        table_layout.add_widget(Label('Pitch Bend Range', align='<'),0)
        table_layout.add_widget(Label('Modulation Wave', align='<'),0)
        table_layout.add_widget(Label('Polyphony', align='<'),0)        

        table_layout.add_widget(VerticalDivider(height=7),1)

        self.synth:DriveSynth = self.app.resource('synth')

        #Bow DropDown  
        self.bow_dd = DropDown(
            options = (('off', 0),('on', 1)),
            start_index = self.synth.bow,
            name = 'bow_dd',
            on_change = self.bow,
            fit = False,
        )       
        table_layout.add_widget(self.bow_dd, 2)
    
        #Drive Spin DropDown
        self.drive_spin_dd = DropDown(
            options = (('off', 0), ('on', 1)),
            start_index = self.synth.spin,
            name = 'drive_spin_dd',
            on_change = self.drive_spin,
            fit = False
        )  
        table_layout.add_widget(self.drive_spin_dd, 2)

        #Pitch Bend Range DropDown 
        self.pitch_bend_range_dd = DropDown(
            options = DropDown.list2options(list(PITCH_BEND_RANGES.keys())),
            start_index = self.synth.pitch_bend_range,
            name = 'pitch_bend_range_dd',
            on_change = self.pitch_bend_range,
            fit = False
        )  
        table_layout.add_widget(self.pitch_bend_range_dd, 2)     
        
        #Modulation Wave DropDown
        self.modulation_wave_dd = DropDown(
            options = DropDown.list2options(MODULATION_WAVES),
            start_index = self.synth.modulation_wave,
            name = 'modulation_wave_dd',
            on_change = self.modulation_wave,
            fit = False
        )  
        table_layout.add_widget(self.modulation_wave_dd, 2)    

        #Polyphony DropDown
        self.polyphony_dd = DropDown(
            options = (('mono', 0),('poly', 1)),
            start_index = self.synth.polyphonic,
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
      

        self.frame.fix()
        self.add_effect(self.frame, reset=False)

    def update_widgets(self):
        self.bow_dd.value = self.synth.bow
        self.drive_spin_dd.value = self.synth.spin
        self.pitch_bend_range_dd.value = self.synth.pitch_bend_range
        self.modulation_wave_dd.value = self.synth.modulation_wave
        self.polyphony_dd.value = self.synth.polyphonic

    def bow(self):
        self.synth.bow = self.bow_dd.value    
    def drive_spin(self):
        self.synth.spin = self.drive_spin_dd.value
    def pitch_bend_range(self):
        self.synth.pitch_bend_range = self.pitch_bend_range_dd.value
    def modulation_wave (self):
        self.synth.modulation_wave = self.modulation_wave_dd.value
    def reset_clicked(self):
        self.synth.reset()    
    def polyphony (self):
        self.synth.polyphonic = self.polyphony_dd.value
