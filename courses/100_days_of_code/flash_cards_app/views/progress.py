import tkinter as tk
import tkinter.ttk as ttk

# Progress section:
#   Functionality:
#     Learned percentage
#     Last studied
#     Number of cards reviewed today
#     Number of cards learned today
#   Widgets:
#     Labels
#     Progressbar
#   Behaviors:
#     None


class ProgressSec:

    def __init__(self, root):
        self.root = root
        # Section frame
        self.frame = ttk.Frame(root)
        # Last studied
        self.last_studied_var = tk.StringVar()
        self.last_studied_var.trace_add('write', self._update_last_studied)
        self.last_studied_lbl = ttk.Label(
            self.frame, text='Last studied in :', anchor='w')
        self.last_studied_lbl.grid(row=0, column=0, sticky='w')
        # Reviewed today
        self.reviewed_today_var = tk.StringVar()
        self.reviewed_today_var.trace_add(
            'write', self._update_reviewed_today)
        self.reviewed_today_lbl = ttk.Label(
            self.frame, text='# Cards reviewed today :', anchor='w')
        self.reviewed_today_lbl.grid(row=1, column=0, sticky='w')
        # Learned today
        self.learned_today_var = tk.StringVar()
        self.learned_today_var.trace_add(
            'write', self._update_learned_today)
        self.learned_today_lbl = ttk.Label(
            self.frame, text='# Cards learned today :', anchor='w')
        self.learned_today_lbl.grid(row=2, column=0, sticky='w')
        # Progress bar
        self.progress_var = tk.StringVar(value='0.0')
        self.progress_var.trace_add('write', self._update_progress_caption)
        self.progress_lbl = ttk.Label(
            self.frame, text='Overall progress : 0.0%', anchor='w')
        self.progress_lbl.grid(row=3, column=0, sticky='w')
        self.progress_bar = ttk.Progressbar(
            self.frame, variable=self.progress_var,
            orient='horizontal', mode='determinate')
        self.progress_bar.grid(row=4, column=0, sticky='we', pady=2)
        # Resizing/Borders
        self.frame.columnconfigure(0, weight=1)
        self.frame.configure(borderwidth=5, relief='groove')

    def _update_progress_caption(self, *args):
        self.progress_lbl.configure(
            text='Overall progress : %s%%' %self.progress_var.get())
    
    def _update_last_studied(self, *args):
        self.last_studied_lbl.configure(
            text='Last studied in : %s' %self.last_studied_var.get())

    def _update_reviewed_today(self, *args):
        self.reviewed_today_lbl.configure(
            text='# Cards reviewed today : %s' %self.reviewed_today_var.get())

    def _update_learned_today(self, *args):
        self.learned_today_lbl.configure(
            text='# Cards learned today : %s' %self.learned_today_var.get())

    def set_progress(self, percentage):
        self.progress_var.set('%.1f' %float(percentage))
    
    def set_last_studied(self, datetime_str):
        self.last_studied_var.set(datetime_str)
    
    def set_todays_reviews(self, num_reviewed):
        self.reviewed_today_var.set(str(num_reviewed))
    
    def set_todays_learnings(self, num_learned):
        self.learned_today_var.set(str(num_learned))

    def grid(self, *, row, column, rowspan=1, columnspan=1, sticky, **kwargs):
        self.frame.grid(row=row, column=column, sticky=sticky,
                        rowspan=rowspan, columnspan=columnspan,
                        **kwargs)

root = tk.Tk()
progress = ProgressSec(root)
progress.grid(row=0, column=0, sticky='we')

root.columnconfigure(0, weight=1)

progress.set_progress(78.85)
progress.set_last_studied('02-21-2024 21:10:23.346681')
progress.set_todays_reviews(15)
progress.set_todays_learnings(7)

root.mainloop()
