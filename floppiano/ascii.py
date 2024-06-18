from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.effects import Effect, Cycle
from asciimatics.renderers import Renderer, FigletText, Box, StaticRenderer
from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import NextScene
from asciimatics.constants import ASCII_LINE, SINGLE_LINE
from enum import Enum

DEFAULT_FONT = "3x5"
DEFAULT_BACKGROUND_COLOR = Screen.COLOUR_BLACK
DEFAULT_FOREGROUND_COLOR = Screen.COLOUR_DEFAULT
DEFAULT_BORDER_COLOR = Screen.COLOUR_DEFAULT
DEFAULT_SELECTION_COLOR = Screen.COLOUR_RED

SELECT_KEY = Screen.KEY_INSERT
NEXT_FOCUS_KEY = Screen.KEY_RIGHT
PREVIOUS_FOCUS_KEY = Screen.KEY_LEFT
NEXT_PAGE_KEY = Screen.KEY_DOWN
PREVIOUS_PAGE_KEY = Screen.KEY_UP

def print_lines(screen:Screen, lines:str, x:int=0, y:int=0, **kwargs):
    """_summary_
        A convenience method for printing many lines using Screen.print()
        by iterating through the lines and incrementing the y position.
        **kwargs passes kwargs to Screen.print_at() 
    Args:
        screen (Screen): The screen to use for printing
        lines (str): The lines to print.
        x (int, optional): x location to print at. Defaults to 0.
        y (int, optional): y location to print at. Defaults to 0.
    """
    y_pos = y
    for line in lines:
        screen.print_at(line, x, y_pos,**kwargs)
        y_pos +=1

class Border(Enum):
    NONE = None
    ASCII = ASCII_LINE
    SINGLE = SINGLE_LINE

class Widget(Effect):
    
    def __init__(
        self, 
        content:Renderer, 
        x:int = 0, 
        y:int = 0, 
        border:Border=Border.NONE,
        border_color:int = DEFAULT_BORDER_COLOR,
        foreground_color:int = DEFAULT_FOREGROUND_COLOR,
        background_color:int = DEFAULT_BACKGROUND_COLOR,
        **kwargs
        ):

        """ Widget (Inherits from Effect)
                A simple UI element that belongs to a Page.
                WARNING: Will not be drawn unless added to a Page
                Use asciimatics colors, for color arguments
        Args:
            content (Renderer): A render that puts lines into the Widget
            x (int): The x position of the widget. Default is 0
            y (int): The y position of the widget. Default is 0
            border (Border): The border around the Widget. Default is Border.NONE
            border_color (int): The color of the border. Default is DEFAULT_BORDER_COLOR
            foreground_color (int): The color of the render's lines. Default is DEFAULT_FOREGROUND_COLOR
            background_color (int): The color of the background of the Widget
        """

        super().__init__(None, **kwargs)

        self._content = content
        self._border = border
        self._needs_redraw = False

        self._bounding_box = Box(
            self._content.max_width+2,
            self._content.max_height+1,
            self._border.value
        )

        self._x = x
        self._y = y
               
        self._border_color = border_color
        self._foreground_color = foreground_color 
        self._background_color = background_color

    def _update(self, frame_no):

        #If the screen is none this widget has not been added to a Frame
        #   don't attempt to draw
        screen:Screen = self._screen        
        if screen is None: return  

        #if something about the widget has changed such that we need to redraw
        # do it
        if self._needs_redraw: 
            screen.clear()
            self._needs_redraw = False

        #offsets for the content if inside a border
        x_offset = 0
        y_offset = 0

        #Draw the border if we have one
        if self._border is not Border.NONE:
            border_lines, _ = self._bounding_box.rendered_text            
            print_lines(
                screen,
                border_lines,
                self._x,self._y,
                colour=self._border_color,
                bg = self._background_color)

            x_offset += 1
            y_offset += 1
         
        #Draw the content
        content_lines, _ = self._content.rendered_text
        print_lines(
            screen,
            content_lines,
            self._x+x_offset,
            self._y+y_offset,
            colour = self._foreground_color,
            bg=self._background_color)

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value:Renderer):
        self._content = value
        #update the bounding box by invoking the border setter 
        # this also requests a redraw
        self.border = self._border

    @property
    def border(self):
        return self._border

    @border.setter
    def border(self, value:Border):
        self._border = value
        self._bounding_box = Box(
                self.content.max_width+2, 
                self.content.max_height+1,
                self._border.value)
        self._needs_redraw = True

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value:int):
        self._x = value
        self._needs_redraw = True

    @property
    def y(self):
        return self._y

    @x.setter
    def y(self, value:int):
        self._y = value
        self._needs_redraw = True
    
    @property
    def border_color(self):
        return self._border_color
    
    @border_color.setter
    def border_color(self, value:int):
        self._border_color = value
        #self._needs_redraw = True

    @property
    def foreground_color(self):
        return self._foreground_color
    
    @foreground_color.setter
    def foreground_color(self, value:int):
        self._foreground_color = value
        #self._needs_redraw = True
    
    @property
    def background_color(self):
        return self._background_color
    
    @background_color.setter
    def background_color(self, value:int):
        self._background_color = value
        #self._needs_redraw = True

    # Decided we didn't need  the below
    # def max_height(self)->int:
    #     if self._border is not Border.NONE:
    #         return self._bounding_box.max_height
    #     return self.content.max_height
    
    # def max_width(self)->int:
    #     if self._border is not Border.NONE:
    #         return self._bounding_box.max_width
    #     return self.content.max_width


    #Below are forced inherited from Effect, but we don't need them
    def reset(self):pass
    def stop_frame(self):return 0

