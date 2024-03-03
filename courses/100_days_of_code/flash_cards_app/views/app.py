from tkinter import Tk

from projects import ProjectsSec
from cards import CardsSec
from progress import ProgressSec
from mode import ModeSec
from card import CardSec

root = Tk()

projects_sec = ProjectsSec(root)
cards_sec = CardsSec(root)
progress_sec = ProgressSec(root)
mode_sec = ModeSec(root)
card_sec = CardSec(root)

# df.grid(row=0, column=0, rowspan=3)
projects_sec.grid(row=0, column=1, sticky='wnes', padx=(1, 2), pady=(2, 0))
cards_sec.grid(row=1, column=1, sticky='wnes', padx=(1, 2), pady=(0, 0))
progress_sec.grid(row=2, column=1, sticky='wnes', padx=(1, 2), pady=(0, 0))
mode_sec.grid(row=3, column=1, sticky='wnes', padx=(1, 2), pady=(0, 2))
card_sec.grid(row=0, column=0, rowspan=4, sticky='wnes', pady=2, padx=(2, 0))

root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)

card_sec.card.set_content(
    'You should enjoy the little detours to the fullest\n-- Ging Freecss',
    'example.png')

root.mainloop()
