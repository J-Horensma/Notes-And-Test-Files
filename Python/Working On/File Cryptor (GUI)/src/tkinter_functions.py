from os.path import isdir, expanduser
from tkinter import Tk, ttk, Toplevel, Frame, Label, StringVar, Entry, Button, filedialog

#THIS FUNCTION:
#1.) REQUIRES A "tkinter.Tk()" ROOT WINDOW CLASS
#2.) RETURNS THE WIDTH AND HEIGHT, OF THE DEVICE SCREEN, AS A LIST
def get_device_screen_size(ROOT_WINDOW):
    if not isinstance(ROOT_WINDOW, Tk):
        raise TypeError('[TypeError]\nFunction: "get_screen_size()"\nThe root window parameter, must be a "tkinter.Tk()" class.')
    ROOT_WINDOW.update_idletasks()
    SCREEN_WIDTH = ROOT_WINDOW.winfo_screenwidth()
    SCREEN_HEIGHT = ROOT_WINDOW.winfo_screenheight()
    return [SCREEN_WIDTH, SCREEN_HEIGHT]

#THIS FUNCTION:
#1.) REQUIRES A "tkinter.Tk()" ROOT WINDOW CLASS
#2.) CLEARS ALL WIDGETS, IN THE ROOT WINDOW
def clear_root_window(ROOT_WINDOW):
    if not isinstance(ROOT_WINDOW, Tk):
        raise TypeError('[TypeError]\nFunction: "clear_root_window()"\nThe root window parameter, must be a "tkinter.Tk()" class.')
    ROOT_WINDOW.update_idletasks()
    for WIDGET in ROOT_WINDOW.winfo_children():
        WIDGET.destroy()

#THIS FUNCTION:
#1.) REQUIRES A "tkinter.Tk()" ROOT WINDOW CLASS, A WINDOW WIDTH INTEGER, AND A WINDOW HEIGHT INTEGER
#2.) CENTERS THE WINDOW, WITH A WINDOW SIZE, OF THE SUPPLIED DIMENTIONS
def center_root_window(ROOT_WINDOW, ROOT_WINDOW_WIDTH, ROOT_WINDOW_HEIGHT):
    if not isinstance(ROOT_WINDOW, Tk):
        raise TypeError('[TypeError]\nFunction: "center_root_window()"\nThe root window parameter, must be a "tkinter.Tk()" class.')
    elif not isinstance(ROOT_WINDOW_WIDTH, int):
        raise TypeError('[TypeError]\nFunction: "center_root_window()"\nThe root window width parameter, was not an integer.')
    elif not isinstance(ROOT_WINDOW_HEIGHT, int):
        raise TypeError('[TypeError]\nFunction: "center_root_window()"\nThe root window height parameter, was not an integer.')
    ROOT_WINDOW.update_idletasks()
    X = (ROOT_WINDOW.winfo_screenwidth() - ROOT_WINDOW_WIDTH) // 2
    Y = (ROOT_WINDOW.winfo_screenheight() - ROOT_WINDOW_HEIGHT) // 2
    ROOT_WINDOW.geometry(f'{ROOT_WINDOW_WIDTH}x{ROOT_WINDOW_HEIGHT}+{X}+{Y}')

#THIS FUNCTION:
#1.) REQUIRES A "tkinter.Tk()" ROOT WINDOW CLASS AND A LIST OF DROPDOWN MENU OPTIONS
#2.) ACCEPTS OPTIONAL PROMPT TITLE AND PROMPT MESSAGE STRINGS
#3.) IF NO PROMPT TITLE AND/OR PROMPT MESSAGE STRING/S ARE SUPPLIED, DEFAULT/S IS/ARE SET
#4.) PROMPTS THE USER TO SELECT A DROPDOWN MENU OPTION
#5.) RETURNS THE USER-SELECTED OPTION, AS A STRING, OR "None", IF THE WINDOW IS CLOSED OR CANCELLED
def dropdown_menu_prompt(ROOT_WINDOW, DROPDOWN_MENU_OPTIONS, PROMPT_TITLE=None, PROMPT_MESSAGE=None):
    if not isinstance(ROOT_WINDOW, Tk):
        raise TypeError('[TypeError]\nFunction: "dropdown_menu_prompt()"\nThe root window parameter, must be a "tkinter.Tk()" class.')
    elif DROPDOWN_MENU_OPTIONS is not None and not isinstance(DROPDOWN_MENU_OPTIONS, list):
        raise TypeError('[TypeError]\nFunction: "dropdown_menu_prompt()"\nThe dropdown menu options parameter, must be a list type.')
    elif PROMPT_TITLE is not None and not isinstance(PROMPT_TITLE, str):
        raise TypeError('[TypeError]\nFunction: "dropdown_menu_prompt()"\nThe prompt title parameter, must be a string type.')
    elif PROMPT_MESSAGE is not None and not isinstance(PROMPT_MESSAGE, str):
        raise TypeError('[TypeError]\nFunction: "dropdown_menu_prompt()"\nThe prompt message parameter, must be a string type.')
    PROMPT_TITLE = 'Select An Option:' if PROMPT_TITLE is None else PROMPT_TITLE
    PROMPT_MESSAGE = 'Select An Option:' if PROMPT_MESSAGE is None else PROMPT_MESSAGE
    SELECTED_DROPDOWN_MENU_VALUE = None
    def close_window():
        DROPDOWN_MENU_WINDOW.destroy()
    def process_selected_value():
        nonlocal SELECTED_DROPDOWN_MENU_VALUE
        SELECTED_DROPDOWN_MENU_VALUE = DROPDOWN_MENU.get()
        DROPDOWN_MENU_WINDOW.destroy()
    #CREATE A NEW WINDOW, SEPARATE FROM THE ROOT WINDOW
    DROPDOWN_MENU_WINDOW = Toplevel(ROOT_WINDOW)
    #TRIGGER A CLOSE FUNCTION, WHEN THE "X" BUTTON, IS CLICKED
    DROPDOWN_MENU_WINDOW.protocol('WM_DELETE_WINDOW', close_window)
    DROPDOWN_MENU_WINDOW.title(PROMPT_TITLE)
    #PREVENT RESIZING WIDTH AND HEIGHT, OF THE WINDOW
    DROPDOWN_MENU_WINDOW.resizable(False, False)
    #SEND ALL MOUSE AND KEYBOARD EVENTS, TO THIS WINDOW
    DROPDOWN_MENU_WINDOW.grab_set()
    #WINDOW WIDGETS (START)
    #----------------------
    MESSAGE_LABEL = Label(DROPDOWN_MENU_WINDOW, text=PROMPT_MESSAGE, font=('Times New Roman', 18, 'bold'))
    MESSAGE_LABEL.pack(padx=10, pady=10)
    DROPDOWN_MENU = ttk.Combobox(DROPDOWN_MENU_WINDOW, values=DROPDOWN_MENU_OPTIONS, state='readonly', font=('Times New Roman', 18, 'bold'))
    DROPDOWN_MENU.pack(fill='both', padx=10)
    DROPDOWN_MENU.current(0)
    CANCEL_BUTTON = Button(DROPDOWN_MENU_WINDOW, text='Cancel', font=('Times New Roman', 18, 'bold'), command=close_window)
    CANCEL_BUTTON.pack(side='left', padx=10, pady=10)
    CONFIRM_BUTTON = Button(DROPDOWN_MENU_WINDOW, text='Confirm', font=('Times New Roman', 18, 'bold'), command=process_selected_value)
    CONFIRM_BUTTON.pack(side='right', padx=10, pady=10)
    #--------------------
    #WINDOW WIDGETS (END)
    #WAIT UNTIL THE WINDOW IS DESTROYED, BEFORE, RETURNING
    DROPDOWN_MENU_WINDOW.wait_window()
    return SELECTED_DROPDOWN_MENU_VALUE

