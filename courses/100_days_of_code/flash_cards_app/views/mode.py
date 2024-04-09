import tkinter as tk
import tkinter.ttk as ttk


__all__ = ["VEV_QUIZ_MODE",
           "VEV_REVISION_MODE",
           "ModeSec"]


VEV_QUIZ_MODE = '<<QuizMode>>'
VEV_REVISION_MODE = '<<RevisionMode>>'


class ModeSec:

    def __init__(self, root):
        self._root = root
        # Section frame
        self._frame = ttk.Frame(root)
        # Quiz mode checkbutton
        self._mode_var = tk.StringVar()
        self._mode_btn = ttk.Checkbutton(
            self._frame, text='Quiz mode',
            variable=self._mode_var, takefocus=0,
            command=self._mode_update_callback)
        self._mode_btn.grid(row=0, column=0)
        # Resizing/Borders
        self._frame.columnconfigure(0, weight=1)
        self._frame.configure(borderwidth=5, relief='groove')

    def _mode_update_callback(self):
        value = self._mode_var.get()
        if value == '1':
            self._root.event_generate(VEV_QUIZ_MODE)
        elif value == '0':
            self._root.event_generate(VEV_REVISION_MODE)
        else:
            self.set_default()

    def get_mode(self):
        return 'quiz' if self._mode_var.get() == '1' else 'revision'

    def set_default(self):
        self._mode_var.set('0')
        self._root.event_generate(VEV_REVISION_MODE)

    def _grid(self, *, row, column,
              rowspan=1, columnspan=1, sticky='', **kwargs):
        self._frame.grid(row=row, column=column, sticky=sticky,
                        rowspan=rowspan, columnspan=columnspan,
                        **kwargs)
