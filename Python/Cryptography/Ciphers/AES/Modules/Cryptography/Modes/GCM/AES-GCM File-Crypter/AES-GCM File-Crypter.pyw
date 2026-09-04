'''
Commercial-Use License, With Redistribution Restrictions
--------------------------------------------------------

"AES-GCM File-Crypter" Copyright © 2026 Joel Horensma

This software may be used, modified, and incorporated into commercial products.
Modified versions and products incorporating the software may be distributed
commercially, provided that they contain substantial original additions or
modifications.

Redistribution or sale of the unmodified software, or a substantially
unchanged copy of it, is prohibited without prior written permission.

The copyright notice and this license must be retained in all copies.
'''

__name__ = 'AES-GCM File-Crypter'
__version__ = '1.0.0'
__author__ = 'Joel Horensma'
__email__ = 'N/A'
__license__ = 'Commercial-Use License, With Redistribution Restrictions'
__description__ = 'A GUI program, for securely encrypting and decrypting, files and folders (Cross-platform).'

from threading import Thread
from os.path import abspath, normpath, dirname, join
from tkinter import Tk, ttk, Frame, scrolledtext, Button, messagebox
from src.tkinter_functions import set_window_icon, center_window, dropdown_menu_prompt, password_input_prompt, folder_path_prompt, file_path_prompt
from src.aes_gcm_crypt import aes_gcm_encrypt_folder, aes_gcm_decrypt_folder, aes_gcm_encrypt_file, aes_gcm_decrypt_file

def disable_buttons():
    ENCRYPT_FOLDER_BUTTON.config(state='disabled')
    DECRYPT_FOLDER_BUTTON.config(state='disabled')
    ENCRYPT_FILE_BUTTON.config(state='disabled')
    DECRYPT_FILE_BUTTON.config(state='disabled')

def enable_buttons():
    ENCRYPT_FOLDER_BUTTON.config(state='normal')
    DECRYPT_FOLDER_BUTTON.config(state='normal')
    ENCRYPT_FILE_BUTTON.config(state='normal')
    DECRYPT_FILE_BUTTON.config(state='normal')

def aes_gcm_encrypt_folder_thread():
    PROMPT_TITLE = 'Choose A Folder, To Encrypt'
    FOLDER_PATH = folder_path_prompt(PROMPT_TITLE)
    if not FOLDER_PATH:
        return
    DROPDOWN_MENU_OPTIONS = ['AES-GCM-128 (Least drive-space used)', 'AES-GCM-192', 'AES-GCM-256 (Most secure)']
    PROMPT_TITLE = 'Select An Encryption:'
    PROMPT_MESSAGE = 'Select An Encryption:'
    SELECTED_ENCRYPTION = dropdown_menu_prompt(ROOT_WINDOW, DROPDOWN_MENU_OPTIONS, ICON_ICO, ICON_PNG, PROMPT_TITLE, PROMPT_MESSAGE)
    if not SELECTED_ENCRYPTION:
        return
    KEY_SIZE = int(SELECTED_ENCRYPTION[8:12])
    while True:
        PROMPT_TITLE = 'Password'
        PROMPT_MESSAGE = 'Enter A Password:'
        PASSWORD = password_input_prompt(ROOT_WINDOW, ICON_ICO, ICON_PNG, PROMPT_TITLE, PROMPT_MESSAGE)
        if PASSWORD is None:
            return
        elif not PASSWORD:
            CONFIRMATION = messagebox.askyesno(
                title='Password Required!',
                message='A password, is required, try again?'
            )
            if not CONFIRMATION:
                return
            else:
                continue
        else:
            CONFIRMATION = messagebox.askyesno(
                title='Confirm Selection',
                message=f'The folder path: "{FOLDER_PATH}", will be encrypted, are you sure you want to continue?' 
            )
            if not CONFIRMATION:
                return
            else:
                break
    ACTIVITY_LOG.config(state='normal')
    ACTIVITY_LOG.insert('insert', f'AES-GCM-{KEY_SIZE} encrypting the folder: "{FOLDER_PATH}",\nplease wait...\n')
    ACTIVITY_LOG.config(state='disabled')
    ACTIVITY_LOG.see('end')
    PROGRESS_BAR = ttk.Progressbar(ROOT_WINDOW, mode='indeterminate')
    PROGRESS_BAR.pack(fill='both')
    def finish_process(RESULT):
        PROGRESS_BAR.stop()
        PROGRESS_BAR.pack_forget()
        enable_buttons()
        ACTIVITY = RESULT[1]
        ACTIVITY_LOG.config(state='normal')
        ACTIVITY_LOG.insert('insert', f'{ACTIVITY}\n\n')
        ACTIVITY_LOG.config(state='disabled')
        ACTIVITY_LOG.see('end')
    def start_process():
        disable_buttons()
        PROGRESS_BAR.start()
        RESULT = aes_gcm_encrypt_folder(FOLDER_PATH, KEY_SIZE, PASSWORD)
        ROOT_WINDOW.after(0, lambda: finish_process(RESULT))
    Thread(target=start_process, daemon=True).start()

