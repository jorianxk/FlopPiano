from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.effects import Effect
from asciimatics.widgets import DropdownList, TextBox
from asciimatics.widgets.utilities import THEMES
from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import NextScene


from .app import App

import logging


#TODO update docstrings for Tab and TabHeader for App() changes

class TabHeader(Effect):
    
    def __init__(
            self, 
            screen:Screen, 
            tab_name:str, 
            tab_row:list[str], 
            divider_row:list[str],
            theme = 'default'):
        super().__init__(screen)
        """_summary_
            An effect that will be drawn at the top of each Tab that shows the
            The active tab and other tabs in the TabGroup
        Args:
            screen (Screen): The Screen that the The TabHeader will be drawn 
                with
            tab_name (str): The name of the tab that the TabHeader will belong 
                to
            tab_row (list[str]): The first row of text that will be drawn (i.e. 
                the Tab names with decorators)
            divider_row (list[str]): The second row of text that will be drawn
                (i.e the tab dividers)
            theme (optional): The ascii theme to use on the TabHeader
        """

        # An asciimatics theme
        # self._theme = None
        self.theme = theme
        
        self._tab_name = tab_name
        self._tab_row = tab_row
        self._divider_row =divider_row

    def _update(self, frame_no):
        """_summary_
            Overridden from effect, draws the TabHeader
        Args:
            frame_no (int): The frame number (not used)
        """
        # Convenience variable for pylance type hinting
        screen:Screen = self.screen

        # Draw the first row
        x = 0 #Location to draw at
        for tab_label in self._tab_row:
            #Get the color, attribute, and background color for drawing
            pallet = self.palette['borders']

            # If the tab name is the selected tab's name highlight it
            if tab_label.strip() == self._tab_name:
                pallet = self.palette['label']
            # Draw
            screen.print_at(tab_label, x, 0, pallet[0], pallet[1], pallet[2])
            
            # Increment the position
            x += len(tab_label)

        #Draw the second row
        x = 0
        for divider_label in self._divider_row:
            #All dividers are disabled colored
            pallet = self.palette['borders']
            screen.print_at(
                divider_label, 
                x, 
                1, 
                pallet[0], pallet[1], pallet[2])
            x += len(divider_label)

    @property
    def theme(self):
        return self._theme

    @theme.setter
    def theme(self, theme):
        """
        Shamelessly stolen from asciimatics to support theming

        Pick a palette from the list of supported THEMES.

        :param theme: The name of the theme to set.
        """
        if theme in THEMES:
            self._theme = theme
            self.palette = THEMES[theme]
    
    @property
    def height(self) -> int:
        """_summary_
            The height of the TabHeader
        Returns:
            int: The height of the TabHeader
        """       
        return 2
    
    @property
    def width(self) ->int:
        """_summary_
            The width of the TabHeader
        Returns:
            int: The width of the TabHeader
        """
        return self.screen.width

    #We have to override these 
    def reset(self):return 
    def stop_frame(self):return 0

class Tab(Scene):
    # Constants for switching tabs
    NEXT_TAB_KEY = Screen.KEY_PAGE_UP
    PRIOR_TAB_KEY = Screen.KEY_PAGE_DOWN
    def __init__(self, screen:Screen, name:str, theme = 'default'):    
        Scene.__init__(
            self,
            effects=[], 
            duration=-1, 
            clear=True,
            name=name)        
        """_summary_
            A Tab is a Scene in a set of Scenes (TabGroup) with a a single
             default effect the TabHeader. A Tab is a Scene so that it may 
             render many effects (like Frames and animations). Best used in a 
             TabGroup 
        Args:
            screen (Screen): The Screen that the The Tab will be drawn with
            name (str): The unique name of the Tab
        """
        self.app = None
        self.screen = screen
        self.theme = theme

        # The previous tab in the TabGroup - used for going to the prior Tab
        self.prior_tab_name = None
        # The next tab in the TabGroup - used for going to the next Tab
        self.next_tab_name = None
    
    def process_event(self, event):
        """_summary_
            Overridden from Scene to handle moving other Tabs in the TabGroup.
        """
        #Only be sensitive to keyboard events
        if isinstance(event, KeyboardEvent):

            if event.key_code == Tab.PRIOR_TAB_KEY: #Go to the prior Tab
                raise NextScene(self.prior_tab_name)
            elif event.key_code == Tab.NEXT_TAB_KEY: #Go to the next Tab
                raise NextScene(self.next_tab_name)
            else: # Do nothing
                pass
        
        # It is very important that we call the super().process_events because
        # otherwise all the effects in the Tab would not get keyboard and mouse
        # events
        return super().process_event(event)
    
    # def useable_height(self) -> int:
    #     """_summary_
    #         The usable height of the Tab
    #     Returns:
    #         int: The Screen's height - The height of the TabHeader
    #     """
    #     return self.screen.height - self._tab_header.height

    @property
    def theme(self):
        return self._theme

    @theme.setter
    def theme(self, theme):
        """
        Shamelessly stolen from asciimatics to support theming

        Pick a palette from the list of supported THEMES.

        :param theme: The name of the theme to set.
        """
        if theme in THEMES:
            self._theme = theme
            self.palette = THEMES[theme]


    def fix(self, app:App, tab_header:TabHeader, prior_tab_name:str, next_tab_name:str):
        """_summary_
            Called by TabGroup to setup the Tab's TabHeader and event handling
        Args:s
            tab_header (TabHeader): The TabHeader to be used with the Tab
            prior_tab_name (str): The name of the previous Tab in the TabGroup
            next_tab_name (str): The name of the next Tab in the TabGroup
        """
        self.app = app
        self.prior_tab_name = prior_tab_name
        self.next_tab_name = next_tab_name
        self._tab_header = tab_header
        self._tab_header.theme = self.theme
        # Make sure the TabHeader is the first effect in the Tab
        self._effects.insert(0, tab_header)

