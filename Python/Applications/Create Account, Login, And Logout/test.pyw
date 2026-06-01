from os.path import exists, dirname
from re import search
import tkinter as tk
from tkinter import  Tk, Frame, Label, Entry, Button, Checkbutton, messagebox, filedialog
from Functions.sqlite3_account_functions import any_empty, table_exists, create_table, select_row_values, get_hash_and_salt, aes_128_encrypt, insert_row_values, aes_128_decrypt

#THIS FUNCTION:
#1.) CLEARS ALL WIDGETS, IN A WINDOW
def clear_window():
    for WIDGET in ROOT.winfo_children():
        WIDGET.destroy()

#THIS FUNCTION:
#1.) REQUIRES DATABASE FILE PATH AND DATABASE TABLE NAME STRINGS
#2.) CHECKS FOR ERRORS, IN EITHER OF THE STRINGS
#3.) DISPLAYS ANY NECCESSARY WINDOWS, TO FIX ERRORS
def db_error_check(DB_FILE_PATH, DB_TABLE_NAME):
    if not DB_FILE_PATH.strip():
        messagebox.showerror('Error: Database File Path, Not Set!', 'The database filepath variable, was empty and must be set.\nThe application will close.')
        exit(1)
    elif not exists(DB_FILE_PATH):
        while True:
            messagebox.showerror('Error: Database File, Not Found!', f'The database file:\n"{DB_FILE_PATH}",\nwas not found, you can create it, in the next window.')
            FILE_PATH = filedialog.asksaveasfilename(
            initialdir = dirname(DB_FILE_PATH),
            title = 'Create A Database File',
            filetypes = [('sqlite or db', ('*.sqlite', '*.db')),],
            defaultextension = '.db'
            )
            if not FILE_PATH:
                exit(1)
            else:
                with open(FILE_PATH, 'w') as FILE:
                    FILE.write()
                break
    if not DB_TABLE_NAME.strip():
        messagebox.showerror('Error: Database Table Name, Not Set!', 'The database table name variable, was empty and must be set.\nThe application will close.')
        exit(1)
    elif not table_exists(DB_FILE_PATH, DB_TABLE_NAME):
        messagebox.showerror('Error: Table Not Found!', f'The database table: "{DB_TABLE_NAME}",\nwas not found and will be created, in the database.')
        COLUMNS_INFO = '''
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash BLOB NOT NULL,
        salt BLOB NOT NULL
        '''
        create_table(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS_INFO)
        messagebox.showinfo('Database Table, Successfully Created', f'The database table: "{DB_TABLE_NAME}",\nwas created, in the database.')

def create_account(DB_FILE_PATH, DB_TABLE_NAME, USERNAME_INPUT, PASSWORD_INPUT):
        db_error_check(DB_FILE_PATH, DB_TABLE_NAME)
        if any_empty([USERNAME_INPUT.get(), PASSWORD_INPUT.get()]):
            messagebox.showerror('Error: Empty Input Field/s!', 'One or more field/s, were empty.')
            return
        elif not bool(search(r'[A-Za-z\d\S]{15,}', PASSWORD_INPUT.get())):
            messagebox.showerror('Error: Insecure Password!', 'The password, must be at least 15 characters long and include lowercase letter/s, uppercase letter/s, number/s, and symbol/s.')
            return
        elif select_row_values(DB_FILE_PATH, DB_TABLE_NAME, 'username', 'username', USERNAME_INPUT.get()):
            messagebox.showerror('Error: Account Exists!', f'An account, already exists for the username: "{USERNAME_INPUT.get()}".')
            return
        else:
            PASSWORD_HASH_BYTES, SALT_BYTES = get_hash_and_salt(PASSWORD_INPUT.get())
            del PASSWORD_INPUT
            ENCRYPTED_PASSWORD_HASH_BYTES = aes_128_encrypt(PASSWORD_HASH_BYTES, PASSWORD_HASH_BYTES)
            COLUMNS = 'username, password_hash, salt'
            ROW_VALUES = [USERNAME_INPUT.get(), ENCRYPTED_PASSWORD_HASH_BYTES, SALT_BYTES]
            insert_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_VALUES)
            messagebox.showinfo('Account, Successfully Created', f'An account, for {USERNAME_INPUT.get()},\nwas successfully created!')

def login(DB_FILE_PATH, DB_TABLE_NAME, USERNAME_INPUT, PASSWORD_INPUT):
    db_error_check(DB_FILE_PATH, DB_TABLE_NAME)
    if any_empty([USERNAME_INPUT.get(), PASSWORD_INPUT.get()]):
        messagebox.showerror('Error: Invalid Username Or Password', 'One or more field/s, were empty.')
        return
    elif not select_row_values(DB_FILE_PATH, DB_TABLE_NAME, 'username', 'username', USERNAME_INPUT.get()):
        messagebox.showerror('Error: Invalid Username Or Password', 'The username or password, was incorrect.')
        return
    else:
        ENCRYPTED_PASSWORD_HASH_BYTES, SALT_BYTES = select_row_values(DB_FILE_PATH, DB_TABLE_NAME, 'password_hash, salt', 'username', USERNAME_INPUT.get())
        PASSWORD_HASH_BYTES, SALT_BYTES = get_hash_and_salt(PASSWORD_INPUT.get(), SALT_BYTES)
        if not aes_128_decrypt(ENCRYPTED_PASSWORD_HASH_BYTES, PASSWORD_HASH_BYTES):
            messagebox.showerror('Error: Invalid Username Or Password!', 'The username or password, was incorrect.')
            PASSWORD_INPUT.delete(0, 'end')
            PASSWORD_INPUT.focus_set()
            return
        else:
            del PASSWORD_INPUT
            home_page_window(DB_FILE_PATH, DB_TABLE_NAME, USERNAME_INPUT.get(), aes_128_decrypt(ENCRYPTED_PASSWORD_HASH_BYTES, PASSWORD_HASH_BYTES))
    
def create_account_window(DB_FILE_PATH, DB_TABLE_NAME):
    def toggle_password_visibility():
        if PASSWORD_INPUT.cget('show') == '':
            PASSWORD_INPUT.config(show='*')
            TOGGLE_VISIBILITY.config(text='Show password')
        else:
            PASSWORD_INPUT.config(show='')
            TOGGLE_PASSWORD_VISIBILITY.config(text='Hide password')
    clear_window()
    ROOT.update_idletasks()
    BORDER_FRAME = Frame(ROOT, bg='#B0AFB3', padx=3, pady=3)
    BORDER_FRAME.pack(expand=True)
    INNER_FRAME = Frame(BORDER_FRAME, bg='#cdcdd4', padx=50, pady=50)
    INNER_FRAME.pack(expand=True)
    USERNAME_LABEL = Label(INNER_FRAME, text='Username:', bg='#cdcdd4', font=('Times New Roman', 22, 'bold'))
    USERNAME_LABEL.pack(expand=True)
    USERNAME_INPUT = Entry(INNER_FRAME, font=('Times New Roman', 28))
    USERNAME_INPUT.pack(expand=True)
    PASSWORD_LABEL = Label(INNER_FRAME, text='Password:', bg='#cdcdd4', font=('Times New Roman', 22, 'bold'))
    PASSWORD_LABEL.pack(expand=True)
    PASSWORD_INPUT = Entry(INNER_FRAME, font=('Times New Roman', 28), show='*')
    PASSWORD_INPUT.pack(expand=True)
    TOGGLE_PASSWORD_VISIBILITY = Checkbutton(INNER_FRAME, text='Show Password', bg='#cdcdd4', command=toggle_password_visibility)
    TOGGLE_PASSWORD_VISIBILITY.pack(side='left', pady=10)
    SUBMIT_BUTTON = Button(INNER_FRAME, text='Submit', bg='#cdcdd4', font=('Times New Roman', 18, 'bold'), relief='raised', command=lambda: create_account(DB_FILE_PATH, DB_TABLE_NAME, USERNAME_INPUT, PASSWORD_INPUT))
    SUBMIT_BUTTON.pack(side='right', pady=10)
    LOGIN_BUTTON = Button(INNER_FRAME, text='Login', bg='#cdcdd4', font=('Times New Roman', 18, 'bold'), relief='raised', command=lambda: login_window(DB_FILE_PATH, DB_TABLE_NAME))
    LOGIN_BUTTON.pack(side='right', pady=10)
    ROOT.bind("<Return>", (lambda event: create_account(DB_FILE_PATH, DB_TABLE_NAME, USERNAME_INPUT, PASSWORD_INPUT)))
    ROOT.mainloop()