def aes_gcm_decrypt_folder_thread():    
    PROMPT_TITLE = 'Choose A Folder, To Decrypt'
    FOLDER_PATH = folder_path_prompt(PROMPT_TITLE)
    if not FOLDER_PATH:
        return
    while True:
        PROMPT_TITLE = 'Password'
        PROMPT_MESSAGE = 'Enter The Password:'
        PASSWORD = password_input_prompt(ROOT_WINDOW, ICON_ICO, ICON_PNG, PROMPT_TITLE, PROMPT_MESSAGE)
        if not PASSWORD:
            CONFIRMATION = messagebox.askyesno(
                title='Password Required!',
                message='A password, is required, try again?'
            )
            if not CONFIRMATION:
                return
            else:
                continue
        else:
            break
    ACTIVITY_LOG.config(state='normal')
    ACTIVITY_LOG.insert('insert', f'Decrypting the folder: "{FOLDER_PATH}",\nplease wait...\n')
    ACTIVITY_LOG.config(state='disabled')
    ACTIVITY_LOG.see('end')
    PROGRESS_BAR = ttk.Progressbar(ROOT_WINDOW, mode='indeterminate')
    PROGRESS_BAR.pack(fill='both')
    def finish_process(RESULT):
        PROGRESS_BAR.stop()
        PROGRESS_BAR.pack_forget()
        enable_buttons()
        ACTIVITY = RESULT[1]
        ACTIVITY_LOG.config(state='normal')
        ACTIVITY_LOG.insert('insert', f'{ACTIVITY}\n\n')
        ACTIVITY_LOG.config(state='disabled')
        ACTIVITY_LOG.see('end')
    def start_process():
        disable_buttons()
        PROGRESS_BAR.start()
        RESULT = aes_gcm_decrypt_folder(FOLDER_PATH, PASSWORD)
        ROOT_WINDOW.after(0, lambda: finish_process(RESULT))
    Thread(target=start_process, daemon=True).start()

def aes_gcm_encrypt_file_thread():
    PROMPT_TITLE='Choose A File, To Encrypt'
    FILE_PATH = file_path_prompt(PROMPT_TITLE)
    if not FILE_PATH:
        return
    DROPDOWN_MENU_OPTIONS = ['AES-GCM-128 (Least drive-space used)', 'AES-GCM-192', 'AES-GCM-256 (Most secure)']
    PROMPT_TITLE = 'Select An Encryption:'
    PROMPT_MESSAGE = 'Select An Encryption:'
    SELECTED_ENCRYPTION = dropdown_menu_prompt(ROOT_WINDOW, DROPDOWN_MENU_OPTIONS, ICON_ICO, ICON_PNG, PROMPT_TITLE, PROMPT_MESSAGE)
    if not SELECTED_ENCRYPTION:
        return
    KEY_SIZE = int(SELECTED_ENCRYPTION[8:12])
    while True:
        PROMPT_TITLE = 'Password'
        PROMPT_MESSAGE = 'Enter A Password:'
        PASSWORD = password_input_prompt(ROOT_WINDOW, ICON_ICO, ICON_PNG, PROMPT_TITLE, PROMPT_MESSAGE)
        if not PASSWORD:
            CONFIRMATION = messagebox.askyesno(
                title='Password Required!',
                message='A password, is required, try again?'
            )
            if not CONFIRMATION:
                return
            else:
                continue
        else:
            CONFIRMATION = messagebox.askyesno(
                title='Confirm Selection',
                message=f'The file path: "{FILE_PATH}", will be encrypted, are you sure you want to continue?' 
            )
            if not CONFIRMATION:
                return
            else:
                break
    ACTIVITY_LOG.config(state='normal')
    ACTIVITY_LOG.insert('insert', f'AES-GCM-{KEY_SIZE} encrypting the file: "{FILE_PATH}",\nplease wait...\n')
    ACTIVITY_LOG.config(state='disabled')
    ACTIVITY_LOG.see('end')
    PROGRESS_BAR = ttk.Progressbar(ROOT_WINDOW, mode='indeterminate')
    PROGRESS_BAR.pack(fill='both')
    def finish_process(RESULT):
        PROGRESS_BAR.stop()
        PROGRESS_BAR.pack_forget()
        enable_buttons()
        ACTIVITY = RESULT[1]
        ACTIVITY_LOG.config(state='normal')
        ACTIVITY_LOG.insert('insert', f'{ACTIVITY}\n\n')
        ACTIVITY_LOG.config(state='disabled')
        ACTIVITY_LOG.see('end')
    def start_process():
        disable_buttons()
        PROGRESS_BAR.start()
        RESULT = aes_gcm_encrypt_file(FILE_PATH, KEY_SIZE, PASSWORD)
        ROOT_WINDOW.after(0, lambda: finish_process(RESULT))
    Thread(target=start_process, daemon=True).start()

