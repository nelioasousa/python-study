import tkinter as tk
import tkinter.ttk as ttk

from model import valid_project_name

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
#
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
#
# Progress section:
#   Functionality:
#     Learned percentage
#     Last studied
#     Number of cards reviewed today
#     Number of cards learned today
#   Widgets:
#     Static labels for descriptions
#     Var labels for progress informations
#   Behaviors:
#     None
#
# Card screen section:
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
#
# Configuration section:
#   Functionality:
#     Change priority scoring
#     Set normal/quiz mode
#   Widgets:
#     Entries for setting variables weights
#     Labels describing variables
#     Checkbutton to set quiz mode
#   Behaviors:
#     Setting quiz mode changes next card functionality
#     Changing weights recalculates cards priority scores


VEV_PROJ_SET = '<<ProjectSet>>'
VEV_PROJ_ENTRY_CREATE = '<<ProjectEntryCreate>>'
VEV_PROJ_POPUP_CREATE = '<<ProjectPopupCreate>>'
VEV_PROJ_DELETE = '<<ProjectDelete>>'

def entry_validator(entry: str):
    return (valid_project_name(entry)
            and entry == ' '.join(('%s_' %entry).split())[:-1])

class ProjectsSec:

    def __init__(self, root):
        self.root = root
        # Section frame
        self.frame = ttk.Frame(root, padding=5)
        # Project selection combobox
        self._combox_entry = tk.StringVar()
        self._combox_entry.trace_add('write', self.att_buttons_state)
        validator = (self.root.register(entry_validator), '%P')
        self.projects_combox = ttk.Combobox(
            self.frame, height=5, state='normal',
            textvariable=self._combox_entry,
            validate='key', validatecommand=validator)
        self.projects_combox.grid(row=0, column=1, columnspan=3)
        self.projects_combox.bind('<Return>', self.combobox_return)
        self.projects_combox.bind('<<ComboboxSelected>>',
                                  self.combobox_selection)
        # Dummy/Default function to list projects
        self.set_post_command()
        # Combobox label
        self.project_lbl = ttk.Label(
            self.frame, text='Project:', anchor='center', padding=1, width=9)
        self.project_lbl.grid(row=0, column=0)
        # New project button
        self.create_btn = ttk.Button(
            self.frame, text='New', command=self.create_project)
        self.create_btn.grid(
            row=1, column=0, columnspan=2,
            sticky='we', padx=(0, 1), pady=(2, 0))
        # Delete project button
        self.delete_btn = ttk.Button(
            self.frame, text='Delete', command=self.delete_project)
        self.delete_btn.grid(
            row=1, column=2, columnspan=2,
            sticky='we', padx=(1, 0), pady=(2, 0))

    def set_post_command(self, post_command=None):
        self._post_command = tuple if post_command is None else post_command
        def post_wrapper():
            values = self._post_command()
            self.projects_combox.configure(values=values)
        self.projects_combox.configure(postcommand=post_wrapper)

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

    def combobox_return(self, _event=None):
        entry = self.get_selection()
        if entry in self.get_listed_projects():
            root.event_generate(VEV_PROJ_SET, data=entry)
        else:
            root.event_generate(VEV_PROJ_ENTRY_CREATE, data=entry)

    def combobox_selection(self, _event=None):
        self.projects_combox.selection_clear()  # Clear text selection
        root.event_generate(VEV_PROJ_SET, data=self.get_selection())

    def create_project(self):
        root.event_generate(VEV_PROJ_POPUP_CREATE)

    def delete_project(self):
        root.event_generate(VEV_PROJ_DELETE, data=self.get_selection())
    
    def grid(self, *, row, column, rowspan=1, columnspan=1, **kwargs):
        self.frame.grid(row=row, column=column, rowspan=rowspan,
                        columnspan=columnspan, **kwargs)
    
    def att_buttons_state(self, *args):
        if self.get_selection() is None:
            self.delete_btn.state(['disabled'])
            self.create_btn.state(['!disabled'])
        else:
            self.delete_btn.state(['!disabled'])
            self.create_btn.state(['disabled'])


root = tk.Tk()
projects = ProjectsSec(root)
projects.grid(row=0, column=0)

def get_values():
    return ['Opt1', 'Opt2']

projects.set_post_command(get_values)

projects.set_working_project('Opt1')  # Works
projects.set_working_project('Test')  # Do nothing

root.mainloop()
