import tkinter as tk
import tkinter.ttk as ttk


__all__ = ["VEV_CARD_SET",
           "VEV_CARD_CREATE",
           "VEV_CARD_DELETE",
           "VEV_CARD_NONE",
           "VEV_CARDS_FILTERING",
           "VEV_FILTER_CATEG_SET",
           "CardsSec"]


VEV_CARD_SET = '<<CardSet>>'
VEV_CARD_CREATE = '<<CardCreate>>'
VEV_CARD_DELETE = '<<CardDelete>>'
VEV_CARD_NONE = '<<NoWorkingCard>>'
VEV_CARDS_FILTERING = '<<CardsFiltering>>'
VEV_FILTER_CATEG_SET = '<<FilterCategSet>>'


class CardsSec:

    def __init__(self, root):
        self._root = root
        # Section frame
        self._frame = ttk.Frame(root)
        # Section header
        self._header_lbl = ttk.Label(
            self._frame, text='Cards', anchor='center')
        self._header_lbl.grid(row=0, column=0, columnspan=2, sticky='wnes')
        # Cards tree list
        self._inner_frame = ttk.Frame(self._frame, relief='sunken', padding=5)
        self._inner_frame.grid(row=1, column=0, columnspan=2, sticky='wnes')
        self._cards_tree_list = ttk.Treeview(
            self._inner_frame, height=15,
            selectmode='browse', columns=('score',))
        self._cards_tree_list.column('score', width=60)
        self._cards_tree_list.heading('#0', text='Name')
        self._cards_tree_list.heading('score', text='Score')
        self._cards_tree_list.grid(
            row=0, column=0, columnspan=4, sticky='wnes')
        ## Filter category
        self._filter_categ_lbl = ttk.Label(
            self._inner_frame, text='Filter ctg.', padding=1)
        self._filter_categ_lbl.grid(row=1, column=0, sticky='we')
        self._filter_categ_var = tk.StringVar()
        self._filter_categ_var.trace_add(
            'write', self._filter_categ_selection_handler)
        self._filter_categ_combox = ttk.Combobox(
            self._inner_frame, state='readonly',
            textvariable=self._filter_categ_var)
        self._filter_categ_combox.grid(
            row=1, column=1, columnspan=3, sticky='we', pady=(4, 1))
        ## Filter value
        self._filter_value_lbl = ttk.Label(
            self._inner_frame, text='Filter value', padding=1)
        self._filter_value_lbl.grid(row=2, column=0, sticky='we')
        self._filter_value_var = tk.StringVar()
        self._filter_value_combox = ttk.Combobox(
            self._inner_frame, state='normal',
            textvariable=self._filter_value_var)
        self._filter_value_combox.bind('<Return>', self._filter_handler)
        self._filter_value_combox.grid(
            row=2, column=1, columnspan=3, sticky='we', pady=(1, 0))
        # Selected card
        self._selected = None
        ## Tag for implementing selection event
        self._dclick = 'dclick'
        self._cards_tree_list.tag_bind(
            self._dclick, '<Double-Button-1>', self._selection_handler)
        ## Tag for configure selected item
        self._slct = 'selected'
        self._cards_tree_list.tag_configure(self._slct, background='#E0E0E0')
        # Button to create new card
        self._create_btn = ttk.Button(
            self._frame, text='New', command=self._create_callback)
        self._create_btn.grid(
            row=2, column=0, padx=(0, 1), pady=(2, 0), sticky='we')
        # Button to delete working card
        self._delete_btn = ttk.Button(
            self._frame, text='Delete',
            command=self._delete_callback, state='disabled')
        self._delete_btn.grid(
            row=2, column=1, padx=(1, 0), pady=(2, 0), sticky='we')
        # Needed because treeview 'loses' detached items
        self._detached_cards = []
        # Resizing/Borders
        self._inner_frame.columnconfigure(
            (0, 1, 2, 3), weight=1, uniform=True)
        self._inner_frame.rowconfigure(0, weight=1)
        self._frame.rowconfigure(1, weight=1)
        self._frame.configure(borderwidth=5, relief='groove')

    def set_working_card(self, name=None):
        try:
            self._cards_tree_list.item(self._selected, tags=(self._dclick,))
        except tk.TclError:
            pass
        if name is None:
            self._selected = None
            self._delete_btn.state(['disabled'])
            self._root.event_generate(VEV_CARD_NONE)
        else:
            self._selected = name
            self._cards_tree_list.item(name, tags=(self._dclick, self._slct))
            self._delete_btn.state(['!disabled'])
            self._root.event_generate(VEV_CARD_SET, data=name)

    def get_working_card(self):
        return self._selected

    def insert_card(self, name, score, idx='end'):
        self._cards_tree_list.insert(
            '', idx, name, text=name, values=score, tags=(self._dclick,))

    def extend_cards(self, names, scores, at=None):
        if at is None:
            for name, score in zip(names, scores):
                self._cards_tree_list.insert(
                    '', 'end', name,
                    text=name, values=score, tags=(self._dclick,))
        else:
            for name, score in zip(names, scores):
                self._cards_tree_list.insert(
                    '', at, name,
                    text=name, values=score, tags=(self._dclick,))
                at += 1

    def remove_card(self, name):
        try: self._detached_cards.remove(name)
        except ValueError: pass
        self._cards_tree_list.delete(name)

    def pop_card(self, idx=-1):
        try:
            cname = self._cards_tree_list.get_children()[idx]
        except IndexError:
            return None
        self._cards_tree_list.delete(cname)
        return cname

    def detach_card(self, name):
        if name in self._detached_cards:
            return None
        idx = self._cards_tree_list.index(name)
        self._cards_tree_list.selection_remove(name)
        self._cards_tree_list.detach(name)
        self._detached_cards.append(name)
        return idx

    def detach_card_by_index(self, idx):
        try:
            name = self._cards_tree_list.get_children()[idx]
        except IndexError:
            return None
        self._cards_tree_list.selection_remove(name)
        self._cards_tree_list.detach(name)
        self._detached_cards.append(name)
        return name

    def reattach_card(self, name, idx='end'):
        try:
            self._detached_cards.remove(name)
        except ValueError:
            return False
        self._cards_tree_list.reattach(name, '', idx)
        return True

    def switch_card(self, name, new_idx):
        if name in self._detached_cards:
            return False
        old_idx = self._cards_tree_list.index(name)
        return self.switch_card_by_index(old_idx, new_idx)

    def switch_card_by_index(self, old_idx, new_idx):
        if old_idx == new_idx:
            return True
        min_idx, max_idx = ((old_idx, new_idx)
                            if old_idx < new_idx
                            else (new_idx, old_idx))
        children = self._cards_tree_list.get_children()
        try:
            cname_min = children[min_idx]
        except IndexError:
            return False
        try:
            cname_max = children[max_idx]
        except IndexError:
            self._cards_tree_list.move(cname_min, '', 'end')
            return True
        self._cards_tree_list.move(cname_max, '', min_idx)
        self._cards_tree_list.move(cname_min, '', max_idx)
        return True

    def remove_all_cards(self):
        self._cards_tree_list.selection_set()
        self._filter_categ_combox.set('')
        self._filter_value_combox.set('')
        self._cards_tree_list.delete(*self._detached_cards)
        self._cards_tree_list.delete(*self._cards_tree_list.get_children())
        self._detached_cards = []
        self.set_working_card()

    def _create_callback(self):
        self._root.event_generate(VEV_CARD_CREATE)

    def _delete_callback(self):
        if self._selected is not None:
            self._root.event_generate(VEV_CARD_DELETE, data=self._selected)

    def _selection_handler(self, *args):
        selection = self._cards_tree_list.selection()
        self.set_working_card(selection[0] if selection else None)

    def _filter_categ_selection_handler(self, *args):
        self._root.event_generate(VEV_FILTER_CATEG_SET)

    def _filter_handler(self, *args):
        self._root.event_generate(VEV_CARDS_FILTERING)

    def set_filter_categories(self, categories):
        self._filter_categ_var.set('')
        self._filter_categ_combox.configure(
            values=categories, height=min(7, len(categories)))

    def set_filter_values(self, values):
        self._filter_value_var.set('')
        self._filter_value_combox.configure(
            values=values, height=min(7, len(values)))

    def _grid(self, *, row, column,
              rowspan=1, columnspan=1, sticky='', **kwargs):
        self._frame.grid(row=row, column=column, sticky=sticky,
                        rowspan=rowspan, columnspan=columnspan,
                        **kwargs)
