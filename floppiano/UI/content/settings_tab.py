from asciimatics.screen import Screen
from asciimatics.widgets import ( 
    Frame, Layout, Label, Button, Divider, VerticalDivider, PopUpDialog)
from asciimatics.widgets.utilities import THEMES

from ..ascii.tabs import Tab
from ..ascii.widgets import DropDown, LoggerText

import logging

class SettingsTab(Tab):

    def __init__(
            self,
            screen: Screen, 
            name: str, 
            start_values:dict,
            synth_logger:logging.Logger,
            theme='default'):
        super().__init__(screen, name, theme)

        #Frame Setup
        self.frame = Frame(
            screen,screen.height-2,
            screen.width,y=2,
            has_border=False,
            can_scroll=False,
            reduce_cpu=True)
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
        table_layout.add_widget(Label('Input Channel', align='<'),0)
        table_layout.add_widget(Label('Output Channel', align='<'),0)
        table_layout.add_widget(Label('Output Mode', align='<'),0)
        table_layout.add_widget(Label('Loopback', align='<'),0)
        table_layout.add_widget(Label('Application Theme', align='<'),0)        

        table_layout.add_widget(VerticalDivider(height=7),1)
        
        #Input / Output Channels
        channels = []
        for channel in range(0,16):
            channels.append((str(channel),channel))


        self.input_channel_dd = DropDown(
            options = channels, 
            start_index = str(start_values['input_channel']),
            on_change = self.input_channel,
            fit = False)
        table_layout.add_widget(self.input_channel_dd,2)

        self.output_channel_dd = DropDown(
            options = channels, 
            start_index = str(start_values['output_channel']),
            on_change = self.output_channel,
            fit = False)
        table_layout.add_widget(self.output_channel_dd,2)

        #Output Mode

        output_modes = []
        for index, name in enumerate(start_values['output_modes']):
            output_modes.append((name,index))
        self.output_mode_dd = DropDown(
            options = output_modes,
            start_index = start_values['output_modes'][start_values['output_mode']],
            on_change = self.output_mode,
            fit = False
        )  
        table_layout.add_widget(self.output_mode_dd, 2)   

        #Loopback
        loopbacks = (('OFF', False),('ON', True))
        self.loopback_dd = DropDown(
            options = loopbacks,
            start_index= 'ON' if start_values['loopback'] else 'OFF',
            on_change = self.loopback,
            fit = False
        )  
        table_layout.add_widget(self.loopback_dd, 2)

        #Application theme
        themes =[]    
        for index, name in enumerate(THEMES.keys()):
            themes.append((name,name))
        self.theme_dd = DropDown(
            options = themes,
            start_index = self.theme,
            on_change = self.change_theme,
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
        
        log_layout = Layout([1],fill_frame=True)
        self.frame.add_layout(log_layout)

        log_layout.add_widget(Label("Synth Activity:", align='^'))
        self.loggerText = LoggerText(
            height=9, 
            disabled =False, 
            name = "loggerText")
        synth_logger.addHandler(self.loggerText)
        log_layout.add_widget(self.loggerText)

       

        self.frame.fix()
        self.add_effect(self.frame, reset=False)

    def input_channel(self):
        self.app.do_action(
            'change_synth',
            ('input_channel',self.input_channel_dd.value))

    def output_channel(self):
        self.app.do_action(
            'change_synth',
            ('output_channel',self.output_channel_dd.value))
    
    def output_mode(self):
        self.app.do_action(
            'change_synth',
            ('output_mode',self.output_mode_dd.value))

    def loopback(self):
        self.app.do_action(
            'change_synth',
            ('loopback',self.loopback_dd.value))

    def change_theme(self):
        self.app.do_action('change_theme', (self.theme_dd.value, self))

    def test_clicked(self):
        self.app.do_action('drive_test',0)