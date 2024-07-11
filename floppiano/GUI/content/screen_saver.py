from asciimatics.screen import Screen
from asciimatics.effects import Effect
from asciimatics.exceptions import StopApplication
from asciimatics.event import KeyboardEvent

from random import randint
from operator import add

class FloppySaver(Effect):

    def __init__(self, screen, version:float):
        super().__init__(screen)
        self._image = (
            '┌───┬────┐──┌─┬─╮',
            '│   │    |  | │ │',
            '│   │    └──┘ │ │',
            '│   └─────────┘ │',
            '│ ┌───────────┐ │',
            '│ │ FlopPiano │ │',
            '│ │  Verison  │ │',
            f'│ │    {version:0.1f}    │■│',
            '└─┴───────────┴─┘'
        )
        
        self._image_width = 17
        self._image_height = 9
       
        self._last_postion = None

        #start at a random point
        self._position = self.random_position() 
        #upper left test: (1,1)
        #upper right test: (27,1) 
        #bottom right (27,12)
        # bottom left (1, 12)

        self._direction = (1,1)


    def _update(self, frame_no):
        #if frame_no %2 : return
        dice = randint(1,100)        
        next_position = self._check_collision(dice<=30)
        #self.screen.print_at(f'pos: {next_position}', 10,9,Screen.COLOUR_RED) 
        #self.screen.print_at(f'next pos: {next_position}', 10,10,Screen.COLOUR_RED) 
        #self.screen.print_at(f'frame:{frame_no}',0,0,Screen.COLOUR_RED)
        self._draw(randint(1,7))
        self._last_postion = self._position
        self._position = next_position        


    def _check_collision(self, allow_corner:bool) -> tuple[int, int]:
        next_position = tuple(map(add, self._position, self._direction))
        corner_check = self._check_corner(next_position, allow_corner)        
        if corner_check is not None: #we will hit a corner
            return corner_check
        return self._check_edges(next_position)

    def _check_corner(
            self, 
            position:tuple[int, int],
            allow_corner:bool) -> tuple[int, int]:
        c_1 = position
        c_2 = (position[0] + self._image_width, position[1])
        c_3 = (c_2[0], position[1] + self._image_height)
        c_4 = (position[0], c_3[1])

        #we will hit top left
        if c_1 == (0,0): 
            if allow_corner: return position
            return self.random_position()

        #we will hit top right    
        if c_2 == (self.screen.width, 0):            
            if allow_corner: return position
            return (position[0]-2, 0)

        #we will hit bottom right
        if c_3 == (self.screen.width, self.screen.height):             
            if allow_corner: return position
            return self.random_position()

        # we will hit bottom left
        if c_4 == (0, self.screen.height):            
            if allow_corner: return position
            return self.random_position()

        return None
    
    def _check_edges(self, position:tuple[int, int]) -> tuple[int, int]:
        x = position[0]
        y = position[1]

        dir_x = self._direction[0]
        dir_y = self._direction[1]

        # we will exit on the left or right edge
        if x < 0 or x + self._image_width  > self.screen.width: 
            #Flip the x dir
            dir_x = -1 * dir_x 

        # we will exit top or bottom
        if y < 0 or y + self._image_height > self.screen.height: 
            #Flip the y dir
            dir_y = -1 * dir_y

        # we will not go out of bounds
        if dir_x == self._direction[0] and dir_y == self._direction[1]:            
            return position
     
        # we will go out of bounds at a corner
        if dir_x != self._direction[0] and dir_y != self._direction[1]:
            self._direction = (dir_x, dir_y)            
            return tuple(map(add, self._position, self._direction))
            
        #if we got her then dir_x XOR dir_y flipped
        #randomly flip the other direction
        if dir_x != self._direction[0]:
            dir_y = -1*dir_y if randint(0,1) else dir_y
        
        if dir_y != self._direction[1]:
            dir_x = -1*dir_x if randint(0,1) else dir_x
            
        self._direction = (dir_x, dir_y)            
        return tuple(map(add, self._position, self._direction))

    def random_position(self) -> tuple[int, int]:
        return (
            randint(0, self.screen.width - self._image_width),
            randint(0, self.screen.height - self._image_height)
        ) 

    def _draw(self, color:int):
        #clear the last draw
        self._clear()

        #draw the new position
        y = self._position[1]
        for line in self._image:
            self.screen.print_at(
                line,
                self._position[0],
                y,
                colour=color,
                transparent=True)
            y+=1
    
    def _clear(self):
        #clear the last draw
        if self._last_postion is not None:
            y = self._last_postion[1]
            for line in self._image: 
                self.screen.print_at(
                    line,
                    self._last_postion[0], 
                    y,
                    colour=Screen.COLOUR_BLACK)
                y+=1
        
    def process_event(self, event):
        ## Any event should trigger the stop of the screen saver
        if isinstance(event, KeyboardEvent):
            #self._had_input = True
            raise StopApplication("Key pressed")

    def reset(self):
        pass
    
    def stop_frame(self):
        return 0
    