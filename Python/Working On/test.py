from threading import Thread
from os import walk
from os.path import dirname, relpath, join, islink, expanduser, getsize
from tkinter import Tk, ttk, Button, messagebox
from tkinter.filedialog import askdirectory
from Functions.sqlite3_account_functions import get_hash_and_salt, aes_128_encrypt, aes_128_decrypt

def check_thread(THREAD):
    if THREAD.is_alive():
        ROOT.after(100, check_thread, THREAD)

def directory_path_prompt(PROMPT_PATH=None, ERROR_MESSAGE=None):
    PROMPT_PATH = expanduser('~') if PROMPT_PATH == None else PROMPT_PATH
    while True:
        PATH = askdirectory(title='Select A Directory Path', initialdir=PROMPT_PATH)
        if not PATH:
            messagebox.showerror('Error', ERROR_MESSAGE if ERROR_MESSAGE else 'Error: A directory path, must be selected.')
            continue
        else:
            break
    return PATH

def recursive_files_total(PATH):
    FILES_TOTAL = 0
    for ROOT, DIRECTORIES, FILES in walk(PATH):
        FILES = [FILE for FILE in FILES if not FILE.startswith('.') and not islink(join(ROOT, FILE))]
        for FILE in FILES:
            FILES_TOTAL += 1
    return FILES_TOTAL

def recursive_aes_128_encrypt(PATH, PASSWORD_HASH_BYTES, SALT_BYTES):
    for ROOT, DIRECTORIES, FILES in walk(PATH):
        FILES = [FILE for FILE in FILES if not FILE.startswith('.') and not islink(join(ROOT, FILE))]
        for FILE_NAME in FILES:
            FILE_PATH = join(ROOT, FILE_NAME)
            with open(FILE_PATH, 'rb') as PLAINTEXT_FILE:
                PLAINTEXT_DATA = PLAINTEXT_FILE.read()
                if PLAINTEXT_DATA.strip() == b'':
                    continue
                ENCRYPTED_DATA = aes_128_encrypt(PLAINTEXT_DATA, PASSWORD_HASH_BYTES)
            with open(FILE_PATH, 'wb') as ENCRYPTED_FILE:
                ENCRYPTED_FILE.write(ENCRYPTED_DATA)

def recursive_aes_128_decrypt(PATH, PASSWORD_HASH_BYTES, SALT_BYTES):
    for ROOT, DIRECTORIES, FILES in walk(PATH):
        FILES = [FILE for FILE in FILES if not FILE.startswith('.') and not islink(join(ROOT, FILE))]
        for FILE_NAME in FILES:
            FILE_PATH = join(ROOT, FILE_NAME)
            with open(FILE_PATH, 'rb') as ENCRYPTED_FILE:
                ENCRYPTED_DATA = ENCRYPTED_FILE.read()
                if ENCRYPTED_DATA.strip() == b'':
                    continue
                PLAINTEXT_DATA = aes_128_decrypt(ENCRYPTED_DATA, PASSWORD_HASH_BYTES)
            with open(FILE_PATH, 'wb') as DECRYPTED_FILE:
                DECRYPTED_FILE.write(PLAINTEXT_DATA)

def encrypt_folder_thread(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, PASSWORD_HASH_BYTES, SALT_BYTES):
    PATH = directory_path_prompt()
    ENCRYPT_THREAD = Thread(target=lambda: recursive_aes_128_encrypt(PATH, PASSWORD_HASH_BYTES, SALT_BYTES))
    ENCRYPT_THREAD.daemon = True
    ENCRYPT_THREAD.start()
    ENCRYPT_FOLDER_BUTTON.config(state='disabled')
    DECRYPT_FOLDER_BUTTON.config(state='disabled')
    ENCRYPT_THREAD.join()
    ENCRYPT_FOLDER_BUTTON.config(state='normal')
    DECRYPT_FOLDER_BUTTON.config(state='normal')

def decrypt_folder_thread(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, PASSWORD_HASH_BYTES, SALT_BYTES):
    PATH = directory_path_prompt()
    DECRYPT_THREAD = Thread(target=lambda: recursive_aes_128_decrypt(PATH, PASSWORD_HASH_BYTES, SALT_BYTES))
    DECRYPT_THREAD.daemon = True
    DECRYPT_THREAD.start()
    ENCRYPT_FOLDER_BUTTON.config(state='disabled')
    DECRYPT_FOLDER_BUTTON.config(state='disabled')
    DECRYPT_THREAD.join()
    ENCRYPT_FOLDER_BUTTON.config(state='normal')
    DECRYPT_FOLDER_BUTTON.config(state='normal')

ROOT = Tk()
ROOT.configure(bg='#D3D5D4')
WIDTH = 900
HEIGHT = 500
X = (ROOT.winfo_screenwidth() - WIDTH) // 2
Y = (ROOT.winfo_screenheight() - HEIGHT) // 2
ROOT.geometry(f'{WIDTH}x{HEIGHT}+{X}+{Y}')
PASSWORD = 'Test'
PASSWORD_HASH_BYTES, SALT_BYTES = get_hash_and_salt(PASSWORD)
ENCRYPT_FOLDER_BUTTON = Button(ROOT, text='Encrypt Folder', width=10, command=lambda: encrypt_folder_thread(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, PASSWORD_HASH_BYTES, SALT_BYTES))
ENCRYPT_FOLDER_BUTTON.pack(side="left", expand=True)
DECRYPT_FOLDER_BUTTON = Button(ROOT, text='Decrypt Folder', width=10, command=lambda: decrypt_folder_thread(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, PASSWORD_HASH_BYTES, SALT_BYTES))
DECRYPT_FOLDER_BUTTON.pack(side="left", expand=True)
ROOT.mainloop()