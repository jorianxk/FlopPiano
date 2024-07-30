from asciimatics.widgets import (
    Widget, Frame, DropdownList, Text , Layout, Label)
from asciimatics.widgets.utilities import _enforce_width
from wcwidth import wcswidth
import textwrap

"""
    A collection of custom (and sloppy) asciimatics widgets.
"""

class DynamicFrame(Frame):
    """
        Essentially a standard asciimatics Frame but overridden to add 
        an on_update() callback that is called when the Frame will be rendered.
        This allows for a more responsive event-driven UI
    """
    def __init__(self, screen, height, width, data=None, on_load=None, 
            has_border=True, hover_focus=False, name=None, title=None, 
            x=None, y=None, has_shadow=False, reduce_cpu=False, is_modal=False, 
            can_scroll=True, on_update=None):
        
        super().__init__(screen, height, width, data, on_load, has_border, 
            hover_focus, name, title, x, y, has_shadow, reduce_cpu, is_modal, 
            can_scroll)
        
        self._on_update = on_update
        
    def _update(self, frame_no):
        # If we have an on_update call back call it
        if self._on_update is not None:
            self._on_update()
        return super()._update(frame_no)

class DropDown(DropdownList):
    """
        Essentially an asciimatics DropDownList but modified to accept a 
        starting index to specify which element in the list should be displayed
        on startup. 
    """
    def __init__(self, options, start_index=None ,**kwargs):
        super().__init__(options, **kwargs)

        self._old_value = None

        if start_index is not None:
            for index, option in enumerate(self.options):
                if option[1]==start_index:break
            else:
                raise ValueError("start_option not in options")

            self._line = index
            self._value = option[1]  

    def update(self, frame_no):
        # Copied and slightly modified from standard asciimatics
        self._draw_label()

        # This widget only ever needs display the current selection - the separate Frame does all
        # the clever stuff when it has the focus.
        text = "" if self._line is None else self._options[self._line][0]
        (colour, attr, background) = self._pick_colours("field", selected=self._has_focus)
        if self._fit:
            width = min(max(map(lambda x: wcswidth(x[0]), self._options)) + 1, self.width - 3)
        else:
            width = self.width - 3

        # For unicode output, we need to adjust for any double width characters.
        output = _enforce_width(text, width, self._frame.canvas.unicode_aware)
        output_tweak = wcswidth(output) - len(output)

        self._frame.canvas.print_at(
            f"  {output:{width - output_tweak}} ",
            self._x + self._offset,
            self._y,
            colour, attr, background)

    @DropdownList.value.setter
    def value(self, new_value):
        # Only trigger change notification after we've changed selection
        old_value = self._value
        self._value = new_value
        for i, [_, value] in enumerate(self._options):
            if value == new_value:
                self._line = i
                break
        else:
            #Overridden to comment out the below
            #self._value = self._line = None
            return #Do nothing

        if old_value != self._value and self._on_change:
            self._old_value = old_value
            self._on_change()
    
    @staticmethod
    def list2options(items:list[str]) -> tuple[str, int]:
        """
            A helper method to convert a standard list to a form that the 
            asciimatics DropDownList wants
        Args:
            items (list[str]): The list to convert

        Returns:
            tuple[str, int]: The set of options for a DropDownList
        """
        return [(name, index) for  index, name in enumerate(items)]

