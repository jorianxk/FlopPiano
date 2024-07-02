from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.effects import Effect
from asciimatics.exceptions import NextScene
from asciimatics.event import KeyboardEvent


class FloppySaver(Effect):

    def __init__(self, screen, return_scene:Scene):
        super().__init__(screen)
        self._return_scene = return_scene

    def _update(self, frame_no):
        screen:Screen = self.screen
        screen.print_at(frame_no,0,0,Screen.COLOUR_RED)
    
    def process_event(self, event):
        ## Any event should trigger a scene change back to the original seen
        if isinstance(event, KeyboardEvent):
            #self._had_input = True
            raise NextScene(self._return_scene.name)

    def reset(self):
        pass
    
    def stop_frame(self):
        return 0