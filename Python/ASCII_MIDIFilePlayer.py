#!/usr/bin/env python3

from asciimatics.event import KeyboardEvent
from asciimatics.widgets import Frame, Layout, FileBrowser, Widget, Label, PopUpDialog, Text, \
    Divider
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, StopApplication
import sys
import os

from FlopPiano.MIDI import MIDIParser
from FlopPiano.Conductor import Conductor
import mido
from threading import Event, Thread


def play(stop_flag:Event, file:str):
    conductor = Conductor((8, 9, 10 ,11, 12, 13, 14, 15, 16, 17))
    parser = MIDIParser(conductor)

    for msg in mido.MidiFile(file).play():
        if stop_flag.is_set(): break

        if (msg.type == "note_on" or msg.type =="note_off"):
            msg.note = msg.note -12

        parser.parse(msg)
        conductor.conduct()

    conductor.silence()
    

class DemoFrame(Frame):
    def __init__(self, screen):
        super(DemoFrame, self).__init__(
            screen, screen.height, screen.width, has_border=False, name="My Form")

        # Create the (very simple) form layout...
        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)


        self.status_label = Label("Press Enter to select (or `q` to quit.)")
        #self.status_label = True
        #self.status_label.custom_colour = "field"
        # Now populate it with the widgets we want to use.
        self._list = FileBrowser(Widget.FILL_FRAME,
                                 os.path.abspath("."),
                                 name="mc_list",
                                 on_select=self.play,
                                 on_change = self.selectChanged)
        layout.add_widget(Label("Ascii MIDI Player"))
        layout.add_widget(Divider())
        layout.add_widget(self._list)
        layout.add_widget(Divider())
        layout.add_widget(self.status_label)

        # Prepare the Frame for use.
        self.fix()

        self.stop_flag = Event()
        self.playThread = None

    def play(self):
        if self._list.value.endswith(".mid"):
            self.playThread = Thread(target=play, daemon= True, args=(self.stop_flag, self._list.value))
            self.playThread.start()
            self._scene.add_effect(
                PopUpDialog(self._screen, f"Playing '{self._list.value}'", ["Stop"], on_close=self.stopPlaying))
        else:
            self._scene.add_effect(
                PopUpDialog(self._screen, f"Can't play '{self._list.value}' - it's not a MIDI file!", ["OK"]))
        # Just confirm whenever the user actually selects something.
        # self._scene.add_effect(
        #     PopUpDialog(self._screen, "You selected: {}".format(self._list.value), ["OK"]))

    def selectChanged(self):
        if self._list.value.endswith(".mid"):
            self.status_label.text = "Press Enter to play the selected .MID file. (or `q` to quit.)"
        else:
            self.status_label.text = "Press Enter to select (or `q` to quit.)"


    def stopPlaying(self, some_param):
        self.stop_flag.set()
        self.playThread.join()
        self.stop_flag.clear()

    def process_event(self, event):
        # Do the key handling for this Frame.
        if isinstance(event, KeyboardEvent):
            if event.key_code in [ord('q'), ord('Q'), Screen.ctrl("c")]:
                if self.playThread is not None:
                    if self.playThread.is_alive():
                        self.stopPlaying(0)
                raise StopApplication("User quit")

        # Now pass on to lower levels for normal handling of the event.
        return super(DemoFrame, self).process_event(event)


def demo(screen, old_scene):
    screen.play([Scene([DemoFrame(screen)], -1)], stop_on_resize=True, start_scene=old_scene)


last_scene = None
while True:
    try:
        Screen.wrapper(demo, catch_interrupt=False, arguments=[last_scene])
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene