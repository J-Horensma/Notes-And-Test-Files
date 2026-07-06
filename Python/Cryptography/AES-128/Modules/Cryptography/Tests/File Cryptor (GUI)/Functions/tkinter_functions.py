from os.path import isdir, expanduser
from tkinter import Tk, messagebox, filedialog, simpledialog

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
#1.) OPTIONALLY ACCEPTS PROMPT TITLE AND PROMPT PATH STRINGS
#2.) PROMPTS THE USER TO SELECT A FOLDER PATH
#3.) RETURNS THE FULL FOLDER PATH, THAT WAS CHOSEN, AS A STRING
def folder_path_prompt(PROMPT_TITLE=None, PROMPT_PATH=None):
    if PROMPT_TITLE is not None and not isinstance(PROMPT_TITLE, str):
        raise TypeError('[TypeError]\nFunction: "folder_path_prompt()"\nThe supplied prompt title parameter, was not a string type.')
    elif PROMPT_PATH is not None and not isdir(PROMPT_PATH):
        raise NotADirectoryError('[NotADirectoryError]\nFunction: "folder_path_prompt()"\nThe supplied prompt path parameter, was not a path to an existing folder.')
    PROMPT_TITLE = 'Choose A Folder' if PROMPT_TITLE is None else PROMPT_TITLE
    PROMPT_PATH = expanduser('~') if PROMPT_PATH is None else PROMPT_PATH
    while True:
        PATH = filedialog.askdirectory(
            title=PROMPT_TITLE, 
            initialdir=PROMPT_PATH
        )
        if not PATH:
            messagebox.showerror('Error!', 'A folder, must be chosen.')
            continue
        else:
            break
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
    while True:
        PATH = filedialog.askopenfilename(
            title=PROMPT_TITLE,
            initialdir=PROMPT_PATH,
            filetypes=FILE_TYPES
        )
        if not PATH:
            messagebox.showerror('Error!', 'A file, must be chosen.')
            continue
        else:
            break
    return PATH

#THIS FUNCTION:
#1.) REQUIRES A "tkinter.Tk()" CLASS
#2.) OPTIONALLY ACCEPTS A PROMPT TITLE STRING
#3.) PROMPTS THE USER TO INPUT A STRING
#4.) RETURNS THE STRING, THAT WAS ENTERED, AS A STRING
def input_string_prompt(WINDOW, PROMPT_TITLE=None):
    if not isinstance(WINDOW, Tk):
        raise TypeError('[TypeError]\nFunction: "input_string_prompt()"\nThe supplied window parameter, was not a valid "tkinter.Tk()" class.')
    elif PROMPT_TITLE is not None and not isinstance(PROMPT_TITLE, str):
        raise TypeError('[TypeError]\nFunction: "input_string_prompt()"\nThe supplied prompt title parameter, was not a string type.')
    PROMPT_TITLE = 'Enter A String:' if PROMPT_TITLE is None else PROMPT_TITLE
    while True:
        STRING = simpledialog.askstring(
            title=PROMPT_TITLE,
            prompt=PROMPT_TITLE,
            initialvalue='',
            parent=WINDOW
        )
        if not STRING:
            messagebox.showerror('Error!', 'A string, must be entered.')
            continue
        else:
            break
    return STRING