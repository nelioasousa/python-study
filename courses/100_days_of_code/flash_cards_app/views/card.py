import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename
from PIL import Image
from PIL.ImageTk import PhotoImage
from os.path import normpath

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


VEV_EDIT_CARD = '<<EditCard>>'

class Card:

    def __init__(self, parent):
        self.parent = parent
        self.root = self.parent.winfo_toplevel()
        self._bg_color = '#99E2E2'
        # Canvas
        self.canvas = tk.Canvas(
            self.parent, width=500, height=500,
            bg=self._bg_color, highlightthickness=0)
        # Title label
        self._side_var = tk.StringVar()
        self._side_lbl = ttk.Label(
            self.canvas, textvariable=self._side_var,
            background=self._bg_color)
        # Edit button
        self.edit_btn = ttk.Button(
            self.canvas, text='Edit', state='disabled',
            command=self.edit_callback)
        # Flip button
        self.flip_btn = ttk.Button(
            self.canvas, text='Flip', state='disabled',
            command=self.flip_callback)
        # Card content
        self._card = None
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
        self._front_txt_lbl = None
        self._back_txt_id = None
        self._back_txt_lbl = None
        # Positioning
        ## Functionality widgets
        self.canvas.create_window(
            250, 17, anchor='center', window=self._side_lbl)
        self.canvas.create_window(5, 5, anchor='nw', window=self.edit_btn)
        self.canvas.create_window(495, 5, anchor='ne', window=self.flip_btn)
        ## Content widgets
        ### Positions
        self._center = (250, 265)
        self._top = (250, 185)
        self._bottom = (250, 415)
        # Default look
        self.set_as_empty()

    def remove_images(self, which='all'):
        if self._front_img is not None and which in ('all', 'front'):
            self.canvas.delete(self._front_img_id)
            self._front_img = None
            self._front_img_id = None
        if self._back_img is not None and which in ('all', 'back'):
            self.canvas.delete(self._back_img_id)
            self._back_img = None
            self._back_img_id = None

    def remove_texts(self, which='all'):
        if self._front_txt_id is not None and which in ('all', 'front'):
            self.canvas.delete(self._front_txt_id)
            self._front_txt_id = None
        if self._back_txt_id is not None and which in ('all', 'back'):
            self.canvas.delete(self._back_txt_id)
            self._back_txt_id = None

    def set_as_empty(self):
        self.remove_images()
        self.remove_texts()
        self._card = None
        self.disable_buttons('all')

    def _hide_item(self, item_id):
        self.canvas.itemconfigure(item_id, state='hidden')

    def _show_item(self, item_id, disabled=False):
        self.canvas.itemconfigure(
            item_id, state='disabled' if disabled else 'normal')

    def _set_text(self, text, position, which, state='normal'):
        if which in ('f', 'front'):
            self.remove_texts('front')
            self._front_txt_lbl = ttk.Label(
                self.canvas, text=text,
                background=self._bg_color, justify='center')
            self._front_txt_id = self.canvas.create_window(
                *position, anchor='center',
                window=self._front_txt_lbl, state=state)
            return self._front_txt_id
        if which in ('b', 'back'):
            self.remove_texts('back')
            self._back_txt_lbl = ttk.Label(
                self.canvas, text=text,
                background=self._bg_color, justify='center')
            self._back_txt_id = self.canvas.create_window(
                *position, anchor='center',
                window=self._back_txt_lbl, state=state)
            return self._back_txt_id
        return None

    def _set_image(self, img_path, position, which, state='normal'):
        if which in ('f', 'front'):
            self.remove_images('front')
            self._front_img = load_tk_photoimage(img_path)
            self._front_img_id = self.canvas.create_image(
                *position, anchor='center',
                image=self._front_img, state=state)
            return self._front_img_id
        if which in ('b', 'back'):
            self.remove_images('back')
            self._back_img = load_tk_photoimage(img_path)
            self._back_img_id = self.canvas.create_image(
                *position, anchor='center',
                image=self._back_img, state=state)
            return self._back_img_id
        return None

    def set_card(self, card):
        self.remove_images()
        self.remove_texts()
        self._card = card
        self._side_var.set('Front')
        if card.fimg and card.ftxt:
            self._set_image(
                card.fimg, position=self._top, which='front')
            self._set_text(
                card.ftxt, position=self._bottom, which='front')
        elif card.fimg:
            self._set_image(
                card.fimg, position=self._center, which='front')
        else:
            self._set_text(
                card.ftxt, position=self._center, which='front')
        if card.bimg and card.btxt:
            self._set_image(
                card.bimg, position=self._top, which='back', state='hidden')
            self._set_text(
                card.btxt, position=self._bottom,
                which='back', state='hidden')
        elif card.bimg:
            self._set_image(
                card.bimg, position=self._center,
                which='back', state='hidden')
        else:
            self._set_text(
                card.btxt, position=self._center,
                which='back', state='hidden')

    def disable_buttons(self, which='all'):
        if which == 'all':
            self.edit_btn['state'] = 'disabled'
            self.flip_btn['state'] = 'disabled'
        elif which == 'edit':
            self.edit_btn['state'] = 'disabled'
        elif which == 'flip':
            self.flip_btn['state'] = 'disabled'

    def enable_buttons(self, which='all'):
        if which == 'all':
            self.edit_btn['state'] = '!disabled'
            self.flip_btn['state'] = '!disabled'
        elif which == 'edit':
            self.edit_btn['state'] = '!disabled'
        elif which == 'flip':
            self.flip_btn['state'] = '!disabled'

    def edit_callback(self):
        self.root.event_generate(VEV_EDIT_CARD)

    def flip_callback(self):
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


