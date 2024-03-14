from tkinter import Tk

from projects import ProjectsSec
from cards import CardsSec, VEV_CARD_CREATE
from progress import ProgressSec
from mode import ModeSec
from card import CardSec, VEV_EDIT_CARD, VEV_CARD_POPUP_CONCLUDE, VEV_CARD_POPUP_CANCEL
from card import CardPopup

import sys
sys.path.append('..')
from model import Card

root = Tk()

projects_sec = ProjectsSec(root)
cards_sec = CardsSec(root)
progress_sec = ProgressSec(root)
mode_sec = ModeSec(root)
card_sec = CardSec(root)

projects_sec.grid(row=0, column=1, sticky='wnes', padx=(1, 2), pady=(2, 0))
cards_sec.grid(row=1, column=1, sticky='wnes', padx=(1, 2), pady=(0, 0))
progress_sec.grid(row=2, column=1, sticky='wnes', padx=(1, 2), pady=(0, 0))
mode_sec.grid(row=3, column=1, sticky='wnes', padx=(1, 2), pady=(0, 2))
card_sec.grid(row=0, column=0, rowspan=4, sticky='wnes', pady=2, padx=(2, 0))

root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)

card = Card('Card1',
            'example.png',
            'Ging Freecss',
            'example.png',
            'You should enjoy the little detours to the fullest!')

card_sec.card.set_card(card)
card_sec.card.enable_buttons()

popup = None

def edit_popup(*args):
    global popup
    if popup is None:
        popup = CardPopup.card_edition_popup(root, card)
        popup.warning('Hello, my friend!')

def create_popup(*args):
    global popup
    if popup is None:
        popup = CardPopup.card_creation_popup(root)

def kill_popup(*args):
    global popup
    if popup is not None:
        popup.close()
        popup = None

root.bind(VEV_EDIT_CARD, edit_popup)
root.bind(VEV_CARD_CREATE, create_popup)
root.bind(VEV_CARD_POPUP_CONCLUDE, kill_popup)
root.bind(VEV_CARD_POPUP_CANCEL, kill_popup)

root.mainloop()
