from asciimatics.widgets import Frame, DropdownList, TextBox
from asciimatics.widgets.utilities import _enforce_width
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen
from wcwidth import wcswidth
import logging


class DynamicFrame(Frame):
    """
        overridden to add on_update
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
        if self._on_update:
            self._on_update()
        return super()._update(frame_no)




class DropDown(DropdownList):
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

    # def revert(self):
    #     for i, [_, value] in enumerate(self._options):
    #         if value == self._old_value:
    #             self._line = i
    #             self._value = self._old_value
    #             break


    def update(self, frame_no):
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
        return [(name, index) for  index, name in enumerate(items)]

class LoggerText(TextBox, logging.StreamHandler):

    def __init__(self, height, history_length:int = 100, label=None, name=None,  **kwargs):
        TextBox.__init__(self,height, label, name, as_string=False, line_wrap=True, parser=None, on_change=None, readonly=True, **kwargs)
        logging.StreamHandler.__init__(self)

        self._logged_lines = []
        self._history_length = history_length
       

    def emit(self, record):
        if len(self._logged_lines) >=self._history_length:
            self._logged_lines = []
        
        #TODO format this
        self._logged_lines.append(f'{record.getMessage()}')
        self.value = self._logged_lines
        self.reset()


    def update(self, frame_no):
        try:
            super().update(frame_no)
        except AttributeError as ae:
            pass
            # raise AppException("LoggerText got AttributeError on update()") from ae