VEV_CARD_POPUP_CONCLUDE = '<<CardPopupConclude>>'
VEV_CARD_POPUP_CANCEL = '<<CardPopupCancel>>'

class CardPopup:

    def __init__(self, parent, action='creation'):
        self.parent = parent
        self.action = action
        self.root = parent.winfo_toplevel()
        # Popup window
        self.popup = tk.Toplevel(parent)
        self.popup.title('Card %s' %action)
        self.popup.rowconfigure(0, weight=1)
        self.popup.columnconfigure((0, 1), weight=1, uniform=True)
        # Frame
        self.frame = ttk.Frame(self.popup)
        self.frame.grid(
            row=0, column=0, columnspan=2, sticky='wnes', padx=2, pady=2)
        self.frame.columnconfigure(1, weight=1)
        self.frame.configure(borderwidth=5, relief='groove')
        # Card name
        ## Label
        self.card_name_lbl = ttk.Label(
            self.frame, text='Card name:', anchor='w', padding=1)
        self.card_name_lbl.grid(row=0, column=0, sticky='we')
        ## Entry
        self.card_name_var = tk.StringVar()
        self.card_name_entry = ttk.Entry(
            self.frame, justify='left', textvariable=self.card_name_var)
        self.card_name_entry.grid(row=0, column=1, sticky='we')
        ## Learned checkbutton
        self.learned_var = tk.StringVar()
        self.learned_btn = ttk.Checkbutton(
            self.frame, text='Learned',
            variable=self.learned_var, takefocus=0, padding=1)
        self.learned_btn.grid(row=0, column=2)
        # Card front
        self.front_section_lbl = ttk.Label(
            self.frame, text='Card front', anchor='center', padding=1)
        self.front_section_lbl.grid(
            row=1, column=0, columnspan=3, sticky='we')
        ## Image
        ### Label
        self.front_img_lbl = ttk.Label(
            self.frame, text='Image:', anchor='w', padding=1)
        self.front_img_lbl.grid(row=2, column=0, sticky='we')
        ### Entry
        self.front_img_var = tk.StringVar()
        self.front_img_entry = ttk.Entry(
            self.frame, textvariable=self.front_img_var, justify='left')
        self.front_img_entry.grid(row=2, column=1, sticky='we')
        ### Button
        self.front_img_btn = ttk.Button(
            self.frame, text='/', command=self.select_front_image)
        self.front_img_btn.grid(row=2, column=2)
        ## Text
        ### Label
        self.front_txt_lbl = ttk.Label(
            self.frame, text='Text:', anchor='w', padding=1)
        self.front_txt_lbl.grid(row=3, column=0, sticky='we')
        ### Text box
        self.front_txt_box = tk.Text(self.frame, height=4, wrap='word')
        self.front_txt_box.grid(
            row=3, column=1, rowspan=4, columnspan=2, sticky='wnes')
        # Card back
        self.back_section_lbl = ttk.Label(
            self.frame, text='Card back', anchor='center', padding=1)
        self.back_section_lbl.grid(row=7, column=0, columnspan=3, sticky='we')
        ## Image
        ### Label
        self.back_img_lbl = ttk.Label(
            self.frame, text='Image:', anchor='w', padding=1)
        self.back_img_lbl.grid(row=8, column=0, sticky='we')
        ### Entry
        self.back_img_var = tk.StringVar()
        self.back_img_entry = ttk.Entry(
            self.frame, textvariable=self.back_img_var, justify='left')
        self.back_img_entry.grid(row=8, column=1, sticky='we')
        ### Button
        self.back_img_btn = ttk.Button(
            self.frame, text='/', command=self.select_back_image)
        self.back_img_btn.grid(row=8, column=2)
        ## Text
        ### Label
        self.back_txt_lbl = ttk.Label(
            self.frame, text='Text:', anchor='w', padding=1)
        self.back_txt_lbl.grid(row=9, column=0, sticky='we')
        ### Text box
        self.back_txt_box = tk.Text(self.frame, height=4, wrap='word')
        self.back_txt_box.grid(
            row=9, column=1, rowspan=4, columnspan=2, sticky='wnes')
        # Warning label
        self.warning_var = tk.StringVar()
        self.warning_lbl = ttk.Label(
            self.frame, textvariable=self.warning_var,
            foreground='#FF0000', anchor='w', padding=3)
        self.warning_lbl.grid(row=13, column=0, columnspan=3, sticky='we')
        # Cancel button
        self.cancel_btn = ttk.Button(
            self.popup, text='Cancel', command=self.cancel_callback)
        self.cancel_btn.grid(row=1, column=0, pady=(0, 3))
        # Conclude button
        self.conclude_btn = ttk.Button(
            self.popup, text='Create' if action == 'creation' else 'Save',
            command=self.conclude_callback)
        self.conclude_btn.grid(row=1, column=1, pady=(0, 3))
        # Handle popup destroy
        self.popup.protocol('WM_DELETE_WINDOW', self.cancel_callback)

    @classmethod
    def card_creation_popup(cls, root):
        return cls(root, 'creation')

    @classmethod
    def card_edition_popup(cls, root, card):
        popup = cls(root, 'edition')
        popup._set_content(name=card.name,
                           learned=card.learned,
                           front_img=card.fimg,
                           front_txt=card.ftxt,
                           back_img=card.bimg,
                           back_txt=card.btxt)
        return popup

    def ask_img_file(self) -> str:
        fmts = (('Image', ('.png', '.jpg', '.gif', '.jpeg', '.tiff')),)
        return askopenfilename(parent=self.popup,
                               title='Select a image file',
                               initialdir='~', filetypes=fmts)

    def select_front_image(self):
        img_path = self.ask_img_file()
        if img_path:
            self.front_img_var.set(normpath(img_path))

    def select_back_image(self):
        img_path = self.ask_img_file()
        if img_path:
            self.back_img_var.set(normpath(img_path))

    def warning(self, message):
        self.warning_var.set(message)

    def _set_content(self,
                     name='', learned=False,
                     front_img='', front_txt='',
                     back_img='', back_txt=''):
        # Card name
        self.card_name_var.set(name)
        # Learned
        self.learned_var.set('1' if learned else '0')
        # Front image
        self.front_img_var.set(front_img)
        # Front text
        ## First char must be a float
        ## 0.0 and 1.0 seem to have the same effect
        ## Probably 1-based indexing
        ## But why float? because of unicode?
        self.front_txt_box.delete('0.0', 'end')
        self.front_txt_box.insert('0.0', '%s\n' %front_txt.strip())
        # Back image
        self.back_img_var.set(back_img)
        # Back text
        self.back_txt_box.delete('0.0', 'end')
        self.back_txt_box.insert('0.0', '%s\n' %back_txt.strip())

    def get_content(self):
        return (self.card_name_var.get(),
                self.learned_var.get(),
                self.front_img_var.get(),
                self.front_txt_box.get('0.0', 'end').strip(),
                self.back_img_var.get(),
                self.back_txt_box.get('0.0', 'end').strip())

    def close(self):
        self.popup.destroy()

    def conclude_callback(self):
        self.root.event_generate(VEV_CARD_POPUP_CONCLUDE)

    def cancel_callback(self):
        self.root.event_generate(VEV_CARD_POPUP_CANCEL)
