from asciimatics.widgets import DropdownList, TextBox
import logging

class DropDown(DropdownList):
    def __init__(self, options, start_option=None ,**kwargs):
        super().__init__(options, **kwargs)

        self._old_value = None

        if start_option is not None:
            for index, option in enumerate(self.options):
                if option[0]==start_option:break
            else:
                raise ValueError("start_option not in options")

            self._line = index
            self._value = option[1]  

    def revert(self):
        for i, [_, value] in enumerate(self._options):
            if value == self._old_value:
                self._line = i
                self._value = self._old_value
                break

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