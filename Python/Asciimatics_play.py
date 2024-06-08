from time import sleep
from asciimatics.screen import ManagedScreen, Screen
from asciimatics.constants import *
from asciimatics.scene import Scene
from asciimatics.effects import Cycle, Stars
from asciimatics.renderers import FigletText


def resTest(screen):    
    screen.print_at("A", 0,0, COLOUR_RED, A_BOLD)
    screen.print_at("B", 89,0, COLOUR_GREEN)
    screen.print_at("C", 0,29, COLOUR_BLUE)
    screen.print_at("D", 89,29, COLOUR_YELLOW)
    screen.refresh()
    sleep(2)

Screen.wrapper(resTest,stop_on_resize = True)



# def demo():
#     with ManagedScreen() as screen:
#         screen.print_at("1", 0,0, COLOUR_MAGENTA)
#         screen.print_at("2", 89,0, COLOUR_CYAN)
#         screen.print_at("3", 0,29, COLOUR_DEFAULT)
#         screen.print_at("4", 89,29, COLOUR_BLACK)
#         screen.refresh()
#         sleep(2)
# demo()
