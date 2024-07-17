from asciimatics.widgets import Layout, Label, Button, Divider, VerticalDivider

from floppiano.UI.tabs import Tab
from floppiano.UI.widgets import DynamicFrame, DropDown

from floppiano.synths import (PITCH_BEND_RANGES, OUTPUT_MODES, DriveSynth)


# self.add_effect(
# PopUpDialog(self.app.screen, 'Polyphony changing is not yet supported', ["OK"]))


class SoundTab(Tab):
    def __init__(self, app, name: str):
        super().__init__(app, name)

        self.synth:DriveSynth = self.app.resource('synth')

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
        table_layout = Layout([17,1,11,10],fill_frame=False)
        self.frame.add_layout(table_layout) 

        # #Table header and Horizontal Dividers
        # table_layout.add_widget(Label('Modifier', align='^'),0)
        # table_layout.add_widget(Label("Setting", align='^'),2)
        # table_layout.add_widget(Divider(),0)
        # table_layout.add_widget(Divider(),2)

        #Modifier Labels
        table_layout.add_widget(Label('Polyphony', align='>'),0)
        #TODO fix polyphony
        #Polyphony DropDown
        self.polyphony_dd = DropDown(
            options = (('mono', 0),('poly', 1)),
            start_index = self.synth.polyphonic,
            name = 'polyphonies_dd',
            on_change = self.polyphony_changed,
            fit = False
        )  
        table_layout.add_widget(self.polyphony_dd, 2)



        table_layout.add_widget(Label('Spin', align='>'),0)
        #Spin DropDown
        self.spin_dd = DropDown(
            options = (('off', 0), ('on', 1)),
            start_index = self.synth.spin,
            name = 'drive_spin_dd',
            on_change = self.spin_changed,
            fit = False
        )  
        table_layout.add_widget(self.spin_dd, 2)


        table_layout.add_widget(Label('Bow', align='>'),0)
        #Bow DropDown  
        self.bow_dd = DropDown(
            options = (('off', 0),('on', 1)),
            start_index = self.synth.bow,
            name = 'bow_dd',
            on_change = self.bow_changed,
            fit = False,
        )       
        table_layout.add_widget(self.bow_dd, 2)


        table_layout.add_widget(Label('Pitch Bend Range', align='>'),0)
        #Pitch Bend Range DropDown 
        self.pitch_bend_range_dd = DropDown(
            options = DropDown.list2options(list(PITCH_BEND_RANGES.keys())),
            start_index = self.synth.pitch_bend_range,
            name = 'pitch_bend_range_dd',
            on_change = self.pitch_bend_range_changed,
            fit = False
        )  
        table_layout.add_widget(self.pitch_bend_range_dd, 2)  

        table_layout.add_widget(Label('Modulation Rate', align='>'),0)
        #TODO limit the rates to the actual available rates
        modulation_rates = []
        for rate in range(0,128):
            modulation_rates.append((str(rate),rate))
        self.modulation_rate_dd = DropDown(
            options = modulation_rates, 
            start_index = self.synth.modulation_rate,
            on_change = self.modulation_rate_changed,
            fit = False)
        table_layout.add_widget(self.modulation_rate_dd,2)


        table_layout.add_widget(Label('Mute', align='>'),0)
        table_layout.add_widget(Button('Mute',None),2)

        table_layout.add_widget(Label('Reset', align='>'),0)
        table_layout.add_widget(Button('Reset',None),2)


        table_layout.add_widget(Label('Monophonic Voices', align='>'),0)
        self.mono_voices_dd = DropDown(
            options = modulation_rates,  #TODO
            start_index = self.synth.mono_voices,
            on_change = self.modulation_rate_changed,
            fit = False)
        table_layout.add_widget(self.mono_voices_dd,2)

        table_layout.add_widget(Label('Polyphonic Voices', align='>'),0)
        self.poly_voices_dd = DropDown(
            options = modulation_rates,  #TODO
            start_index = self.synth.poly_voices,
            on_change = self.modulation_rate_changed,
            fit = False)
        table_layout.add_widget(self.poly_voices_dd,2)

        table_layout.add_widget(Label('Loopback', align='>'),0)
        self.loopback_dd = DropDown(
            options = (('off', False),('on', True)),
            start_index= self.app.resource('loopback'),
            on_change = self.loopback_changed,
            fit = False
        )  
        table_layout.add_widget(self.loopback_dd, 2)


        channels = []
        for channel in range(0,16):
            channels.append((str(channel),channel))

        table_layout.add_widget(Label('Input Channel', align='>'),0)
        self.input_channel_dd = DropDown(
            options = channels, 
            start_index = self.synth.input_channel,
            on_change = self.input_channel_changed,
            fit = False)
        table_layout.add_widget(self.input_channel_dd,2)


        table_layout.add_widget(Label('Output Channel', align='>'),0)
        self.output_channel_dd = DropDown(
            options = channels, 
            start_index = self.synth.output_channel,
            on_change = self.output_channel_changed,
            fit = False)
        table_layout.add_widget(self.output_channel_dd,2)


        table_layout.add_widget(Label('Output Mode', align='>'),0)
        self.output_mode_dd = DropDown(
            options = DropDown.list2options(OUTPUT_MODES),
            start_index = self.synth.output_mode,
            on_change = self.output_mode_changed,
            fit = False
        )  
        table_layout.add_widget(self.output_mode_dd, 2)   

       

        #table_layout.add_widget(VerticalDivider(height=15),1)




      

        self.frame.fix()
        self.add_effect(self.frame, reset=False)

    def update_widgets(self):
        self.bow_dd.value = self.synth.bow
        self.spin_dd.value = self.synth.spin
        self.pitch_bend_range_dd.value = self.synth.pitch_bend_range
        self.modulation_rate_dd.value = self.synth.modulation_rate
        self.input_channel_dd.value = self.synth.input_channel
        self.output_channel_dd.value = self.synth.output_channel
        self.output_mode_dd.value = self.synth.output_mode
        self.loopback_dd.value = self.app.resource('loopback')

        # Drives only have one modulation wave
        #self.modulation_wave_dd.value = self.synth.modulation_wave
        #self.polyphony_dd.value = self.synth.polyphonic

    def bow_changed(self):
        self.synth.bow = self.bow_dd.value    
    def spin_changed(self):
        self.synth.spin = self.spin_dd.value
    def pitch_bend_range_changed(self):
        self.synth.pitch_bend_range = self.pitch_bend_range_dd.value
    def modulation_rate_changed(self):
        self.synth.modulation_rate = self.modulation_rate_dd.value
    # Drives only have one modulation wave
    # def modulation_wave_changed (self):
    #     self.synth.modulation_wave = self.modulation_wave_dd.value

    def polyphony_changed (self):
        #self.synth.polyphonic = self.polyphony_dd.value
        pass

    def input_channel_changed(self):
        self.synth.input_channel = self.input_channel_dd.value

    def output_channel_changed(self):
        self.synth.output_channel = self.output_channel_dd.value
    
    def output_mode_changed(self):
        self.synth.output_mode = self.output_mode_dd.value

    def loopback_changed(self):
        self.app.action('loopback', self.loopback_dd.value)