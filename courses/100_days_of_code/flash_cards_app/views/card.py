import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename
from PIL import Image
from PIL.ImageTk import PhotoImage
from os.path import normpath


all = ["VEV_EDIT_CARD",
       "VEV_CARD_FLIPPED",
       "VEV_KNOW_CARD",
       "VEV_DKNOW_CARD",
       "VEV_CARD_POPUP_CANCEL",
       "VEV_CARD_POPUP_CONCLUDE",
       "CardSec",
       "CardPopup"]


def load_tk_photoimage(img_path):
    return PhotoImage(Image.open(img_path))


VEV_EDIT_CARD = '<<EditCard>>'
VEV_CARD_FLIPPED = '<<CardFlipped>>'


class Card:

    def __init__(self, parent):
        self._parent = parent
        self._root = self._parent.winfo_toplevel()
        self._bg_color = '#99E2E2'
        # Canvas
        self._canvas = tk.Canvas(
            self._parent, width=500, height=500,
            bg=self._bg_color, highlightthickness=0)
        # Title label
        self._side_var = tk.StringVar()
        self._side_lbl = ttk.Label(
            self._canvas, textvariable=self._side_var,
            background=self._bg_color)
        # Edit button
        self._edit_btn = ttk.Button(
            self._canvas, text='Edit', state='disabled',
            command=self._edit_callback)
        # Flip button
        self._flip_btn = ttk.Button(
            self._canvas, text='Flip', state='disabled',
            command=self._flip_callback)
        # Working card id
        self._working_card_id = None
        ## Image
        # Canvas widget do not keep a referente to the image object
        # A reference to the image object must be explicity created
        # ... so it won't be garbage colected
        # Max width: 450; Max height: 300
        self._front_img_id = None
        self._front_img = None
        self._back_img_id = None
        self._back_img = None
        ## Text
        self._front_txt_id = None
        self._back_txt_id = None
        # Positioning
        ## Functionality widgets
        self._canvas.create_window(
            250, 17, anchor='center', window=self._side_lbl)
        self._canvas.create_window(5, 5, anchor='nw', window=self._edit_btn)
        self._canvas.create_window(495, 5, anchor='ne', window=self._flip_btn)
        ## Content widgets
        ### Positions
        self._center = (250, 270)
        self._top = (250, 200)
        self._bottom = (250, 425)
        # Default look
        self.set_as_empty()

    def _remove_images(self, which='all'):
        if self._front_img is not None and which in ('all', 'front'):
            self._canvas.delete(self._front_img_id)
            self._front_img = None
            self._front_img_id = None
        if self._back_img is not None and which in ('all', 'back'):
            self._canvas.delete(self._back_img_id)
            self._back_img = None
            self._back_img_id = None

    def _remove_texts(self, which='all'):
        if self._front_txt_id is not None and which in ('all', 'front'):
            self._canvas.delete(self._front_txt_id)
            self._front_txt_id = None
        if self._back_txt_id is not None and which in ('all', 'back'):
            self._canvas.delete(self._back_txt_id)
            self._back_txt_id = None

    def set_as_empty(self):
        self._remove_images()
        self._remove_texts()
        self._working_card_id = None
        self._side_var.set('Front')
        self._set_text('Empty...', self._center, 'front')
        self._set_text('Empty...', self._center, 'back', 'hidden')
        self.disable_buttons('edit')

    def _hide_item(self, item_id):
        self._canvas.itemconfigure(item_id, state='hidden')

    def _show_item(self, item_id, disabled=False):
        self._canvas.itemconfigure(
            item_id, state='disabled' if disabled else 'normal')

    def _set_text(self, text, position, which, state='normal'):
        if which == 'front':
            self._remove_texts('front')
            front_txt_lbl = ttk.Label(
                self._canvas, text=text,
                background=self._bg_color, justify='center')
            self._front_txt_id = self._canvas.create_window(
                *position, anchor='center', window=front_txt_lbl, state=state)
        if which == 'back':
            self._remove_texts('back')
            back_txt_lbl = ttk.Label(
                self._canvas, text=text,
                background=self._bg_color, justify='center')
            self._back_txt_id = self._canvas.create_window(
                *position, anchor='center', window=back_txt_lbl, state=state)

    def _set_image(self, img_path, position, which, state='normal'):
        if which == 'front':
            self._remove_images('front')
            self._front_img = load_tk_photoimage(img_path)
            self._front_img_id = self._canvas.create_image(
                *position, anchor='center',
                image=self._front_img, state=state)
        if which == 'back':
            self._remove_images('back')
            self._back_img = load_tk_photoimage(img_path)
            self._back_img_id = self._canvas.create_image(
                *position, anchor='center',
                image=self._back_img, state=state)

    def set_content(
            self, card_id,
            card_front_img, card_front_txt,
            card_back_img, card_back_txt):
        self._remove_images()
        self._remove_texts()
        self._working_card_id = card_id
        self._side_var.set('Front')
        # Card front
        if card_front_img and card_front_txt:
            self._set_image(card_front_img, self._top, 'front')
            self._set_text(card_front_txt, self._bottom, 'front')
        elif card_front_img:
            self._set_image(card_front_img, self._center, 'front')
        elif card_front_txt:
            self._set_text(card_front_txt, self._center, 'front')
        else:
            self._set_text('Empty...', self._center, 'front')
        # Card back
        if card_back_img and card_back_txt:
            self._set_image(card_back_img, self._top, 'back', 'hidden')
            self._set_text(card_back_txt, self._bottom, 'back', 'hidden')
        elif card_back_img:
            self._set_image(card_back_img, self._center, 'back', 'hidden')
        elif card_back_txt:
            self._set_text(card_back_txt, self._center, 'back', 'hidden')
        else:
            self._set_text('Empty...', self._center, 'back', 'hidden')

    def disable_buttons(self, which='all'):
        if which == 'all':
            self._edit_btn['state'] = 'disabled'
            self._flip_btn['state'] = 'disabled'
        elif which == 'edit':
            self._edit_btn['state'] = 'disabled'
        elif which == 'flip':
            self._flip_btn['state'] = 'disabled'

    def enable_buttons(self, which='all'):
        if which == 'all':
            self._edit_btn['state'] = '!disabled'
            self._flip_btn['state'] = '!disabled'
        elif which == 'edit':
            self._edit_btn['state'] = '!disabled'
        elif which == 'flip':
            self._flip_btn['state'] = '!disabled'

    def _edit_callback(self):
        self._root.event_generate(VEV_EDIT_CARD)

    def _flip_callback(self):
        if self._side_var.get() == 'Front':
            self._hide_item(self._front_img_id)
            self._hide_item(self._front_txt_id)
            self._show_item(self._back_img_id)
            self._show_item(self._back_txt_id)
            self._side_var.set('Back')
        else:
            self._hide_item(self._back_img_id)
            self._hide_item(self._back_txt_id)
            self._show_item(self._front_img_id)
            self._show_item(self._front_txt_id)
            self._side_var.set('Front')
        self._root.event_generate(VEV_CARD_FLIPPED)

    def _grid(self, *, row, column,
              rowspan=1, columnspan=1, sticky='', **kwargs):
        self._canvas.grid(row=row, column=column, sticky=sticky,
                         rowspan=rowspan, columnspan=columnspan,
                         **kwargs)


