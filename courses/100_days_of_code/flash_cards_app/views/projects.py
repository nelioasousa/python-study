import tkinter as tk
import tkinter.ttk as ttk

# Projects section:
#   Functionality:
#     List all projects
#     Create project
#     Delete project
#     Select working project
#     *No project filtering functionality
#     *No project edit functionality
#   Widgets:
#     Combobox to list projects
#     Static label to explain combobox
#     Button do create new project
#     Button do delete working project
#   Behaviors:
#     No working project > All sections empty
#     No working project > Delete button deactivated
#     Create project > Create button opens pop-up window
#     Create project > Combobox entry also create project
#     Create project > Created project as working project
#     Delete project > Confirmation pop-up
#     Delete project > No working project after
#     Project selection > Updates all other sections


VEV_PROJ_SET = '<<ProjectSet>>'
VEV_PROJ_CREATE = '<<ProjectCreate>>'
VEV_PROJ_DELETE = '<<ProjectDelete>>'

class ProjectsSec:

    def __init__(self, root):
        self.root = root
        # Section frame
        self.frame = ttk.Frame(root)
        # Project selection combobox
        self._combox_entry = tk.StringVar()
        self._combox_entry.trace_add('write', self.att_buttons_state)
        self.projects_combox = ttk.Combobox(
            self.frame, height=5, state='normal',
            textvariable=self._combox_entry)
        self.projects_combox.grid(row=0, column=1, columnspan=3, sticky='we')
        self.projects_combox.bind('<Return>', self.combobox_return)
        self.projects_combox.bind('<<ComboboxSelected>>',
                                  self.combobox_selection)
        # Attribute to store project creation popup
        self.popup = None
        # Dummy/Default function to list projects
        self.set_post_command()
        # Combobox label
        self.project_lbl = ttk.Label(
            self.frame, text='Project:', anchor='center', padding=1)
        self.project_lbl.grid(row=0, column=0)
        # New project button
        self.create_btn = ttk.Button(
            self.frame, text='New', command=self.create_callback)
        self.create_btn.grid(
            row=1, column=0, columnspan=2,
            sticky='we', padx=(0, 1), pady=(2, 0))
        # Delete project button
        self.delete_btn = ttk.Button(
            self.frame, text='Delete',
            command=self.delete_project, state='disabled')
        self.delete_btn.grid(
            row=1, column=2, columnspan=2,
            sticky='we', padx=(1, 0), pady=(2, 0))
        # Resizing/Borders
        self.frame.columnconfigure((0, 1, 2, 3), weight=1, uniform=True)
        self.frame.configure(borderwidth=5, relief='groove')
        # Bind popup virtual events
        self.root.bind(VEV_PROJECT_POPUP_CREATE, self.popup_create_handler)
        self.root.bind(VEV_PROJECT_POPUP_CANCEL, self.popup_cancel_handler)

    def set_post_command(self, post_command=None):
        self._post_command = tuple if post_command is None else post_command
        def post_wrapper():
            values = self._post_command()
            self.projects_combox.configure(values=values)
        self.projects_combox.configure(postcommand=post_wrapper)

    def set_validation(self, val_trigger, val_command):
        self.validation_trigger = val_trigger
        self.validation_command = val_command
        self.projects_combox.configure(
            validate=val_trigger, validatecommand=val_command)

    def set_working_project(self, project_name):
        if project_name in self.get_listed_projects():
            self.projects_combox.set(project_name)
            self.combobox_selection()

    def get_listed_projects(self):
        return self._post_command()

    def get_selection(self):
        proj_selection = self.projects_combox.get()
        if proj_selection in self.get_listed_projects():
            return proj_selection
        return None

    def combobox_return(self, *args):
        entry = self.projects_combox.get()
        if entry in self.get_listed_projects():
            self.root.event_generate(VEV_PROJ_SET, data=entry)
        else:
            self.root.event_generate(VEV_PROJ_CREATE, data=entry)

    def combobox_selection(self, *args):
        self.projects_combox.selection_clear()  # Clear text selection
        self.root.event_generate(VEV_PROJ_SET, data=self.get_selection())

    def create_callback(self):
        if self.popup is None:
            self.popup = ProjectCreationPopup(self.root)
            try:
                self.popup.set_validation(
                    self.validation_trigger, self.validation_command)
            except AttributeError:
                pass

    def popup_create_handler(self, *args):
        name = self.popup.get_name()
        self.popup.close()
        self.popup = None
        self.projects_combox.set(name)
        self.combobox_return()

    def popup_cancel_handler(self, *args):
        self.popup.close()
        self.popup = None

    def delete_project(self):
        selection = self.get_selection()
        if selection is not None:
            self.root.event_generate(VEV_PROJ_DELETE, data=selection)

    def grid(self, *, row, column,
             rowspan=1, columnspan=1, sticky='', **kwargs):
        self.frame.grid(row=row, column=column, sticky=sticky,
                        rowspan=rowspan, columnspan=columnspan,
                        **kwargs)

    def att_buttons_state(self, *args):
        if self.get_selection() is None:
            self.delete_btn.state(['disabled'])
            self.create_btn.state(['!disabled'])
        else:
            self.delete_btn.state(['!disabled'])
            self.create_btn.state(['disabled'])


VEV_PROJECT_POPUP_CREATE = '<<ProjectPopupCreate>>'
VEV_PROJECT_POPUP_CANCEL = '<<ProjectPopupCancel>>'

class ProjectCreationPopup:

    def __init__(self, parent):
        self.parent = parent
        self.root = parent.winfo_toplevel()
        # Popup window
        self.popup = tk.Toplevel(parent)
        self.popup.title('Project creation')
        self.popup.rowconfigure(0, weight=1)
        self.popup.columnconfigure(0, weight=1)
        # Frame
        self.frame = ttk.Frame(self.popup)
        self.frame.grid(row=0, column=0, sticky='wnes', padx=2, pady=2)
        self.frame.columnconfigure((0, 1), weight=1, uniform=True)
        self.frame.configure(borderwidth=5, relief='groove')
        # Label
        self.lbl = ttk.Label(
            self.frame, text='Project name:', padding=1, anchor='center')
        self.lbl.grid(
            row=0, column=0, columnspan=2, sticky='wnes', pady=(0, 5))
        # Entry
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(
            self.frame, width=45, textvariable=self.name_var)
        self.name_entry.grid(
            row=1, column=0, columnspan=2, sticky='wnes', pady=(0, 5))
        # Cancel button
        self.cancel_btn = ttk.Button(
            self.frame, text='Cancel', command=self.cancel_callback)
        self.cancel_btn.grid(row=2, column=0)
        # Create button
        self.create_btn = ttk.Button(
            self.frame, text='Create',
            command=self.create_callback, default='active')
        self.create_btn.grid(row=2, column=1)
        # Handle popup destroy
        self.popup.protocol('WM_DELETE_WINDOW', self.cancel_callback)

    def create_callback(self):
        self.root.event_generate(VEV_PROJECT_POPUP_CREATE)

    def cancel_callback(self):
        self.root.event_generate(VEV_PROJECT_POPUP_CANCEL)

    def close(self):
        self.popup.destroy()

    def set_validation(self, val_trigger, val_command):
        self.name_entry.configure(
            validate=val_trigger, validatecommand=val_command)

    def get_name(self):
        return self.name_var.get()