#THIS FUNCTION:
#1.) REQUIRES "tkinter.Entry()" AND "tkinter.Button()" WIDGETS
#2.) SHOWS/HIDES THE INPUT VALUE OF THE "tkinter.Entry()" WIDGET AND CHANGES THE TEXT, OF THE SHOW/HIDE BUTTON
def toggle_input_visibility(ENTRY_WIDGET, VISIBILITY_BUTTON):
    if not isinstance(ENTRY_WIDGET, Entry):
        raise TypeError('[TypeError]\nFunction: "toggle_input_visibility()"\nThe entry widget parameter, must be a "tkinter.Entry()" class.')
    elif not isinstance(VISIBILITY_BUTTON, Button):
        raise TypeError('[TypeError]\nFunction: "toggle_input_visibility()"\nThe visibility button parameter, must be a "tkinter.Button()" class.')
    if ENTRY_WIDGET.cget('show') == '':
        ENTRY_WIDGET.config(show='*')
        VISIBILITY_BUTTON.config(text='Show')
    else:
        ENTRY_WIDGET.config(show='')
        VISIBILITY_BUTTON.config(text='Hide')

#THIS FUNCTION:
#1.) REQUIRES A "tkinter.Tk()" ROOT WINDOW CLASS
#2.) ACCEPTS OPTIONAL PROMPT TITLE AND PROMPT MESSAGE STRINGS
#3.) IF NO PROMPT TITLE AND/OR PROMPT MESSAGE STRING/S ARE SUPPLIED, DEFAULT/S IS/ARE SET
#4.) PROMPTS THE USER TO INPUT A PASSWORD
#5.) ALLOWS THE USER TO SHOW/HIDE, THE INPUT
def password_input_prompt(ROOT_WINDOW, PROMPT_TITLE=None, PROMPT_MESSAGE=None):
    if not isinstance(ROOT_WINDOW, Tk):
        raise TypeError('[TypeError]\nFunction: "password_input_prompt()"\nThe root window parameter, must be a "tkinter.Tk()" class.')
    elif PROMPT_TITLE is not None and not isinstance(PROMPT_TITLE, str):
        raise TypeError('[TypeError]\nFunction: "password_input_prompt()"\nThe prompt title parameter, must be a string type.')
    elif PROMPT_MESSAGE is not None and not isinstance(PROMPT_MESSAGE, str):
        raise TypeError('[TypeError]\nFunction: "password_input_prompt()"\nThe prompt message parameter, must be a string type.')
    PROMPT_TITLE = 'Enter A Password:' if PROMPT_TITLE is None else PROMPT_TITLE
    PROMPT_MESSAGE = 'Enter A Password:' if PROMPT_MESSAGE is None else PROMPT_MESSAGE
    PASSWORD_INPUT_VALUE = None
    def close_window():
        PASSWORD_INPUT_WINDOW.destroy()
    def process_password_input():
        nonlocal PASSWORD_INPUT_VALUE
        PASSWORD_INPUT_VALUE = PASSWORD_INPUT.get()
        PASSWORD_INPUT_WINDOW.destroy()
    #CREATE A NEW WINDOW, SEPARATE FROM THE ROOT WINDOW
    PASSWORD_INPUT_WINDOW = Toplevel(ROOT_WINDOW)
    #TRIGGER A CLOSE FUNCTION, WHEN THE "X" BUTTON, IS CLICKED
    PASSWORD_INPUT_WINDOW.protocol('WM_DELETE_WINDOW', close_window)
    PASSWORD_INPUT_WINDOW.title(PROMPT_TITLE)
    #PREVENT RESIZING WIDTH AND HEIGHT, OF THE WINDOW
    PASSWORD_INPUT_WINDOW.resizable(False, False)
    #SEND ALL MOUSE AND KEYBOARD EVENTS, TO THIS WINDOW
    PASSWORD_INPUT_WINDOW.grab_set()
    #WINDOW WIDGETS (START)
    #----------------------
    MESSAGE_LABEL = Label(PASSWORD_INPUT_WINDOW, text=PROMPT_MESSAGE, font=('Times New Roman', 18, 'bold'))
    MESSAGE_LABEL.pack(padx=10, pady=10)
    VISIBILITY = StringVar()
    CENTERED_FRAME = Frame(PASSWORD_INPUT_WINDOW)
    CENTERED_FRAME.pack(padx=10, anchor='center')
    PASSWORD_INPUT = Entry(CENTERED_FRAME, textvariable=VISIBILITY, show='*', font=('Times New Roman', 26, 'bold'))
    PASSWORD_INPUT.pack(padx=(0, 10), side='left')
    VISIBILITY_BUTTON = Button(CENTERED_FRAME, text='Show', font=('Times New Roman', 18, 'bold'), command=lambda: toggle_input_visibility(PASSWORD_INPUT, VISIBILITY_BUTTON))
    VISIBILITY_BUTTON.pack(side='left')
    CANCEL_BUTTON = Button(PASSWORD_INPUT_WINDOW, text='Cancel', font=('Times New Roman', 18, 'bold'), command=close_window)
    CANCEL_BUTTON.pack(side='left', padx=10, pady=10)
    CONFIRM_BUTTON = Button(PASSWORD_INPUT_WINDOW, text='Confirm', font=('Times New Roman', 18, 'bold'), command=process_password_input)
    CONFIRM_BUTTON.pack(side='right', padx=10, pady=10)
    #--------------------
    #WINDOW WIDGETS (END)
    #WAIT UNTIL THE WINDOW IS DESTROYED, BEFORE, RETURNING
    PASSWORD_INPUT_WINDOW.wait_window()
    return PASSWORD_INPUT_VALUE