VEV_KNOW_CARD = '<<KnowCard>>'
VEV_DKNOW_CARD = '<<DontKnowCard>>'

class CardSec:

    def __init__(self, root):
        self._root = root
        # Section frame
        self._frame = ttk.Frame(self._root)
        # Card view
        self.card = Card(self._frame)
        self.card._grid(row=1, column=1, columnspan=2)
        # Know button
        self._know_btn = ttk.Button(
            self._frame, text='Know',
            command=self._know_callback, state='disabled')
        self._know_btn.grid(row=2, column=1)
        # Don't know button
        self._dknow_btn = ttk.Button(
            self._frame, text="Don't know",
            command=self._dknow_callback, state='disabled')
        self._dknow_btn.grid(row=2, column=2)
        self._frame.rowconfigure(1, pad=10)
        # Resizing/Borders
        self._frame.rowconfigure((0, 3), weight=1, uniform=True)
        self._frame.columnconfigure((0, 3), weight=1, uniform=True)
        self._frame.configure(borderwidth=5, relief='groove')

    def _know_callback(self):
        try:
            self._root.event_generate(
                VEV_KNOW_CARD, data=self.card._working_card_id)
        except AttributeError:
            pass

    def _dknow_callback(self):
        try:
            self._root.event_generate(
                VEV_DKNOW_CARD, data=self.card._working_card_id)
        except AttributeError:
            pass

    def disable_buttons(self):
        self._know_btn['state'] = 'disabled'
        self._dknow_btn['state'] = 'disabled'

    def enable_buttons(self):
        self._know_btn['state'] = '!disabled'
        self._dknow_btn['state'] = '!disabled'

    def _grid(self, *, row, column,
              rowspan=1, columnspan=1, sticky='', **kwargs):
        self._frame.grid(row=row, column=column, sticky=sticky,
                        rowspan=rowspan, columnspan=columnspan,
                        **kwargs)


