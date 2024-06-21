from asciimatics.screen import Screen
from asciimatics.widgets import Frame, Layout, Label

from tab import Tab

# text1 = "┌ Sound ┐┌ Settings ┐┌ MIDI Player ┐┌ About ┐"
# text2 = "┘       └┴──────────┴┴─────────────┴┴───────┴"

# text1 = "...┐┌ Settings ┐┌ MIDI Player ┐┌ About ┐ ┌..."
# text2 = "───┴┘          └┴─────────────┴┴───────┴─┴───"
class TabGroup():

    left_dec = '┌'
    right_dec = '┐'

    div = '─'
    left_div = '┘'
    right_div ='└'
    connect_div = '┴'

    def __init__(self, screen):
        self.screen = screen
        self._tabs:dict[str,Tab] = {}
        self._tab_headers:dict[str,Frame] = []


    def add_tab(self, tab:Tab):
        if tab.name in self.tab_names():
            raise ValueError("Tab already in TabGroup")
        self._tabs[tab.name] = tab

    def tab_names(self) -> list[str]:
        return list(self._tabs.keys())

    def tabs(self) -> list[Tab]:
        return list(self._tabs.values())

    def fix(self):
        #tab label width = tab name length +4
        width = 0
        for tab_name in self.tab_names():
            width = (
                width + 
                len(tab_name) + 
                len(TabGroup.left_dec) + 
                len(TabGroup. right_dec)+2 #TODO this is because of spaces
            )

        #print(width)
        if width <= self.screen.width:
            #print("no scroll needed")
            self._headers = TabGroup._no_scroll(self.screen, self.tab_names())
        else:
            #print("we need to scroll")
            raise NotImplemented("fuck you jorian")
        
        for tab in self.tabs():
            tab.fix(self._headers[tab_name], None, None)
        

    def tab_header(self, tab_name:str)-> Frame:
        if tab_name not in self.tab_names():
            raise ValueError("Tab must be in TabGroup")
        return self._headers[tab_name]

    @staticmethod
    def _no_scroll(screen, tab_group) -> dict[str,Frame]:
        headers:dict[str, Frame] = {}
        for tab_name in tab_group:
            columns = []
            tab_row:list[Label] = []
            divider_row:list[Label] =[]
            for label_text in tab_group:
                if label_text == tab_name:
                    left_dec = Label(TabGroup.left_dec)
                    left_dec.disabled = True
                    tab_row.append(left_dec)
                    columns.append(len(left_dec.text))

                    tab = Label(f' {label_text} ')
                    tab.disabled = False
                    tab_row.append(tab)
                    columns.append(len(tab.text))

                    right_dec = Label(TabGroup.right_dec)
                    right_dec.disabled = True
                    tab_row.append(right_dec)
                    columns.append(len(right_dec.text))

                    left_div = Label(TabGroup.left_div)
                    left_div.disabled = True
                    divider_row.append(left_div)

                    padding = Label(' '.ljust(len(label_text)+2)) #TODO remove hard code
                    padding.disabled = True
                    divider_row.append(padding)

                    right_div = Label(TabGroup.right_div)
                    right_div.disabled = True
                    divider_row.append(right_div)

                else:
                    tab = Label(f'{TabGroup.left_dec} {label_text} {TabGroup.right_dec}')
                    tab.disabled = True
                    tab_row.append(tab)
                    columns.append(len(tab.text))

                    
                    padding_text = (f'{TabGroup.connect_div}{TabGroup.div.ljust(len(label_text)+2,TabGroup.div)}{TabGroup.connect_div}')
                    padding = Label(padding_text)  #TODO remove hard code
                    padding.disabled = True
                    divider_row.append(padding)



            # for label in tab_row:
            #     print(label.text,end='')
            # print('')

            # for label in divider_row:
            #     print(label.text,end='')
            # print('')
            # print(columns)

            # print('col len', len(columns))
            # print('tab row len', len(tab_row))
            # print('div row len', len(divider_row))


            tabs_frame = Frame(screen, height=2, width=screen.width, has_border=False, can_scroll= False, x=0, y=0)
            tabs_frame_layout = Layout(columns,fill_frame=True)
            tabs_frame.add_layout(tabs_frame_layout)
            for i in range(0, len(columns)):
                tabs_frame_layout.add_widget(tab_row[i],i)
                tabs_frame_layout.add_widget(divider_row[i],i)
            
            tabs_frame.fix()
            headers[tab_name] = tabs_frame

        return headers