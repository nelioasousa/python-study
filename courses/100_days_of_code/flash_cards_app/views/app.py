from tkinter import Tk as _Tk

from projects import *
from cards import *
from mode import *
from card import *
from progress import *


VEV_CLOSE_APP = '<<CloseApp>>'


class App:

    def __init__(self):
        self.root = _Tk()
        # App sections
        self.projects_section = ProjectsSec(self.root)
        self.cards_section = CardsSec(self.root)
        self.progress_section = ProgressSec(self.root)
        self.card_section = CardSec(self.root)
        self.mode_section = ModeSec(self.root)
        # Positioning
        self.projects_section._grid(
            row=0, column=1, sticky='wnes', padx=(1, 2), pady=(2, 0))
        self.cards_section._grid(
            row=1, column=1, sticky='wnes', padx=(1, 2), pady=(0, 0))
        self.progress_section._grid(
            row=2, column=1, sticky='wnes', padx=(1, 2), pady=(0, 0))
        self.mode_section._grid(
            row=3, column=1, sticky='wnes', padx=(1, 2), pady=(0, 2))
        self.card_section._grid(
            row=0, column=0, rowspan=4, sticky='wnes', pady=2, padx=(2, 0))
        # Resizing
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        # Working data
        self.projects = []
        self.working_project = None
        self.working_card = None
        # Handle app destroy
        self.root.protocol('WM_DELETE_WINDOW', self.close_callback)

    def close_callback(self):
        self.root.event_generate(VEV_CLOSE_APP)

    def run(self):
        self.root.mainloop()

app = App()
app.card_section.card.set_content(
    '?', 'example.png', 'Ging Freecss', 'example.png',
    'You should enjoy the little detours to the fullest!')
app.card_section.card.enable_buttons('flip')
app.projects_section.set_post_command(lambda : ('Project 1', 'Project 2'))
app.cards_section.extend_cards(
    ('c1', 'c2', 'c3'),
    ('Card 1', 'Card 2', 'Card 3'),
    (99, 66, 33))
app.root.bind(VEV_CLOSE_APP, lambda _event: app.root.destroy())
app.run()
