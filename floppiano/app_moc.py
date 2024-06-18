"""
------------------------------ FlopPiano Alpha Mockup-------------------------------------

Best if used in CLI with 90 columns and 30 lines (The backup camera's CLI resolution)

This is a demonstration of a FIGlet UI tools that I built on top of asciimatics.
I don't think we can use the in built UI from asciimatics because it uses single
characters for text. Since, we're using a tiny screen, text that is only a single
character in height is very hard to read. Therefore, we must use a bigger "font". Thats
where FIGlet text come into play. It generates larger ASCII based renditions of text! So,
I built a simple/sloppy python module that mimics behavior of an event based UI with two
simple "Widgets". 

A Widget is really just a wrapper around FIGlet text, but they offer a little more 
functionality and are UI fields. There are two types of Widgets; Labels and Buttons. 
-- A label is a simple non-user-editable text field that can not be given focus. A label 
is used to display information.
-- A button is a focus-able, click-able field that performs an programmable action (using 
callbacks).

All Widgets are housed in a Page (which is analogous to a Frame) The page handles the 
Widgets, input focusing and orchestrations.
                                                                        - Jorian
                               Keyboard controls:
                               
            [ENTER] or [SPACE] -> Sequence break. Just skip to the next Scene

[UP]     -> Next Page                 [RIGHT]  -> Next Button
[DOWN]   -> Previous Page             [LEFT]   -> Previous Button
[INSERT] -> Click/ Press buttons      [ctrl+C] -> Exit
"""


from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError
from asciimatics.effects import Print, Mirage, Matrix, Wipe
from asciimatics.renderers import Fire
from ascii import *
   

class KeyboardPage(Page):
    def __init__(self, screen, name: str, page_group: tuple[str], **kwargs):
        super().__init__(screen, name, page_group)

        label = Label("Keyboard", font="ansi_shadow", x=13, y=0)
        self.add_widget(label)
        
        crashModeHeader = Label(
            "Crash",
            font = "small",
            x=0,
            y=6,
            border = Border.ASCII
        )
        self.add_widget(crashModeHeader)

        ##Vertical separators
        for i in range(0,3):
            separator = Label(
                " ",
                font ="small",
                x = 24,
                y = 6 + 7* i,
                border = Border.ASCII 
            )
            self.add_widget(separator)

        pitchModeHeader = Label(
            "PitchBend Range",
            font = "small",
            x=26,
            y=6,
            border = Border.ASCII
        )
        self.add_widget(pitchModeHeader)       

        crashButtons = []
        off = Button("OFF",  x=9, y=14, font="mini", on_click=self.buttonClick, foreground_color = Screen.COLOUR_GREEN)
        off._args = (crashButtons, off)
        crashButtons.append(off)
        bow = Button("BOW",  x=7, y=18, font="mini", on_click=self.buttonClick)
        bow._args = (crashButtons, bow)
        crashButtons.append(bow)
        flip = Button("FLIP", x=8, y=22, font="mini", on_click=self.buttonClick)
        flip._args = (crashButtons, flip)
        crashButtons.append(flip)
        for button in crashButtons: self.add_widget(button)

        pitchButtons = []
        half = Button("HALF",   x=32, y=14, font="mini", on_click=self.buttonClick, foreground_color = Screen.COLOUR_GREEN)
        half._args = (pitchButtons, half)
        pitchButtons.append(half)  
        whole = Button("WHOLE",  x=30, y=18, font="mini", on_click=self.buttonClick)
        whole._args = (pitchButtons, whole)
        pitchButtons.append(whole)
        minor3 = Button("MINOR3", x=29, y=22, font="mini", on_click=self.buttonClick)
        minor3._args = (pitchButtons, minor3)
        pitchButtons.append(minor3) 
        major3 = Button("MAJOR3", x=51, y=14, font="mini", on_click=self.buttonClick)
        major3._args = (pitchButtons, major3)
        pitchButtons.append(major3)
        fourth = Button("FOURTH", x=53, y=18, font="mini", on_click=self.buttonClick)
        fourth._args = (pitchButtons, fourth)
        pitchButtons.append(fourth)
        fifth = Button("FIFTH",  x=55, y=22, font="mini", on_click=self.buttonClick)
        fifth._args = (pitchButtons, fifth)
        pitchButtons.append(fifth)  
        octave = Button("OCTAVE", x=73, y=14, font="mini", on_click=self.buttonClick)
        octave._args = (pitchButtons, octave)
        pitchButtons.append(octave)  
        for button in pitchButtons: self.add_widget(button)
    
    def buttonClick(self, args):
        all_buttons = args[0]
        clicked_button:Button = args[1]

        for button in all_buttons:
            button.foreground_color = Screen.COLOUR_DEFAULT
        
        clicked_button.foreground_color = Screen.COLOUR_GREEN

