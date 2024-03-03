import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image
from PIL.ImageTk import PhotoImage

# Card section:
#   Functionality:
#     Flip card
#     Edit card
#     Set card as learned
#     Set card as not learned
#     Next card
#   Widgets:
#     Button to set card as learned
#     Button to set card as not learned
#     Card screen
#       Label to indicate side
#       Label for text
#       Label for image
#       Button to flip card
#       Button to edit card
#   Behaviors:
#     Button to set/unset disabled until first flip
#     Edit button disabled until first flip
#     Next card only using set/unset button


def load_tk_photoimage(img_path):
    return PhotoImage(Image.open(img_path))


VEV_FLIP_CARD = '<<FlipCard>>'
VEV_EDIT_CARD = '<<EditCard>>'

class Card:

    def __init__(self, parent):
        self.parent = parent
        # Canvas
        self._color = '#99E2E2'
        self.canvas = tk.Canvas(
            self.parent, width=400, height=400,
            bg=self._color, highlightthickness=0)
        # Title label
        self.title_var = tk.StringVar()
        self.title_lbl = ttk.Label(
            self.canvas, textvariable=self.title_var, background=self._color)
        # Edit button
        self.edit_btn = ttk.Button(
            self.canvas, text='Edit', state='disabled',
            command=self.edit_callback)
        # Flip button
        self.flip_btn = ttk.Button(
            self.canvas, text='Flip', state='disabled',
            command=self.flip_callback)
        # Card content
        self.txt_lbl = ttk.Label(
            self.canvas, text='', justify='center', background=self._color)
        self._txt_id = None
        self._img_id = None  # 200x200
        # Canvas do not keep a referente to the image object
        # Attribute needed so image won't be garbage colected
        self._img = None
        # Positioning
        ## Functionality widgets
        self.canvas.create_window(
            200, 17, anchor='center', window=self.title_lbl)
        self.canvas.create_window(5, 5, anchor='nw', window=self.edit_btn)
        self.canvas.create_window(395, 5, anchor='ne', window=self.flip_btn)
        ## Content widgets
        ### Positions
        self._center = (200, 215)
        self._top = (200, 160)
        self._bottom = (200, 325)
        ### Label positioning
        self._txt_id = self.canvas.create_window(
            *self._center, anchor='center',
            window=self.txt_lbl, state='hidden')
        # Default look
        self.set_as_empty()

    def remove_image(self):
        if self._img is not None:
            self.canvas.delete(self._img_id)
            self._img = None
            self._img_id = None

    def set_as_empty(self):
        self.remove_image()
        self._set_text('Empty card...', self._center)
        self.disable_buttons('all')

    def _set_text(self, text, position=None):
        self.txt_lbl.configure(text=text)
        if position is not None:
            # moveto method uses top-left corner for positioning
            # widget WxH needed so widget center falls in position
            w = self.txt_lbl.winfo_reqwidth()
            h = self.txt_lbl.winfo_reqheight()
            self.canvas.moveto(
                self._txt_id, position[0] - w/2, position[1] - h/2)
        self.canvas.itemconfigure(self._txt_id, state='normal')

    def _set_image(self, img_path, position):
        self.remove_image()
        self._img = load_tk_photoimage(img_path)
        self._img_id = self.canvas.create_image(
            *position, anchor='center', image=self._img)

    def set_content(self, text=None, img_path=None):
        if text is img_path is None:
            self.set_as_empty()
        elif img_path is None:
            self.remove_image()
            self._set_text(text, self._center)
        elif text is None:
            self._set_text('')
            self._set_image(img_path, self._center)
        else:
            self._set_image(img_path, self._top)
            self._set_text(text, self._bottom)

    def disable_buttons(self, which):
        if which == 'all':
            self.edit_btn['state'] = 'disabled'
            self.flip_btn['state'] = 'disabled'
        elif which == 'edit':
            self.edit_btn['state'] = 'disabled'
        elif which == 'flip':
            self.flip_btn['state'] = 'disabled'

    def enable_buttons(self, which):
        if which == 'all':
            self.edit_btn['state'] = '!disabled'
            self.flip_btn['state'] = '!disabled'
        elif which == 'edit':
            self.edit_btn['state'] = '!disabled'
        elif which == 'flip':
            self.flip_btn['state'] = '!disabled'

    def edit_callback(self):
        self.parent.winfo_toplevel().event_generate(VEV_EDIT_CARD)

    def flip_callback(self):
        self.parent.winfo_toplevel().event_generate(VEV_EDIT_CARD)

    def grid(self, *, row, column,
             rowspan=1, columnspan=1, sticky='', **kwargs):
        self.canvas.grid(row=row, column=column, sticky=sticky,
                         rowspan=rowspan, columnspan=columnspan,
                         **kwargs)


VEV_KNOW_CARD = '<<KnowCard>>'
VEV_DKNOW_CARD = '<<DontKnowCard>>'

class CardSec:

    def __init__(self, root):
        self.root = root
        # Section frame
        self.frame = ttk.Frame(self.root)
        # Card view
        self.card = Card(self.frame)
        self.card.grid(row=1, column=1, columnspan=2)
        # Know button
        self.know_btn = ttk.Button(
            self.frame, text='Know',
            command=self.know_callback, state='disabled')
        self.know_btn.grid(row=2, column=1)
        # Don't know button
        self.dknow_btn = ttk.Button(
            self.frame, text='Don\'t know',
            command=self.dknow_callback, state='disabled')
        self.dknow_btn.grid(row=2, column=2)
        self.frame.rowconfigure(1, pad=10)
        # Resizing/Borders
        self.frame.rowconfigure((0, 3), weight=1, uniform=True)
        self.frame.columnconfigure((0, 3), weight=1, uniform=True)
        self.frame.configure(borderwidth=5, relief='groove')

    def know_callback(self):
        self.root.event_generate(VEV_KNOW_CARD)

    def dknow_callback(self):
        self.root.event_generate(VEV_DKNOW_CARD)

    def disable_buttons(self):
        self.know_btn['state'] = 'disabled'
        self.dknow_btn['state'] = 'disabled'

    def enable_buttons(self):
        self.know_btn['state'] = '!disabled'
        self.dknow_btn['state'] = '!disabled'

    def grid(self, *, row, column,
             rowspan=1, columnspan=1, sticky='', **kwargs):
        self.frame.grid(row=row, column=column, sticky=sticky,
                        rowspan=rowspan, columnspan=columnspan,
                        **kwargs)