class FloppieWidget(Widget):
    """
        A silly Clippie like guy (Widget) to show various text bubbles and tool-
        tips
    """

    # Image must be 45 columns X 45 lines!
    IMAGE_PATH = 'assets/floppie_widget.txt'
   
    def __init__(self, name=None, value = '', animate = True):
        super().__init__(name, False, False, None, None)

        self._image = None
        with open(FloppieWidget.IMAGE_PATH, encoding="utf8") as file:
            self._image = [line for line in file]

        self.value = value
        self.animate = animate

    def reset(self):
        pass

    def update(self, frame_no):        
        # A new reference to our frame for code auto-completion
        frame:Frame = self._frame
        
        # Get the theme colors
        (colour, attr, background) = self._pick_colours("label", selected=self._has_focus)
       
        #Draw Floppie (The Image)
        y = self._y
        for line in self._image:
            frame.canvas.print_at(
                line,
                self._x,
                y,
                colour=colour,
                bg = background,
            )
            y+=1

        #Draw the text frame ( The corners of the speech bubble)
        frame.canvas.print_at('┌', self._x+20, self._y+1, colour=colour, attr=attr, bg = background)
        frame.canvas.print_at('┐', self._x+42, self._y+1, colour=colour, attr=attr, bg = background)
        frame.canvas.print_at('└', self._x+20, self._y+6, colour=colour, attr=attr, bg = background)
        frame.canvas.print_at('┘', self._x+42, self._y+6, colour=colour, attr=attr, bg = background)

        # Draw the text/value (The text Floppie is saying)
        y = self._y + 2
        for line in self._value:
            frame.canvas.print_at(line, self._x+22, y, colour=colour, attr=attr, bg = background)
            y+=1

        #Draw the eyebrows/ overwrite Floppie's eyebrows (animated every-other frame)
        if self.animate and frame_no % 2:
            frame.canvas.print_at('^', self._x+7, self._y+1, colour=colour, attr=attr, bg = background)
            frame.canvas.print_at('^', self._x+13, self._y+1, colour=colour, attr=attr, bg = background)

    def process_event(self, event):
        # Noting to do here
        return event
    
    @property
    def value(self) -> list[str]:
        return self._value

    @value.setter
    def value(self, value:str):
        # Sets Floppie's speech text which is only 4 lines by 19 columns

        # Wrap the string into chunks of length 19
        self._value = textwrap.wrap(value, 19)

        # If we have more then four chunks
        if len(self._value) > 4:
            # Force the list only to be four chunks
            self._value = self._value[0:4]
            # The last chunk should be "..."ed to let the user know the value 
            # was shortened
            self._value[-1] = textwrap.shorten(
                self._value[-1] + "more words to make the line be shortened",
                width = 19,
                placeholder = '...')

    def required_height(self, offset, width):
        return 8

class ReadOnlyText(Text):
    """
        Just a disabled & readonly asciimatics Text widget modified to 
        render with a normal (non-disabled) color scheme 
    """
    def __init__(self,  **kwargs):        
        super().__init__(label=None, name=None, on_change=None, validator=None, 
                         hide_char=None, max_length=None, readonly=True, 
                         **kwargs)
 
    def _pick_colours(self, palette_name, selected=False):
        # overloaded to fix color
        return super()._pick_colours("edit_text")

class Setting():
    '''
        A helper class to manage the layout an behavior of a Dropdown
        representing a synth or application setting. Encapsulates a layout,
        a Dropdown and a tool-tip string. 
    '''
    def __init__(self, 
                 label_text:str, 
                 options, 
                 on_update, 
                 on_change, 
                 frame:DynamicFrame,
                 tool_tip = '') -> None:
        """
            Creates a Layout, Label, and DropDown and adds them to the specified
            frame. 
        Args:
            label_text (str): The label test to use for the Setting
            options (_type_): The options to use in the DropDown
            on_update (_type_): A callback to update the DropDown's option on 
                an update
            on_change (_type_): A callback to preform some action when the 
                DropDown's value is changed
            frame (DynamicFrame): The Frame which will house the setting
            tool_tip (str, optional): The help text for the setting. Defaults to ''.

        Raises:
            ValueError: If the specified options are not a list or a range
        """
    
        self._on_update = on_update
        self._on_change = on_change
        self.tool_tip = tool_tip

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
            start_index = None if self._on_update is None else self._on_update(), # Call the on_update once to get the start value
            on_change = self._changed,
            fit = False,
        )  
        layout.add_widget(self._dd,3)
    
    def update(self):
        if self._on_update is not None:
            self._dd.value = self._on_update()
    
    def _changed(self):
        if self._on_change is not None:
            self._on_change(self._dd.value)
    
    @property
    def value(self):
        return self._dd.value
    
    @property
    def selected(self) -> bool:
        return self._dd._has_focus