class MIDIPage(Page):
    def __init__(self, screen, name: str, page_group: tuple[str], **kwargs):
        super().__init__(screen, name, page_group)

        label = Label("MIDI Player", font="ansi_shadow", x=6, y=0)
        self.add_widget(label)

        midi_text = Label(
            "We add stuff here for\nPlaying MIDI Files",
            font = "small",
            x=1,
            y=8,
            border =Border.SINGLE,
            border_color = Screen.COLOUR_YELLOW,
            background_color = Screen.COLOUR_WHITE,
            foreground_color = Screen.COLOUR_BLUE        
        )

        self.add_widget(midi_text)    

        self.add_widget(Button("Play", x=30, y=20, font="mini", border = Border.SINGLE))
        self.add_widget(Button("Stop", x=50, y=20, font="mini", border = Border.SINGLE))

class SettingsPage(Page):
    def __init__(self, screen, name: str, page_group: tuple[str], **kwargs):
        super().__init__(screen, name, page_group)

        label = Label("Settings", font="ansi_shadow", x=14, y=0)
        self.add_widget(label)

        settings_text = Label(
            "We add stuff here for\nchanging the MIDI out\nMode/In & Out Chan.",
            font = "small",
            x=1,
            y=8,
            border =Border.SINGLE,
            border_color = Screen.COLOUR_YELLOW,
            background_color = Screen.COLOUR_WHITE,
            foreground_color = Screen.COLOUR_BLUE        
        )

        self.add_widget(settings_text)        

class AboutPage(Page):

    def __init__(self, screen, name: str, page_group: tuple[str], **kwargs):
        super().__init__(screen, name, page_group)
 
        label = Label("About", font="ansi_shadow", x=25, y=0)
        self.add_widget(label)

        about_us = Label(
            "We add stuff here\nabout us and the\nFlopPiano",
            font = "small",
            x=9,
            y=8,
            border =Border.SINGLE,
            border_color = Screen.COLOUR_GREEN,
            foreground_color = Screen.COLOUR_MAGENTA            
        )

        self.add_widget(about_us)



#A Simple introduction/ info page
def getIntroScene(screen:Screen)->Scene:
    intro_text = None
    with open("assets/intro_text.txt","r") as file:
        intro_text = file.read()

    introScene = Scene([],duration=3600)

    infoText = Print(
        screen,
        StaticRenderer([intro_text]),
        0,
        speed = 1,
        colour=Screen.COLOUR_DEFAULT
        )

    introScene.add_effect(infoText)

    return introScene   

#A simple legend that shows the user the keyboard controls
def getKeyMapLegend(screen:Screen)->Effect:
    controls_text = None
    with open("assets/controls.txt","r") as file:
        controls_text = file.read()

    keyMapLegend = Print(screen,
        StaticRenderer([controls_text]),
        27,
        speed=1,
        colour=Screen.COLOUR_DEFAULT)
    
    return keyMapLegend

#Return all application Scenes in a list
def getAppScenes(screen:Screen)->list[Scene]:
    appScenes = []

    page_group = ("Keyboard", "MIDI" ,"Settings","About",)
    
    pages = [
        KeyboardPage(screen, "Keyboard", page_group),
        MIDIPage(screen, "MIDI", page_group),
        SettingsPage(screen, "Settings", page_group),
        AboutPage(screen, "About", page_group)
    ]
    
    keyMapLegend = getKeyMapLegend(screen)

    for page in pages:
        appScenes.append(Scene([page, keyMapLegend],-1,name=page.name))
    
    return appScenes

#Return our splash screens in a list
def getSplashScenes(screen:Scene)->list[Scene]:
    jacob_placeholder = None
    jorian_splashscreen = None
    with open("assets/jacob_placeholder.txt","r") as file:
        jacob_placeholder = file.read()
    with open("assets/jxk_logo.txt","r") as file:
        jorian_splashscreen = file.read()

    splashScenes =[]

    # Jacobs Splash Screen
    splashScenes.append(Scene(
        [
            Print(screen,
              Fire(screen.height, screen.width, "*"*screen.width,0.5, 50, screen.colours),
              0,
              speed=1,
              transparent=False, stop_frame = 110),    

            Print(screen,
              StaticRenderer([jacob_placeholder]),
              4,
              speed = 1,
              colour=Screen.COLOUR_RED, stop_frame=110),

            Wipe(screen, bg=Screen.COLOUR_BLACK, start_frame = 100)
        ]
        ,180))
    
    #Jorian's Splash Screen
    splashScenes.append(Scene(
        [
            Matrix(screen,start_frame = 90, stop_frame=225),

            Mirage(screen,
              StaticRenderer([jorian_splashscreen]),
              0,
              colour=Screen.COLOUR_GREEN, stop_frame = 90),
        ]
        ,250))
    
    return splashScenes

def demo(screen:Screen, lastScene:Scene):
    scenes = []
    #Get the Introduction/Info Screen
    scenes.append(getIntroScene(screen))
    #Get the Splash Screens/Scenes
    scenes.extend(getSplashScenes(screen))
    #Ge the actual application Scenes
    scenes.extend(getAppScenes(screen))

    #Start playing the Scenes
    screen.play(scenes, stop_on_resize=True,start_scene=lastScene, allow_int=True)



if __name__ == "__main__":
    lastScene = None
    while True:
        try:
            Screen.wrapper(demo, catch_interrupt=False, arguments=[lastScene])
            exit(0)
        except KeyboardInterrupt as ke:
            print("Exiting...")
            break
        except ResizeScreenError as e:
            lastScene = e.scene

    print("Done.")
