from tkinter import Tk as _Tk

from views.projects import *
from views.cards import *
from views.mode import *
from views.card import *
from views.progress import *


VEV_CLOSE_APP = '<<CloseApp>>'


class App:

    def __init__(self):
        self.root = _Tk()
        # App sections
        self.projects = ProjectsSec(self.root)
        self.cards = CardsSec(self.root)
        self.progress = ProgressSec(self.root)
        self.viewer = CardSec(self.root)
        self.mode = ModeSec(self.root)
        # Positioning
        self.projects._grid(
            row=0, column=1, sticky='wnes', padx=(1, 2), pady=(2, 0))
        self.cards._grid(
            row=1, column=1, sticky='wnes', padx=(1, 2), pady=(0, 0))
        self.progress._grid(
            row=2, column=1, sticky='wnes', padx=(1, 2), pady=(0, 0))
        self.mode._grid(
            row=3, column=1, sticky='wnes', padx=(1, 2), pady=(0, 2))
        self.viewer._grid(
            row=0, column=0, rowspan=4, sticky='wnes', pady=2, padx=(2, 0))
        # Resizing
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        # Handle app destroy
        self.root.protocol('WM_DELETE_WINDOW', self.close_callback)

    def close_callback(self):
        self.root.event_generate(VEV_CLOSE_APP)

    def bind(self, event, command, percent_subs=tuple()):
        command = self.root.register(command)
        command = "%s %s" %(command, ' '.join(percent_subs))
        self.root.tk.call(
            "bind", str(self.root), event, command)

    def run(self):
        self.root.mainloop()
