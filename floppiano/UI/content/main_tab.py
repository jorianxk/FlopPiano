from asciimatics.widgets import Layout, Button
from floppiano.UI.tabs import Tab
from floppiano.UI.widgets import DynamicFrame, FloppieWidget, Setting
from floppiano.synths import (PITCH_BEND_RANGES, OUTPUT_MODES, DriveSynth)



class MainTab(Tab):
    """
        A tab for showing/setting Synth and application settings.
    """

    def __init__(self, app, name: str):
        super().__init__(app, name)

        # Get the App's Synth
        self._synth:DriveSynth = self.app.resource('synth')

        #Setup the Frame
        self._frame = DynamicFrame(
            self.app.screen,
            self.app.screen.height-2,
            self.app.screen.width,
            y=2,
            has_border=False,
            can_scroll=False,
            on_update=self._update_widgets)
        self._frame.set_theme(self.app.theme)
        
        # A list of all the settings on the page
        self._settings:list[Setting] = []

        # Create all the settings' UI elements

        self._settings.append(
            Setting(
                label_text = 'Spin', 
                options = ['off', 'on'], 
                on_update = lambda: self._synth.__getattribute__('spin'), # On update just read the synth's attribute and match it
                on_change = lambda x: self._synth.__setattr__('spin', x), # Make the synth change
                frame = self._frame,
                tool_tip = "Controls the floppy drive platters. 'on' = the platters will spin!")
        )

        self._settings.append(
            Setting(
                label_text = 'Bow', 
                options = ['off', 'on'], 
                on_update = lambda: self._synth.__getattribute__('bow'), 
                on_change = lambda x: self._synth.__setattr__('bow', x),
                frame = self._frame,
                tool_tip = "How the floppy drive heads move. 'on' = heads move to-and-fro!")
        )

        self._settings.append(
            Setting(
                label_text = 'Polyphony', 
                options = ['monophonic', 'polyphonic'], 
                on_update = lambda: self._synth.__getattribute__('polyphonic'), 
                on_change = self._polyphony_changed,
                frame = self._frame,
                tool_tip = "Sets the polyphony.") 
        )

        self._settings.append(
            Setting(
                label_text = 'Pitch bend Range', 
                options = list(PITCH_BEND_RANGES.keys()), 
                on_update = lambda: self._synth.__getattribute__('pitch_bend_range'), 
                on_change = lambda x: self._synth.__setattr__('pitch_bend_range', x),
                frame = self._frame,
                tool_tip = "Changes how far the pitchwheel will bend a note at its extreme position.")
        )

        self._settings.append(
            Setting(
                label_text = 'Modulation Rate', 
                options = range(0,128), 
                on_update = lambda: self._synth.__getattribute__('modulation_rate'), 
                on_change = lambda x: self._synth.__setattr__('modulation_rate', x),
                frame = self._frame,
                tool_tip = "The amount in Hz to add to a note when modulating. A.K.A. modulation attack.")
        )

        self._settings.append(
            Setting(
                label_text = 'Monophonic Voices', 
                options = range(0,128), 
                on_update = lambda: self._synth.__getattribute__('mono_voices'),
                # _mono_voices is a private variable only edit if you know what you're doing
                on_change = lambda x: self._synth.__setattr__('_mono_voices', x), 
                frame = self._frame,
                tool_tip = "The number of voices to use when monophonic. '0' = max voices")
        )

        self._settings.append(
            Setting(
                label_text = 'Polyphonic Voices', 
                options = range(0,128), 
                on_update = lambda: self._synth.__getattribute__('poly_voices'), 
                on_change = lambda x: self._synth.__setattr__('poly_voices', x),
                frame = self._frame,
                tool_tip = "The number of voices to use when polyphonic. '0' = max voices")
        )   

        self._settings.append(
            Setting(
                label_text = 'Loopback', 
                options = ['off', 'on'], 
                on_update = lambda: self.app.resource('loopback'), 
                on_change = lambda x: self.app.action('loopback', x),
                frame = self._frame,
                tool_tip = "When 'on' the MIDI notes generated by the keyboard will be played.")
        )   

        self._settings.append(
            Setting(
                label_text = 'Input Channel', 
                options = range(0,16), 
                on_update = lambda: self._synth.__getattribute__('input_channel'), 
                on_change = lambda x: self._synth.__setattr__('input_channel', x),
                frame = self._frame,
                tool_tip = "The incoming MIDI channel.")
        ) 

        self._settings.append(
            Setting(
                label_text = 'Output Channel', 
                options = range(0,16), 
                on_update = lambda: self._synth.__getattribute__('output_channel'), 
                on_change = lambda x: self._synth.__setattr__('output_channel', x),
                frame = self._frame,
                tool_tip = "The outgoing MIDI channel.")
        ) 

        self._settings.append(
            Setting(
                label_text = 'Output Mode', 
                options = OUTPUT_MODES, 
                on_update = lambda: self._synth.__getattribute__('output_mode'), 
                on_change = lambda x: self._synth.__setattr__('output_mode', x),
                frame = self._frame,
                tool_tip = "What MIDI gets output. 'rollover' = MIDI that could not be played.")
        ) 

        # Mute and Reset Buttons 

        layout = Layout([1,1],False)
        self._frame.add_layout(layout)

        self._mute_button = Button('Mute', on_click=self._mute_clicked)
        layout.add_widget(self._mute_button,0)

        self._reset_button = Button('Reset', on_click=self._reset_clicked)
        layout.add_widget(self._reset_button,1)
        
        layout = Layout([1], False)
        self._frame.add_layout(layout)
        self._floppie = FloppieWidget()
        layout.add_widget(self._floppie)
        
        self._frame.fix()
        self.add_effect(self._frame, reset=False)

    def _update_widgets(self):        
        # Update the settings (DropDowns) and update the tool tip as necessary
        for setting in self._settings:
            setting.update()
            if setting.selected:
                self._floppie.value = setting.tool_tip
        
        # Handle button (non-setting tool-tips)
        if self._mute_button._has_focus:
            self._floppie.value = "Mutes all sounding voices."
        
        if self._reset_button._has_focus:
            self._floppie.value = "Resets all sounding voices and un-mutes."

    def _mute_clicked(self):
        # Mute the synth
        self._synth.mute()

    def _reset_clicked(self):
        # Reset the synth
        self._synth.reset()
    
    def _polyphony_changed(self, polyphonic:bool):
        if polyphonic:
            #uses synth property poly_voices to become polyphonic
            self._synth.poly_mode()
        else:
            # _mono_voices is a private variable which is set by the Monophonic
            # Voices setting. tldr: this is a hacky work around because MIDI cc
            # 126 sets how many voices to use when monophonic
            self._synth.mono_mode(self._synth._mono_voices)