def aes_gcm_decrypt_file_thread():
    PROMPT_TITLE='Choose A File, To Decrypt'
    FILE_PATH = file_path_prompt(PROMPT_TITLE)
    if not FILE_PATH:
        return
    while True:
        PROMPT_TITLE = 'Password'
        PROMPT_MESSAGE = 'Enter The Password:'
        PASSWORD = password_input_prompt(ROOT_WINDOW, ICON_ICO, ICON_PNG, PROMPT_TITLE, PROMPT_MESSAGE)
        if not PASSWORD:
            CONFIRMATION = messagebox.askyesno(
                title='Password Required!',
                message='A password, is required, try again?'
            )
            if not CONFIRMATION:
                return
            else:
                continue
        else:
            break
    ACTIVITY_LOG.config(state='normal')
    ACTIVITY_LOG.insert('insert', f'Decrypting the file: "{FILE_PATH}",\nplease wait...\n')
    ACTIVITY_LOG.config(state='disabled')
    ACTIVITY_LOG.see('end')
    PROGRESS_BAR = ttk.Progressbar(ROOT_WINDOW, mode='indeterminate')
    PROGRESS_BAR.pack(fill='both')
    def finish_process(RESULT):
        PROGRESS_BAR.stop()
        PROGRESS_BAR.pack_forget()
        enable_buttons()
        ACTIVITY = RESULT[1]
        ACTIVITY_LOG.config(state='normal')
        ACTIVITY_LOG.insert('insert', f'{ACTIVITY}\n\n')
        ACTIVITY_LOG.config(state='disabled')
        ACTIVITY_LOG.see('end')
    def start_process():
        disable_buttons()
        PROGRESS_BAR.start()
        RESULT = aes_gcm_decrypt_file(FILE_PATH, PASSWORD)
        ROOT_WINDOW.after(0, lambda: finish_process(RESULT))
    Thread(target=start_process, daemon=True).start()

ROOT_WINDOW = Tk()
BASE_DIRECTORY = dirname(abspath(__file__))
ICON_ICO = join(BASE_DIRECTORY, normpath('assets/icon/ico/icon.ico'))
ICON_PNG = join(BASE_DIRECTORY, normpath('assets/icon/png/256x256.png'))
set_window_icon(ROOT_WINDOW, ICON_ICO, ICON_PNG)
ROOT_WINDOW.configure(bg='#D3D5D4')
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 500
center_window(ROOT_WINDOW, WINDOW_WIDTH, WINDOW_HEIGHT)
ROOT_WINDOW.title('AES-GCM File-Crypter')
BUTTON_FRAME = Frame(ROOT_WINDOW, bg='#D3D5D4')
BUTTON_FRAME.pack(expand=True)
ENCRYPT_FOLDER_BUTTON = Button(
    BUTTON_FRAME,
    text='Encrypt A Folder',
    width=18,
    font=('Times New Roman', 18, 'bold'),
    command=aes_gcm_encrypt_folder_thread
)
ENCRYPT_FOLDER_BUTTON.pack(pady=10)
DECRYPT_FOLDER_BUTTON = Button(
    BUTTON_FRAME,
    text='Decrypt A Folder',
    width=18,
    font=('Times New Roman', 18, 'bold'),
    command=aes_gcm_decrypt_folder_thread
)
DECRYPT_FOLDER_BUTTON.pack(pady=10)
ENCRYPT_FILE_BUTTON = Button(
    BUTTON_FRAME,
    text='Encrypt A File',
    width=18,
    font=('Times New Roman', 18, 'bold'),
    command=aes_gcm_encrypt_file_thread
)
ENCRYPT_FILE_BUTTON.pack(pady=10)
DECRYPT_FILE_BUTTON = Button(
    BUTTON_FRAME,
    text='Decrypt A File',
    width=18,
    font=('Times New Roman', 18, 'bold'),
    command=aes_gcm_decrypt_file_thread
)
DECRYPT_FILE_BUTTON.pack(pady=10)
ACTIVITY_LOG = scrolledtext.ScrolledText(ROOT_WINDOW, width=900, height=10)
ACTIVITY_LOG.pack(expand=True, fill='both')
ACTIVITY_LOG.insert('insert', 'Activity Log:\n\n')
ACTIVITY_LOG.config(state='disabled')
ROOT_WINDOW.mainloop()