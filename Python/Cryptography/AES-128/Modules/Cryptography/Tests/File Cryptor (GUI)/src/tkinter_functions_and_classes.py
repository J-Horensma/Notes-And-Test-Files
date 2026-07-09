from os.path import isdir, expanduser
from tkinter import Tk, Label, StringVar, Entry, Button, filedialog, simpledialog

#THIS FUNCTION:
#1.) REQUIRES A "tkinter.Tk()" CLASS
#2.) RETURNS THE WIDTH AND HEIGHT OF THE DEVICE SCREEN, AS A LIST
def get_screen_size(WINDOW):
    if not isinstance(WINDOW, Tk):
        raise TypeError('[TypeError]\nFunction: "get_screen_size()"\nThe supplied window parameter, was not a valid "tkinter.Tk()" class.')
    WINDOW.update_idletasks()
    SCREEN_WIDTH = WINDOW.winfo_screenwidth()
    SCREEN_HEIGHT = WINDOW.winfo_screenheight()
    return [SCREEN_WIDTH, SCREEN_HEIGHT]

#THIS FUNCTION:
#1.) REQUIRES A "tkinter.Tk()" CLASS
#2.) CLEARS ALL WIDGETS, IN THE WINDOW
def clear_window(WINDOW):
    if not isinstance(WINDOW, Tk):
        raise TypeError('[TypeError]\nFunction: "clear_window()"\nThe supplied window parameter, was not a valid "tkinter.Tk()" class.')
    WINDOW.update_idletasks()
    for WIDGET in WINDOW.winfo_children():
        WIDGET.destroy()

#THIS FUNCTION:
#1.) REQUIRES A "tkinter.Tk()" CLASS, WINDOW WIDTH, AND WINDOW HEIGHT INTEGERS
#2.) CENTERS THE WINDOW, WITH A WINDOW SIZE, OF THE SUPPLIED DIMENTIONS
def center_window(WINDOW, WINDOW_WIDTH, WINDOW_HEIGHT):
    if not isinstance(WINDOW, Tk):
        raise TypeError('[TypeError]\nFunction: "center_window()"\nThe supplied window parameter, was not a valid "tkinter.Tk()" class.')
    elif not isinstance(WINDOW_WIDTH, int):
        raise TypeError('[TypeError]\nFunction: "center_window()"\nThe supplied window width parameter, was not an integer.')
    elif not isinstance(WINDOW_HEIGHT, int):
        raise TypeError('[TypeError]\nFunction: "center_window()"\nThe supplied window height parameter, was not an integer.')
    WINDOW.update_idletasks()
    X = (WINDOW.winfo_screenwidth() - WINDOW_WIDTH) // 2
    Y = (WINDOW.winfo_screenheight() - WINDOW_HEIGHT) // 2
    WINDOW.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{X}+{Y}')

#THIS FUNCTION:
#1.) OPTIONALLY ACCEPTS A PROMPT TITLE STRING
#2.) PROMPTS THE USER TO SELECT A FOLDER PATH
#3.) RETURNS THE FULL FOLDER PATH, THAT WAS CHOSEN, AS A STRING
def folder_path_prompt(PROMPT_TITLE=None):
    if PROMPT_TITLE is not None and not isinstance(PROMPT_TITLE, str):
        raise TypeError('[TypeError]\nFunction: "folder_path_prompt()"\nThe supplied prompt title parameter, was not a string type.')
    PROMPT_TITLE = 'Choose A Folder' if PROMPT_TITLE is None else PROMPT_TITLE
    PATH = filedialog.askdirectory(
        title=PROMPT_TITLE
    )
    return PATH

#THIS FUNCTION:
#1.) OPTIONALLY ACCEPTS PROMPT TITLE AND PROMPT PATH STRINGS
#2.) OPTIONALLY ACCEPTS A FILE TYPES LIST
#FORMAT: [('Text Files', '*.txt'), ('Python Files', '*.py')]
#3.) PROMPTS THE USER TO CHOOSE A FILE PATH
#4.) RETURNS THE FULL FILE PATH, THAT WAS CHOSEN, AS A STRING
def file_path_prompt(PROMPT_TITLE=None, PROMPT_PATH=None, FILE_TYPES=None):
    if PROMPT_TITLE is not None and not isinstance(PROMPT_TITLE, str):
        raise TypeError('[TypeError]\nFunction: "file_path_prompt()"\nThe supplied prompt title parameter, was not a string type.')
    elif PROMPT_PATH is not None and not isdir(PROMPT_PATH):
        raise NotADirectoryError('[NotADirectoryError]\nFunction: "file_path_prompt()"\nThe supplied prompt path parameter, was not a path to an existing folder.')
    elif FILE_TYPES is not None and not isinstance(FILE_TYPES, list):
        raise TypeError('[TypeError]\nFunction: "file_path_prompt()"\nThe supplied file types parameter, was not a list.')
    PROMPT_TITLE = 'Choose A File' if PROMPT_TITLE is None else PROMPT_TITLE
    PROMPT_PATH = expanduser('~') if PROMPT_PATH is None else PROMPT_PATH
    FILE_TYPES = [('All Files', '*.*')] if FILE_TYPES is None else FILE_TYPES
    PATH = filedialog.askopenfilename(
        title=PROMPT_TITLE,
        initialdir=PROMPT_PATH,
        filetypes=FILE_TYPES
    )
    return PATH

#THIS CLASS:
#1.) REQUIRES A "tkinter.Tk()" CLASS
#2.) PROMPTS THE USER TO INPUT A PASSWORD, WITH AN INPUT PROMPT, CONTAINING A TOGGLE VISIBILITY BUTTON
#3.) RETURNS THE PASSWORD, THAT WAS ENTERED, AS A STRING, WHEN CALLED WITH "input_password_prompt(tkinter.Tk()).value"
class input_password_prompt(simpledialog.Dialog):
    def body(self, WINDOW):
        self.value = ''
        self.geometry(f'290x75')
        self.title('Enter A Password: ')
        Label(WINDOW, text='Enter A Password: ').grid(row=0, column=0)
        self.VISIBILITY = StringVar()
        self.PASSWORD_INPUT = Entry(WINDOW, textvariable=self.VISIBILITY, show='*')
        self.PASSWORD_INPUT.grid(row=0, column=1)
        self.VISIBILITY_BUTTON = Button(WINDOW, text='Show', command=self.toggle_visibility)
        self.VISIBILITY_BUTTON.grid(row=0, column=2, padx=10)
        return self.PASSWORD_INPUT
    def toggle_visibility(self):
        self.PASSWORD_INPUT.config(show='' if self.PASSWORD_INPUT.cget('show') else '*')
        self.VISIBILITY_BUTTON.config(text='Show' if self.PASSWORD_INPUT.cget('show') else 'Hide')
    def apply(self):
        self.value = self.VISIBILITY.get()