class TabGroup():
    #Constants for generating text for TabHeaders
    #Tab name decorations
    L_DEC = '┌'
    R_DEC = '┐'

    #Divider characters
    H_DIV = '─'
    L_DIV = '┘'
    R_DIV ='└'
    T_DIV = '┴'

    def __init__(self, screen, app:App, tabs:list[Tab]=[]):
        """_summary_
            A TabGroup is a collection of Tabs. When a Tab is added to the 
            TabGroup, the Tab is setup for use. That is, the TabGroup
            generates the TabHeader for the Tab and sets up event handling
        Args:
            screen (_type_): The Screen that will be used to draw the Tabs
            tabs (list[Tab], optional): A list of Tab to add upon instantiation
        """
        self.screen = screen
        self.app = app
        self._tabs:dict[str,Tab] = {}

        for tab in tabs:
            self.add_tab(tab)

    def add_tab(self, tab:Tab):
        """_summary_
            Add a Tab to the TabGroup
        Args:
            tab (Tab): The Tab to be added

        Raises:
            ValueError: If the Tab is already in the TabGroup
        """
        if tab.name in self.tab_names:
            raise ValueError("Tab already in TabGroup")
        self._tabs[tab.name] = tab

    @property
    def tab_names(self) -> list[str]:
        """_summary_
            A list of all the Tab names in the TabGroup
        Returns:
            list[str]: All Tab names in the TabGroup
        """
        return list(self._tabs.keys())
    
    @property
    def tabs(self) -> list[Tab]:
        """_summary_
            A list of all Tabs in the TabGroup
        Returns:
            list[Tab]: All Tabs in the TabGroup
        """
        return list(self._tabs.values())    

    def fix(self):
        """_summary_
            This should be called after all the Tabs have been added to the 
            TabGroup and before adding Tabs to a Scene For rendering.

            This function prepares all Tabs by adding the TabHeader to each
            tab and setting up event handling for tab switching.
        """

        # A dict that will contain the name of each tab(key) and it's tab header
        # (value) in the TabGroup
        headers:dict[str, Effect] = {}
        
        # First we need to 'group' the Tabs into groups that will fit onto the
        # Screen
        groups = TabGroup._group(self.tab_names, self.screen)

        # Then we generate a TabHeader for each Tab in group and append them to 
        # the header dictionary
        for group in groups:
            headers.update(TabGroup._gen_headers(group,self.screen))
        
        # Finally we setup each Tab by giving it it's TabHeader and telling it
        # it's neighboring tabs via the Tab.fix() function
        for index, tab in enumerate(self.tabs):
            # We get the Tab's neighboring tabs so it knows which NextScene
            # Exception to through when switching tabs
            next = index + 1
            if (next > len(self.tabs)-1): next = 0
            prior = index -1
            if (prior < 0): prior = len(self.tabs)-1

            next_tab_name = self.tabs[next].name
            prior_tab_name = self.tabs[prior].name  

            #Give the Tab it's header and neighboring tab names
            tab.fix(self.app, headers[tab.name], prior_tab_name, next_tab_name)
    
    @staticmethod
    def _group(tab_names:list[str], screen)->list[list[str]]:
        """_summary_
            This function groups all the Tabs into groups that will 
            render in one line on the screen. Used to 'bank' tabs for tab
            cycling
        Args:
            tab_names (list[str]): The list of all Tab names in the TabGroup
            screen (_type_): The screen the Tabs will be drawn with. (used for
             it's width property)

        Raises:
            ValueError: If a singular Tab name is too long for the screen

        Returns:
            list[list[str]]: A list of groups(which is a list of tab names)
        """

        all_groups = []  # The list we intend to return
        unused_names = tab_names # The list of Tab names to use
        #The set of Tab names used in a prior iteration of the loop
        last_loop_names = None

        #Loop until we have used up all the tab names
        while len(unused_names) > 0:
            # This means we did not use any names from the unused names list.
            # Which should only happen if a Tab name was too long to fit on the 
            # screen.
            if last_loop_names == unused_names: 
                raise ValueError(
                    f'{unused_names[0]} is too wide for the screen')
            # A list to test the width of the tab group
            test_group = []
            # The actual group of tab names
            group = []

            #Try to use each name in the unused names
            for tab_name in unused_names:
                # Put the Tab name + the decorations that will be used 
                # in the test group
                test_group.append(f'{TabGroup.L_DEC} {tab_name} {TabGroup.R_DEC}')

                # If the test group is too wide for the screen break so we can
                # create a new group
                if TabGroup._row_width(test_group) > screen.width:
                    break
                else:
                    #Add the Tab name to the group
                    group.append(tab_name)
            
            #Update the too-long-for-screen check
            last_loop_names = list(unused_names)

            #Remove all the used names from the unused names
            for name in group: unused_names.remove(name)

            #Add the group to the groups list        
            all_groups.append(group)

        return all_groups
    
    @staticmethod
    def _gen_headers(tab_names:list[str], screen) -> dict[str, TabHeader]:
        """_summary_
            Used to generate all the TabHeaders fore each tab in the TabGroup
        Args:
            tab_names (list[str]): The list of Tab names in the Tab group
            screen (_type_): The screen the tab will be drawn with

        Returns:
            dict[str, TabHeader]: A dict where the key is the Tab name and the 
                key is the TabHeader that should be used with that Tab
        """
        headers = {} #The dict we intent to return


        for tab_name in tab_names:
            # The first row of text in the TabHeader ex:
            #┌ Sound ┐┌ Settings ┐┌ MIDI Player ┐┌ About ┐
            names_row = []
            
            #The second row of text in the TabHeader ex:
            #┘       └┴──────────┴┴─────────────┴┴───────┴
            dividers_row = []
            #Both rows together:
            #┌ Sound ┐┌ Settings ┐┌ MIDI Player ┐┌ About ┐
            #┘       └┴──────────┴┴─────────────┴┴───────┴

            for label_text in tab_names:
                if label_text == tab_name:
                    # If the current Tab name is selected, we want the name to 
                    # be separated from the decorators so it can be highlighted
                    # when drawn 
                    names_row.append(TabGroup.L_DEC)
                    names_row.append(f' {label_text} ')# We add spaces here
                    names_row.append(TabGroup.R_DEC)

                    # There should not be a divider under the selected tab, so 
                    # pad the space with empty (space) characters
                    dividers_row.append(TabGroup.L_DIV)
                    dividers_row.append(' ' * (len(label_text)+2))# +2-spaces
                    dividers_row.append(TabGroup.R_DIV)                    
                else:

                    # The tab is not selected 
                    names_row.append(
                        f'{TabGroup.L_DEC} {label_text} {TabGroup.R_DEC}'
                    ) 
                    # Add the divider under the tab name
                    dividers_row.append(
                        f'{TabGroup.T_DIV}'
                        f'{TabGroup.H_DIV.ljust(len(label_text)+2, TabGroup.H_DIV)}'
                        f'{TabGroup.T_DIV}'                        
                    )


            # We may need to add padding if the Tabs didn't take up the whole
            # Screen
            row_width = TabGroup._row_width(dividers_row)
            if row_width < screen.width:
                # amount of padding to add
                spaces_to_add = screen.width - row_width 
                # Just add space padding
                names_row.append(' '.ljust(spaces_to_add))
                
                #Add the dividing character for padding on the second row
                dividers_row.append(
                    TabGroup.H_DIV.ljust(spaces_to_add,TabGroup.H_DIV))

            #Update the headers with a tab header using the first and second row
            headers[tab_name] = TabHeader(
                screen,
                tab_name,
                names_row,
                dividers_row)
        
        return headers

    @staticmethod
    def _row_width(row:list[str]) -> int:
        """_summary_
            Returns the width (length) of each string the row summed 
        Args:
            row (list[str]): The list of strings to sum the lengths of

        Returns:
            int: The combined length of all the strings in the list
        """
        length = 0
        for text in row:
            length += len(text)
        return length

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
            self._value = start_option

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
        self._logged_lines.append(f'{record.name}, [{record.levelname}], {record.getMessage()}')
        self.value = self._logged_lines
        self.reset()