def login_window(DB_FILE_PATH, DB_TABLE_NAME):  
    def toggle_password_visibility():
        if PASSWORD_INPUT.cget('show') == '':
            PASSWORD_INPUT.config(show='*')
            TOGGLE_PASSWORD_VISIBILITY.config(text='Show password')
        else:
            PASSWORD_INPUT.config(show='')
            TOGGLE_PASSWORD_VISIBILITY.config(text='Hide password')    
    clear_window()
    ROOT.update_idletasks()
    BORDER_FRAME = Frame(ROOT, bg='#B0AFB3', padx=3, pady=3)
    BORDER_FRAME.pack(expand=True)
    INNER_FRAME = Frame(BORDER_FRAME, bg='#cdcdd4', padx=50, pady=50)
    INNER_FRAME.pack(expand=True)
    USERNAME_LABEL = Label(INNER_FRAME, text='Username:', bg='#cdcdd4', font=('Times New Roman', 22, 'bold'))
    USERNAME_LABEL.pack(expand=True)
    USERNAME_INPUT = Entry(INNER_FRAME, font=('Times New Roman', 28))
    USERNAME_INPUT.pack(expand=True)
    PASSWORD_LABEL = Label(INNER_FRAME, text='Password:', bg='#cdcdd4', font=('Times New Roman', 22, 'bold'))
    PASSWORD_LABEL.pack(expand=True)
    PASSWORD_INPUT = Entry(INNER_FRAME, font=('Times New Roman', 28), show='*')
    PASSWORD_INPUT.pack(expand=True)
    TOGGLE_PASSWORD_VISIBILITY = Checkbutton(INNER_FRAME, text='Show Password', bg='#cdcdd4', command=toggle_password_visibility)
    TOGGLE_PASSWORD_VISIBILITY.pack(side='left', pady=10)
    SUBMIT_BUTTON = Button(INNER_FRAME, text='Submit', bg='#cdcdd4', font=('Times New Roman', 18, 'bold'), relief='raised', command=lambda: login(DB_FILE_PATH, DB_TABLE_NAME, USERNAME_INPUT, PASSWORD_INPUT))
    SUBMIT_BUTTON.pack(side='right', pady=10)
    CREATE_ACCOUNT_BUTTON = Button(INNER_FRAME, text='Create Account', bg='#cdcdd4', font=('Times New Roman', 18, 'bold'), relief='raised', command=lambda: create_account_window(DB_FILE_PATH, DB_TABLE_NAME))
    CREATE_ACCOUNT_BUTTON.pack(side='right', pady=10)
    ROOT.bind("<Return>", (lambda event: login(DB_FILE_PATH, DB_TABLE_NAME, USERNAME_INPUT, PASSWORD_INPUT)))
    ROOT.mainloop()

def home_page_window(DB_FILE_PATH, DB_TABLE_NAME, USERNAME, PASSWORD_HASH_BYTES):
    clear_window()
    NAVBAR_BORDER_FRAME = Frame(ROOT, bg='#B0AFB3', padx=3, pady=3)
    NAVBAR_BORDER_FRAME.pack(expand=True, anchor='n')
    NAVBAR_INNER_FRAME = Frame(NAVBAR_BORDER_FRAME, bg='#cdcdd4')
    NAVBAR_INNER_FRAME.pack(expand=True)
    NAVBAR_LABEL = Label(NAVBAR_INNER_FRAME, text=f'Welcome: {USERNAME}', bg='#cdcdd4', font=('Times New Roman', 22, 'bold'), width=ROOT.winfo_width())
    NAVBAR_LABEL.pack(expand=True)
    SUBMIT_BUTTON = Button(ROOT, text='Logout', bg='#cdcdd4', font=('Times New Roman', 18, 'bold'), relief='raised', command=lambda: logout(DB_FILE_PATH, DB_TABLE_NAME))
    SUBMIT_BUTTON.pack(expand=True, anchor='n')

def logout(DB_FILE_PATH, DB_TABLE_NAME):
    login_window(DB_FILE_PATH, DB_TABLE_NAME)
    
ROOT = Tk()
ROOT.configure(bg='#D3D5D4')
WIDTH = 900
HEIGHT = 500
X = (ROOT.winfo_screenwidth() - WIDTH) // 2
Y = (ROOT.winfo_screenheight() - HEIGHT) // 2
ROOT.geometry(f'{WIDTH}x{HEIGHT}+{X}+{Y}')
DB_FILE_PATH = fr'{dirname(__file__)}\Database\test.db'
DB_TABLE_NAME = 'Users'
login_window(DB_FILE_PATH, DB_TABLE_NAME)