import tkinter as tk
import tkinter.ttk as ttk

# Cards section:
#   Functionality:
#     List cards
#     Cards filter (Single filtering | No multi filtering)
#     Create card
#     Remove working card
#     Select new working card
#     Score cards by priority
#   Widgets:
#     Section static label
#     Button to create card
#     Combobox for filter category
#     Combobox for filter value
#     Button to delete working card
#   Behaviors:
#     Card selection update only card screen section
#     Card deletion loads next card
#     Filter cards only after return press
#     Card add, delete, review, and learning > New progress 
#     New progress > Updates progress section


VEV_CARD_SET = '<<CardSet>>'
VEV_CARD_CREATE = '<<CardCreate>>'
VEV_CARD_DELETE = '<<CardDelete>>'
VEV_CARD_NONE = '<<NoWorkingCard>>'
VEV_CARD_FILTER = '<<CardFiltering>>'
VEV_FILTER_CATEG = '<<FilterCategSet>>'

class CardsSec:

    def __init__(self, root):
        self.root = root
        # Section frame
        self.frame = ttk.Frame(root)
        # Section header
        self.header_lbl = ttk.Label(self.frame, text='Cards', anchor='center')
        self.header_lbl.grid(row=0, column=0, columnspan=2, sticky='wnes')
        # Cards tree list
        self._inner_frame = ttk.Frame(self.frame, relief='sunken', padding=5)
        self._inner_frame.grid(row=1, column=0, columnspan=2, sticky='ns')
        self.cards_tree_list = ttk.Treeview(
            self._inner_frame, height=15,
            selectmode='browse', columns=('score',))
        self.cards_tree_list.column('score', width=60)
        self.cards_tree_list.heading('#0', text='Name')
        self.cards_tree_list.heading('score', text='Score')
        self.cards_tree_list.grid(row=0, column=0, columnspan=4, sticky='ns')
        ## Filter category
        self.filter_categ_lbl = ttk.Label(
            self._inner_frame, text='Filter ctg.', padding=1)
        self.filter_categ_lbl.grid(row=1, column=0, sticky='we')
        self.filter_categ_var = tk.StringVar()
        self.filter_categ_var.trace_add('write',
                                        self.filter_categ_selection_callback)
        self.filter_categ_combox = ttk.Combobox(
            self._inner_frame, state='readonly',
            textvariable=self.filter_categ_var)
        self.filter_categ_combox.grid(
            row=1, column=1, columnspan=3, sticky='we', pady=(4, 1))
        ## Filter value
        self.filter_value_lbl = ttk.Label(
            self._inner_frame, text='Filter value', padding=1)
        self.filter_value_lbl.grid(row=2, column=0, sticky='we')
        self.filter_value_var = tk.StringVar()
        self.filter_value_combox = ttk.Combobox(
            self._inner_frame, state='normal',
            textvariable=self.filter_value_var)
        self.filter_value_combox.bind('<Return>', self.filter_callback)
        self.filter_value_combox.grid(
            row=2, column=1, columnspan=3, sticky='we', pady=(1, 0))
        # Selected item
        self._selected = tk.StringVar()
        self._selected.trace_add('write', self.button_state_callback)
        ## Tag for implementing selection event
        self._dclick = 'dclick'
        self.cards_tree_list.tag_bind(
            self._dclick, '<Double-Button-1>', self.selection_callback)
        ## Selected item tag
        self._slct = 'selected'
        self.cards_tree_list.tag_configure(self._slct, background='#E0E0E0')
        # Button to create new card
        self.create_btn = ttk.Button(
            self.frame, text='New', command=self.create_callback)
        self.create_btn.grid(
            row=2, column=0, padx=(0, 1), pady=(2, 0), sticky='we')
        # Button to delete working card
        self.delete_btn = ttk.Button(
            self.frame, text='Delete',
            command=self.delete_callback, state='disabled')
        self.delete_btn.grid(
            row=2, column=1, padx=(1, 0), pady=(2, 0), sticky='we')
        # Needed since treeview 'losses' detached items
        self.detached_cards = []
        # Resizing/Borders
        self._inner_frame.columnconfigure(
            (0, 1, 2, 3), weight=1, uniform=True)
        self._inner_frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.configure(borderwidth=5, relief='groove')

    def insert_card(self, cid, text, score, idx='end'):
        self.cards_tree_list.insert(
            '', idx, cid, text=text, values=score, tags=self._dclick)

    def extend_cards(self, cids, texts, scores, at=None):
        if at is None:
            for cid, text, score in zip(cids, texts, scores):
                self.cards_tree_list.insert(
                    '', 'end', cid, text=text,
                    values=score, tags=self._dclick)
        else:
            for cid, text, score in zip(cids, texts, scores):
                self.cards_tree_list.insert(
                    '', at, cid, text=text, values=score, tags=self._dclick)
                at += 1

    def remove_card(self, cid):
        try: self.detached_cards.remove(cid)
        except ValueError: pass
        self.cards_tree_list.delete(cid)

    def pop_card(self, idx=-1):
        try:
            cid = self.cards_tree_list.get_children()[idx]
        except IndexError:
            return None
        self.cards_tree_list.delete(cid)
        return cid

    def detach_card_by_id(self, cid):
        if cid in self.detached_cards:
            return None
        idx = self.cards_tree_list.index(cid)
        self.cards_tree_list.selection_remove(cid)
        self.cards_tree_list.detach(cid)
        self.detached_cards.append(cid)
        return idx

    def detach_card_by_index(self, idx=-1):
        try:
            cid = self.cards_tree_list.get_children()[idx]
        except IndexError:
            return None
        self.cards_tree_list.selection_remove(cid)
        self.cards_tree_list.detach(cid)
        self.detached_cards.append(cid)
        return cid

    def reattach_card(self, cid, idx='end'):
        try:
            self.detached_cards.remove(cid)
        except ValueError:
            return False
        self.cards_tree_list.reattach(cid, '', idx)
        return True

    def switch_card_by_id(self, cid, new_idx):
        if cid in self.detached_cards:
            return False
        old_idx = self.cards_tree_list.index(cid)
        return self.switch_card_by_index(old_idx, new_idx)

    def switch_card_by_index(self, old_idx, new_idx):
        if old_idx == new_idx:
            return True
        min_idx, max_idx = ((old_idx, new_idx)
                            if old_idx < new_idx
                            else (new_idx, old_idx))
        children = self.cards_tree_list.get_children()
        try:
            cid_min = children[min_idx]
        except IndexError:
            return False
        try:
            cid_max = children[max_idx]
        except IndexError:
            self.cards_tree_list.move(cid_min, '', 'end')
            return True
        self.cards_tree_list.move(cid_max, '', min_idx)
        self.cards_tree_list.move(cid_min, '', max_idx)
        return True

    def remove_all_cards(self):
        self.cards_tree_list.selection_set()
        self.filter_categ_combox.set('')
        self.filter_value_combox.set('')
        self.cards_tree_list.delete(*self.detached_cards)
        self.cards_tree_list.delete(*self.cards_tree_list.get_children())
        self.detached_cards = []

    def create_callback(self):
        self.root.event_generate(VEV_CARD_CREATE)

    def delete_callback(self):
        selected_item = self._selected.get()
        if selected_item:
            self.root.event_generate(VEV_CARD_DELETE, data=selected_item)

    def selection_callback(self, *args):
        selected_item = self._selected.get()
        if selected_item:
            self.cards_tree_list.item(selected_item, tags=(self._dclick,))
        selection = self.cards_tree_list.selection()
        if selection:
            self._selected.set(selection[0])
            self.cards_tree_list.item(
                selection[0], tags=(self._dclick, self._slct))
            self.root.event_generate(VEV_CARD_SET, data=selection[0])
        else:
            self._selected.set('')
            self.root.event_generate(VEV_CARD_NONE)

    def filter_categ_selection_callback(self, *args):
        self.root.event_generate(
            VEV_FILTER_CATEG, data=self.filter_categ_var.get())

    def filter_callback(self, *args):
        self.root.event_generate(VEV_CARD_FILTER,
                                 data=(self.filter_categ_var.get(),
                                       self.filter_value_var.get()))

    def button_state_callback(self, *args):
        if self._selected:
            self.delete_btn.state(['!disabled'])
        else:
            self.delete_btn.state(['disabled'])

    def set_filter_categories(self, categories):
        self.filter_categ_var.set('')
        self.filter_categ_combox.configure(
            values=categories, height=min(7, len(categories)))

    def set_filter_values(self, values):
        self.filter_value_var.set('')
        self.filter_value_combox.configure(
            values=values, height=min(7, len(values)))

    def grid(self, *, row, column,
             rowspan=1, columnspan=1, sticky='', **kwargs):
        self.frame.grid(row=row, column=column, sticky=sticky,
                        rowspan=rowspan, columnspan=columnspan,
                        **kwargs)
