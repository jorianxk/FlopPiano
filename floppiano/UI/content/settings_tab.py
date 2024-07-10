from asciimatics.widgets import Layout, Label, Button, Divider, VerticalDivider
from asciimatics.widgets.utilities import THEMES

from ..ascii.tabs import Tab
from ..ascii.widgets import DynamicFrame, DropDown

from synths import OUTPUT_MODES, DriveSynth


class SettingsTab(Tab):


    def __init__(self, app, name: str):
        super().__init__(app, name)

        self.synth:DriveSynth = self.app.resource('synth')
        
        # Frame Setup
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

        # Layout for table 
        table_layout = Layout([22,1,22],fill_frame=False)
        self.frame.add_layout(table_layout) 

        #Table header and Horizontal Dividers
        table_layout.add_widget(Label('Modifier', align='^'),0)
        table_layout.add_widget(Label("Setting", align='^'),2)
        table_layout.add_widget(Divider(),0)
        table_layout.add_widget(Divider(),2)

        # Modifier Labels
        table_layout.add_widget(Label('Input Channel', align='<'),0)
        table_layout.add_widget(Label('Output Channel', align='<'),0)
        table_layout.add_widget(Label('Output Mode', align='<'),0)
        table_layout.add_widget(Label('Loopback', align='<'),0)
        table_layout.add_widget(Label('Application Theme', align='<'),0)        

        table_layout.add_widget(VerticalDivider(height=7),1)
        
        # Input / Output Channels
        channels = []
        for channel in range(0,16):
            channels.append((str(channel),channel))

        self.input_channel_dd = DropDown(
            options = channels, 
            start_index = self.synth.input_channel,
            on_change = self.input_channel_changed,
            fit = False)
        table_layout.add_widget(self.input_channel_dd,2)

        self.output_channel_dd = DropDown(
            options = channels, 
            start_index = self.synth.output_channel,
            on_change = self.output_channel_changed,
            fit = False)
        table_layout.add_widget(self.output_channel_dd,2)

        # Output Mode
        self.output_mode_dd = DropDown(
            options = DropDown.list2options(OUTPUT_MODES),
            start_index = self.synth.output_mode,
            on_change = self.output_mode_changed,
            fit = False
        )  
        table_layout.add_widget(self.output_mode_dd, 2)   

        # Loopback
        self.loopback_dd = DropDown(
            options = (('off', False),('on', True)),
            start_index= self.app.resource('loopback'),
            on_change = self.loopback_changed,
            fit = False
        )  
        table_layout.add_widget(self.loopback_dd, 2)

        #Application theme
        themes =[]    
        for index, name in enumerate(THEMES.keys()):
            themes.append((name,name))
        self.theme_dd = DropDown(
            options = themes,
            start_index = self.app.theme,
            on_change = self.theme_changed,
            fit = False
        )  
        table_layout.add_widget(self.theme_dd, 2)

        table_layout.add_widget(Divider(),0)
        table_layout.add_widget(Divider(),1)
        table_layout.add_widget(Divider(),2)

        #-----------------------------Test button-----------------------------#
        test_layout = Layout([1,1,1],fill_frame=False)
        self.frame.add_layout(test_layout)

        test_layout.add_widget(Divider(False),0)
        self.test_button = Button(
                'Test Drives',
                on_click=self.test_clicked,
                add_box=True)
        test_layout.add_widget(self.test_button, 1)
        
        test_layout.add_widget(Divider(False),2)
        
        test_layout.add_widget(Divider(),0)
        test_layout.add_widget(Divider(),1)
        test_layout.add_widget(Divider(),2)


        #----------------------------Synth Log---------------------------------#
        
        # log_layout = Layout([1],fill_frame=True)
        # self.frame.add_layout(log_layout)

        # log_layout.add_widget(Label("Synth Activity:", align='^'))
        # self.loggerText = LoggerText(
        #     height=9, 
        #     disabled =False, 
        #     name = "loggerText")
        # synth_logger.addHandler(self.loggerText)
        # log_layout.add_widget(self.loggerText)       

        self.frame.fix()
        self.add_effect(self.frame, reset=False)

    def update_widgets(self):
        self.input_channel_dd.value = self.synth.input_channel
        self.output_channel_dd.value = self.synth.output_channel
        self.output_mode_dd.value = self.synth.output_mode
        self.loopback_dd.value = self.app.resource('loopback')
        self.theme_dd.value = self.app.theme    

    def input_channel_changed(self):
        self.synth.input_channel = self.input_channel_dd.value

    def output_channel_changed(self):
        self.synth.output_channel = self.output_channel_dd.value
    
    def output_mode_changed(self):
        self.synth.output_mode = self.output_mode_dd.value

    def loopback_changed(self):
        self.app.action('loopback', self.loopback_dd.value)

    def theme_changed(self):
        self.app.action('theme', (self.theme_dd.value, self))

    def test_clicked(self):
        pass
       