VEV_CARD_POPUP_CONCLUDE = '<<CardPopupConclude>>'
VEV_CARD_POPUP_CANCEL = '<<CardPopupCancel>>'

class CardPopup:

    def __init__(self, parent, action='creation'):
        self._parent = parent
        self._root = parent.winfo_toplevel()
        self.action = action
        # Popup window
        self._popup = tk.Toplevel(parent)
        self._popup.title('Card %s' %action)
        self._popup.rowconfigure(0, weight=1)
        self._popup.columnconfigure((0, 1), weight=1, uniform=True)
        # Frame
        self._frame = ttk.Frame(self._popup)
        self._frame.grid(
            row=0, column=0, columnspan=2, sticky='wnes', padx=2, pady=2)
        self._frame.columnconfigure(1, weight=1)
        self._frame.configure(borderwidth=5, relief='groove')
        # Card name
        ## Label
        self._card_name_lbl = ttk.Label(
            self._frame, text='Card name:', anchor='w', padding=1)
        self._card_name_lbl.grid(row=0, column=0, sticky='we')
        ## Entry
        self._card_name_var = tk.StringVar()
        self._card_name_entry = ttk.Entry(
            self._frame, justify='left', textvariable=self._card_name_var)
        self._card_name_entry.grid(row=0, column=1, sticky='we')
        ## Learned checkbutton
        self._learned_var = tk.StringVar()
        self._learned_btn = ttk.Checkbutton(
            self._frame, text='Learned',
            variable=self._learned_var, takefocus=0, padding=1)
        self._learned_btn.grid(row=0, column=2)
        # Card front
        self._front_section_lbl = ttk.Label(
            self._frame, text='Card front', anchor='center', padding=1)
        self._front_section_lbl.grid(
            row=1, column=0, columnspan=3, sticky='we')
        ## Image
        ### Label
        self._front_img_lbl = ttk.Label(
            self._frame, text='Image:', anchor='w', padding=1)
        self._front_img_lbl.grid(row=2, column=0, sticky='we')
        ### Entry
        self._front_img_var = tk.StringVar()
        self._front_img_entry = ttk.Entry(
            self._frame, textvariable=self._front_img_var, justify='left')
        self._front_img_entry.grid(row=2, column=1, sticky='we')
        ### Button
        self._front_img_btn = ttk.Button(
            self._frame, text='/', command=self._select_front_image)
        self._front_img_btn.grid(row=2, column=2)
        ## Text
        ### Label
        self._front_txt_lbl = ttk.Label(
            self._frame, text='Text:', anchor='w', padding=1)
        self._front_txt_lbl.grid(row=3, column=0, sticky='we')
        ### Text box
        self._front_txt_box = tk.Text(self._frame, height=4, wrap='word')
        self._front_txt_box.grid(
            row=3, column=1, rowspan=4, columnspan=2, sticky='wnes')
        # Card back
        self._back_section_lbl = ttk.Label(
            self._frame, text='Card back', anchor='center', padding=1)
        self._back_section_lbl.grid(row=7, column=0, columnspan=3, sticky='we')
        ## Image
        ### Label
        self._back_img_lbl = ttk.Label(
            self._frame, text='Image:', anchor='w', padding=1)
        self._back_img_lbl.grid(row=8, column=0, sticky='we')
        ### Entry
        self._back_img_var = tk.StringVar()
        self._back_img_entry = ttk.Entry(
            self._frame, textvariable=self._back_img_var, justify='left')
        self._back_img_entry.grid(row=8, column=1, sticky='we')
        ### Button
        self._back_img_btn = ttk.Button(
            self._frame, text='/', command=self._select_back_image)
        self._back_img_btn.grid(row=8, column=2)
        ## Text
        ### Label
        self._back_txt_lbl = ttk.Label(
            self._frame, text='Text:', anchor='w', padding=1)
        self._back_txt_lbl.grid(row=9, column=0, sticky='we')
        ### Text box
        self._back_txt_box = tk.Text(self._frame, height=4, wrap='word')
        self._back_txt_box.grid(
            row=9, column=1, rowspan=4, columnspan=2, sticky='wnes')
        # Warning label
        self._warning_var = tk.StringVar()
        self._warning_lbl = ttk.Label(
            self._frame, textvariable=self._warning_var,
            foreground='#FF0000', anchor='w', padding=3)
        self._warning_lbl.grid(row=13, column=0, columnspan=3, sticky='we')
        # Cancel button
        self._cancel_btn = ttk.Button(
            self._popup, text='Cancel', command=self._cancel_callback)
        self._cancel_btn.grid(row=1, column=0, pady=(0, 3))
        # Conclude button
        self._conclude_btn = ttk.Button(
            self._popup, text='Create' if action == 'creation' else 'Save',
            command=self._conclude_callback)
        self._conclude_btn.grid(row=1, column=1, pady=(0, 3))
        # Handle popup destroy
        self._popup.protocol('WM_DELETE_WINDOW', self._cancel_callback)

    @classmethod
    def card_creation_popup(cls, root):
        return cls(root, 'creation')

    @classmethod
    def card_edition_popup(cls, root, card):
        popup = cls(root, 'edition')
        popup.set_content(name=card.name,
                          learned=card.learned,
                          front_img=card.fimg,
                          front_txt=card.ftxt,
                          back_img=card.bimg,
                          back_txt=card.btxt)
        return popup

    def _ask_img_file(self) -> str:
        # Pillow read and write supported files
        fmts = (('Image', ('.png', '.jpg', '.gif', '.jpeg', '.tiff')),)
        return askopenfilename(parent=self._popup,
                               title='Select a image file',
                               initialdir='~', filetypes=fmts)

    def _select_front_image(self):
        img_path = self._ask_img_file()
        if img_path:
            self._front_img_var.set(normpath(img_path))

    def _select_back_image(self):
        img_path = self._ask_img_file()
        if img_path:
            self._back_img_var.set(normpath(img_path))

    def warning(self, message):
        self._warning_var.set(message)

    def set_content(self,
                    name='', learned=False,
                    front_img='', front_txt='',
                    back_img='', back_txt=''):
        # Card name
        self._card_name_var.set(name)
        # Learned
        self._learned_var.set('1' if learned else '0')
        # Front image
        self._front_img_var.set(front_img)
        # Front text
        ## First char must be a float
        ## 0.0 and 1.0 seem to have the same effect
        ## Probably 1-based indexing
        ## But why float? Because of unicode? Idk yet
        self._front_txt_box.delete('0.0', 'end')
        self._front_txt_box.insert('0.0', '%s\n' %front_txt.strip())
        # Back image
        self._back_img_var.set(back_img)
        # Back text
        self._back_txt_box.delete('0.0', 'end')
        self._back_txt_box.insert('0.0', '%s\n' %back_txt.strip())

    def get_content(self):
        return (self._card_name_var.get().strip(),
                bool(self._learned_var.get()),
                self._front_img_var.get().strip(),
                self._front_txt_box.get('0.0', 'end').strip(),
                self._back_img_var.get().strip(),
                self._back_txt_box.get('0.0', 'end').strip())

    def close(self):
        self._popup.destroy()

    def _conclude_callback(self):
        self._root.event_generate(VEV_CARD_POPUP_CONCLUDE)

    def _cancel_callback(self):
        self._root.event_generate(VEV_CARD_POPUP_CANCEL)