#THIS FUNCTION:
#1.) ACCEPTS OPTIONAL PROMPT TITLE AND PROMPT PATH STRINGS
#2.) PROMPTS THE USER TO CHOOSE A FOLDER PATH
#3.) RETURNS THE FULL FOLDER PATH, THAT WAS CHOSEN, AS A STRING, OR "None", IF THE WINDOW IS CLOSED OR CANCELLED
def folder_path_prompt(PROMPT_TITLE=None, PROMPT_PATH=None):
    if PROMPT_TITLE is not None and not isinstance(PROMPT_TITLE, str):
        raise TypeError('[TypeError]\nFunction: "folder_path_prompt()"\nThe prompt title parameter, was not a string type.')
    elif PROMPT_PATH is not None and not isdir(PROMPT_PATH):
        raise NotADirectoryError('[NotADirectoryError]\nFunction: "folder_path_prompt()"\nThe prompt path parameter, must be a path to an existing folder.')
    PROMPT_TITLE = 'Choose A Folder:' if PROMPT_TITLE is None else PROMPT_TITLE
    PROMPT_PATH = expanduser('~') if PROMPT_PATH is None else PROMPT_PATH
    PATH = filedialog.askdirectory(
        title=PROMPT_TITLE,
        initialdir=PROMPT_PATH
    )
    if not PATH:
        PATH = None
    return PATH

#THIS FUNCTION:
#1.) ACCEPTS OPTIONAL PROMPT TITLE AND PROMPT PATH STRINGS
#2.) ACCEPTS AN OPTIONAL FILE TYPES LIST
#FORMAT: [('Text Files', '*.txt'), ('Python Files', '*.py')]
#3.) PROMPTS THE USER TO CHOOSE A FILE PATH
#4.) RETURNS THE FULL FILE PATH, THAT WAS CHOSEN, AS A STRING, OR "None", IF THE WINDOW IS CLOSED OR CANCELLED
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
    if not PATH:
        PATH = None
    return PATH