import tkinter as tk
import tkinter.ttk as ttk

# Mode section:
#   Functionality:
#     Set quiz mode on
#   Widgets:
#     Checkbutton to set quiz mode
#   Behaviors:
#     Changes next card functionality


VEV_QUIZ_MODE = '<<QuizMode>>'
VEV_REVISION_MODE = '<<RevisionMode>>'

class ModeSec:

    def __init__(self, root):
        self.root = root
        # Section frame
        self.frame = ttk.Frame(root)
        # Quiz mode checkbutton
        self.mode_var = tk.StringVar()
        self.mode_btn = ttk.Checkbutton(
            self.frame, text='Quiz mode',
            variable=self.mode_var, takefocus=0,
            command=self.mode_update_callback)
        self.mode_btn.grid(row=0, column=0)
        # Resizing/Borders
        self.frame.columnconfigure(0, weight=1)
        self.frame.configure(borderwidth=5, relief='groove')

    def mode_update_callback(self):
        value = self.mode_var.get()
        if value == '1':
            self.root.event_generate(VEV_QUIZ_MODE)
        elif value == '0':
            self.root.event_generate(VEV_REVISION_MODE)
        else:
            self.set_default()

    def set_default(self):
        self.mode_var.set('0')
        self.root.event_generate(VEV_REVISION_MODE)

    def grid(self, *, row, column, rowspan=1, columnspan=1, sticky, **kwargs):
        self.frame.grid(row=row, column=column, sticky=sticky,
                        rowspan=rowspan, columnspan=columnspan,
                        **kwargs)

root = tk.Tk()
mode = ModeSec(root)
mode.grid(row=0, column=0, sticky='we')

root.columnconfigure(0, weight=1)

mode.set_default()

root.mainloop()
