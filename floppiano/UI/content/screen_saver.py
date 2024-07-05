from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.effects import Effect
from asciimatics.exceptions import StopApplication
from asciimatics.event import KeyboardEvent

from threading import Thread, Event
import time

class FloppySaver(Effect):

    def __init__(self, screen):
        super().__init__(screen)

    def _update(self, frame_no):
        screen:Screen = self.screen
        screen.print_at(frame_no,0,0,Screen.COLOUR_RED)
    
    def process_event(self, event):
        ## Any event should trigger the stop of the screen saver
        if isinstance(event, KeyboardEvent):
            #self._had_input = True
            raise StopApplication("Key pressed")

    def reset(self):
        pass
    
    def stop_frame(self):
        return 0


def screen_saver(screen:Screen):
    return [Scene([FloppySaver(screen)],-1,clear=True)]
    #screen.play([Scene([FloppySaver(screen)],-1,clear=True)])




# class SaverService(Thread):

#     def __init__(self):
#         Thread.__init__(self)
 
#         self._stop_event = Event()       


#     def run(self):

#         screen = Screen.open(catch_interrupt=True)
#         screen.set_scenes([Scene([FloppySaver(screen)], -1, clear=True)])

#         #do this until stop flag is set or until the the scene exits
#         last_time = time.time()
#         while not self._stop_event.is_set():
#             if time.time() - last_time >= 1:
#                 try:
#                     screen.draw_next_frame()
#                     last_time = time.time()
#                 except StopApplication: break

#         screen.clear()
#         screen.close()

#     def quit(self):
#         """_summary_
#             Stop the Service Thread
#         """
#         self._stop_event.set()