class Label(Widget):
    def __init__(self, text:str, font:str=DEFAULT_FONT, **kwargs):
        """ Label (Inherits from Widget)
                A simple text label to display
                A label can not be selected
        Args:
            text (str): The text the label should have.
            font (str, optional): The FIGlet font to use. Defaults to DEFAULT_FONT.
        """

        self._text = text
        self._font = font              
        super().__init__(FigletText(self._text,self._font), **kwargs)
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, value:str):
        self._text = value
        #update the border via super() content setter
        self.content = FigletText(self._text,self._font)

    @property
    def font(self):
        return self._font
    
    @font.setter
    def font(self, value:str):
        self._font = value
        #update the border via super() content setter
        self.content = FigletText(self._text,self._font)

class Button(Label):    
    def __init__(
        self,
        text:str, 
        on_click = None, 
        args = None,
        **kwargs):

        """ Button (Inherits from Label)
                A simple button that can be clicked.
                A Button can be selected
        Args:
            text (str): The text the Button should have.
            on_click (any): The callback function for when the button is clicked. Default is None
            args (any): The arguments to pass to the callback function. Default is None
        """

        super().__init__(text, **kwargs)

        self.focused:bool = False
        self._on_click = on_click
        self._args = args
    
    def _update(self, frame_no):
        #Just change the background color if this Button is focused
        if(self.focused):
            self.background_color = DEFAULT_SELECTION_COLOR
        else:
            self.background_color = DEFAULT_BACKGROUND_COLOR

        return super()._update(frame_no)

    def process_event(self, event):        
        if event.key_code == SELECT_KEY and self._on_click:           
            self._on_click(self._args)
            return None # we precessed the event so return none

        return event # we didn't do anything so return back the event

class Page(Effect):

    def __init__(self, screen, name:str, page_group:tuple[str],widgets:list[Widget]=[], **kwargs):
        """Page (Inherits from Effect)
                A simple container for managing Widgets, and navigation key presses
                A page belongs to a page group. When the NEXT_PAGE_KEY or the PREVIOUS_PAGE_KEY ar pressed
                the Page triggers a NextScene Exception to move to the next page
        Args:
            screen (_type_): The screen to draw with.
            name (str): The name pf this Page
            page_group (tuple[str]): A tuple of strings that represent all the pages in the page group.
            widgets (list[Widget], optional): Widgets to add to the Page. Defaults to [].

        Raises:
            ValueError: If the name of the this Page is not in the Page Group
        """
        
        super().__init__(screen, **kwargs)
       
        if name not in page_group:
            raise ValueError("The page_name must be in the page_group.")
        
        self._name = name
        self._page_group = page_group 

        self._widgets:list[Widget] = []
        self._Buttons:list[Button] = []
        
        for widget in widgets:
            self.add_widget(widget)

        self._focused_button = 0 
     
    def _update(self, frame_no):
        for index, button in enumerate(self._Buttons):
            #update the focused button
            if (index == self._focused_button):                    
                button.focused = True
            else:
                button.focused = False

        #update all widgets
        for widget in self._widgets:
            widget._update(frame_no)
    
    def process_event(self, event):

        if isinstance(event, KeyboardEvent):
            if event.key_code == NEXT_FOCUS_KEY:
                #change focus forward
                self._next_focus()
                return None # we handled the event so nothing to return
            elif event.key_code == PREVIOUS_FOCUS_KEY:
                #change focus backwards
                self._previous_focus()
                return None # we handled the event so nothing to return
            elif event.key_code == NEXT_PAGE_KEY:
                #go to the next page
                self._next_page()
            elif event.key_code == PREVIOUS_PAGE_KEY:
                #go to the previous page
                self._previous_page()
            else:                
                if self._focused_button < len(self._Buttons):
                    return self._Buttons[self._focused_button].process_event(event)
            
        
        return event

    @property
    def name(self):
        return self._name

    def add_widget(self, widget:Widget):
        #update all the widgets so that they have a screen and can draw
        widget._screen = self._screen

        #If it's a button add it to the button (focus) list
        if isinstance(widget, Button):
            self._Buttons.append(widget)

        #add the widget
        self._widgets.append(widget)

    def _next_focus(self):
        if len(self._Buttons)==0: return

        self._focused_button +=1
        if self._focused_button >= len(self._Buttons):
            self._focused_button = 0
        
    def _previous_focus(self):
        if len(self._Buttons)==0: return
        
        self._focused_button -=1
        if self._focused_button < 0:
            self._focused_button = len(self._Buttons)-1

    def _next_page(self):
        this_index = self._page_group.index(self._name)
        next_index = this_index + 1

        #Wrap around if need be
        if next_index >= len(self._page_group):
            next_index = 0

        raise NextScene(self._page_group[next_index])

    def _previous_page(self):
        this_index = self._page_group.index(self._name)
        next_index = this_index -1

        #Wrap around if need be
        if next_index < 0:
            next_index = len(self._page_group)-1

           
        raise NextScene(self._page_group[next_index])

    #TODO: Uncomment when not doing the demo
    # @property
    # def safe_to_default_unhandled_input(self):
    #     #disable enter and space auto handling 
    #     #see https://asciimatics.readthedocs.io/en/stable/widgets.html?highlight=enter%20#global-key-handling
    #     return False

    #Below are forced inherited from Effect, but we don't need them
    def reset(self):pass
    def stop_frame(self):return 0
