import tkinter as tk
import tkinter.ttk as ttk


__all__ = ["ProgressSec"]


class ProgressSec:

    def __init__(self, root):
        self._root = root
        # Section frame
        self._frame = ttk.Frame(root)
        # Last studied
        self._last_studied_var = tk.StringVar()
        self._last_studied_var.trace_add('write', self._update_last_studied)
        self._last_studied_lbl = ttk.Label(
            self._frame, text='Last studied in :', anchor='w')
        self._last_studied_lbl.grid(row=0, column=0, sticky='w')
        # Reviewed today
        self._reviewed_today_var = tk.StringVar()
        self._reviewed_today_var.trace_add(
            'write', self._update_reviewed_today)
        self._reviewed_today_lbl = ttk.Label(
            self._frame, text='# Cards reviewed today :', anchor='w')
        self._reviewed_today_lbl.grid(row=1, column=0, sticky='w')
        # Learned today
        self._learned_today_var = tk.StringVar()
        self._learned_today_var.trace_add(
            'write', self._update_learned_today)
        self._learned_today_lbl = ttk.Label(
            self._frame, text='# Cards learned today :', anchor='w')
        self._learned_today_lbl.grid(row=2, column=0, sticky='w')
        # Progress bar
        self._progress_var = tk.StringVar(value='0.0')
        self._progress_var.trace_add('write', self._update_progress)
        self._progress_lbl = ttk.Label(
            self._frame, text='Overall progress : 0.0%', anchor='w')
        self._progress_lbl.grid(row=3, column=0, sticky='w')
        self._progress_bar = ttk.Progressbar(
            self._frame, variable=self._progress_var,
            orient='horizontal', mode='determinate')
        self._progress_bar.grid(row=4, column=0, sticky='we', pady=2)
        # Resizing/Borders
        self._frame.columnconfigure(0, weight=1)
        self._frame.configure(borderwidth=5, relief='groove')

    def _update_progress(self, *args):
        self._progress_lbl.configure(
            text='Overall progress : %s%%' %self._progress_var.get())

    def _update_last_studied(self, *args):
        self._last_studied_lbl.configure(
            text='Last studied in : %s' %self._last_studied_var.get())

    def _update_reviewed_today(self, *args):
        self._reviewed_today_lbl.configure(
            text='# Cards reviewed today : %s' %self._reviewed_today_var.get())

    def _update_learned_today(self, *args):
        self._learned_today_lbl.configure(
            text='# Cards learned today : %s' %self._learned_today_var.get())

    def set_progress(self, percentage):
        self._progress_var.set('%.1f' %float(percentage))

    def set_last_studied(self, datetime_str):
        self._last_studied_var.set(datetime_str)

    def set_todays_reviews(self, num_reviewed):
        self._reviewed_today_var.set(str(num_reviewed))

    def increment_todays_reviews(self, increment=1):
        num_rv = int(self._reviewed_today_var.get())
        self.set_todays_reviews(num_rv + increment)

    def set_todays_learnings(self, num_learned):
        self._learned_today_var.set(str(num_learned))

    def increment_todays_learnings(self, increment=1):
        num_lr = int(self._learned_today_var.get())
        self.set_todays_learnings(num_lr + increment)

    def reset(self):
        self.set_progress(0.0)
        self.set_last_studied('')
        self.set_todays_reviews('')
        self.set_todays_learnings('')

    def _grid(self, *, row, column,
              rowspan=1, columnspan=1, sticky='', **kwargs):
        self._frame.grid(row=row, column=column, sticky=sticky,
                        rowspan=rowspan, columnspan=columnspan,
                        **kwargs)
