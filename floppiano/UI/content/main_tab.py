from asciimatics.widgets import Layout, Label, Button, Divider, VerticalDivider

from floppiano.UI.tabs import Tab
from floppiano.UI.widgets import DynamicFrame, DropDown

from floppiano.synths import (PITCH_BEND_RANGES, OUTPUT_MODES, DriveSynth)


# self.add_effect(
# PopUpDialog(self.app.screen, 'Polyphony changing is not yet supported', ["OK"]))

class Setting():

    def __init__(self, 
                 label_text:str, 
                 options, 
                 on_update, 
                 on_change, 
                 frame:DynamicFrame) -> None:
    
        self._on_update = on_update
        self._on_change = on_change

        layout = Layout([3,9,1,9],fill_frame=False)
        frame.add_layout(layout) 


        layout.add_widget(Label(label_text, align='<'),1)
        layout.add_widget(Label(':', align='^'),2)

        dd_options = []
        if isinstance(options, list):
            for index, value in enumerate(options):
                dd_options.append((value, index))       
        elif isinstance(options, range):
            for value in options:
                dd_options.append((str(value), value))
        else:
            raise ValueError("Options must be a list or a range")

        dd_options = tuple(dd_options)

        self._dd = DropDown(
            options = dd_options,
            start_index = self._on_update(),
            on_change = self._changed,
            fit = False,
        )  
        layout.add_widget(self._dd,3)

    
    def update(self):
        self._dd.value = self._on_update()
    
    def _changed(self):
        self._on_change(self._dd.value)


class MainTab(Tab):
    def __init__(self, app, name: str):
        super().__init__(app, name)

        self.synth:DriveSynth = self.app.resource('synth')

        #Frame Setup
        self.frame = DynamicFrame(
            self.app.screen,
            self.app.screen.height-2,
            self.app.screen.width,
            y=2,
            has_border=True,
            title="Settings",
            can_scroll=False,
            on_update=self.update_settings)
        self.frame.set_theme(self.app.theme)
        
        self.settings = []

        self.settings.append(
            Setting(
                'Spin', 
                ['off', 'on'], 
                lambda: self.synth.__getattribute__('spin'), 
                lambda x: self.synth.__setattr__('spin', x),
                self.frame)
        )

        self.settings.append(
            Setting(
                'Bow', 
                ['off', 'on'], 
                lambda: self.synth.__getattribute__('bow'), 
                lambda x: self.synth.__setattr__('bow', x),
                self.frame)
        )

        self.settings.append(
            Setting(
                'Pitch bend Range', 
                list(PITCH_BEND_RANGES.keys()), 
                lambda: self.synth.__getattribute__('pitch_bend_range'), 
                lambda x: self.synth.__setattr__('pitch_bend_range', x),
                self.frame)
        )

        self.settings.append(
            Setting(
                'Modulation Rate', 
                range(0,128), 
                lambda: self.synth.__getattribute__('modulation_rate'), 
                lambda x: self.synth.__setattr__('modulation_rate', x),
                self.frame)
        )

        self.settings.append(
            Setting(
                'Monophonic Voices', 
                range(0,128), 
                lambda: self.synth.__getattribute__('mono_voices'), 
                lambda x: x,  #self.synth.__setattr__('modulation_rate', x), #TODO
                self.frame)
        )

        self.settings.append(
            Setting(
                'Polyphonic Voices', 
                range(0,128), 
                lambda: self.synth.__getattribute__('poly_voices'), 
                lambda x: self.synth.__setattr__('poly_voices', x),
                self.frame)
        )   

        self.settings.append(
            Setting(
                'Loopback', 
                ['off', 'on'], 
                lambda: self.app.resource('loopback'), 
                lambda x: self.app.action('loopback', x),
                self.frame)
        )   

        self.settings.append(
            Setting(
                'Input Channel', 
                range(0,16), 
                lambda: self.synth.__getattribute__('input_channel'), 
                lambda x: self.synth.__setattr__('input_channel', x),
                self.frame)
        ) 

        self.settings.append(
            Setting(
                'Output Channel', 
                range(0,16), 
                lambda: self.synth.__getattribute__('output_channel'), 
                lambda x: self.synth.__setattr__('output_channel', x),
                self.frame)
        ) 

        self.settings.append(
            Setting(
                'Output Mode', 
                OUTPUT_MODES, 
                lambda: self.synth.__getattribute__('output_mode'), 
                lambda x: self.synth.__setattr__('output_mode', x),
                self.frame)
        ) 

        layout = Layout([1,1],False)
        self.frame.add_layout(layout)

        layout.add_widget(Button('Mute', on_click=None),0)
        layout.add_widget(Button('Reset', on_click=None),1)
        #layout.add_widget(Divider())



        self.frame.fix()
        self.add_effect(self.frame, reset=False)

    def update_settings(self):
        pass

