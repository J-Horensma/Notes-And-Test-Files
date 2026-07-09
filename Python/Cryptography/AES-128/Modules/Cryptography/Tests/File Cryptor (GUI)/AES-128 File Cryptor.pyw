from threading import Thread
from os.path import expanduser
from tkinter import Tk, ttk, Frame, Label, Button, messagebox
from src.tkinter_functions_and_classes import input_password_prompt, folder_path_prompt, file_path_prompt
from src.aes_128_crypt_functions import aes_128_encrypt_folder, aes_128_decrypt_folder, aes_128_encrypt_file, aes_128_decrypt_file

def disable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON):
    ENCRYPT_FOLDER_BUTTON.config(state='disabled')
    DECRYPT_FOLDER_BUTTON.config(state='disabled')
    ENCRYPT_FILE_BUTTON.config(state='disabled')
    DECRYPT_FILE_BUTTON.config(state='disabled')

def enable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON):
    ENCRYPT_FOLDER_BUTTON.config(state='normal')
    DECRYPT_FOLDER_BUTTON.config(state='normal')
    ENCRYPT_FILE_BUTTON.config(state='normal')
    DECRYPT_FILE_BUTTON.config(state='normal')

def aes_128_encrypt_folder_thread(WINDOW, ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON):
    PROMPT_TITLE='Choose A Folder, To Encrypt'
    FOLDER_PATH = folder_path_prompt(PROMPT_TITLE)
    if not FOLDER_PATH:
        return
    while True:
        PASSWORD = input_password_prompt(WINDOW).value
        if not PASSWORD:
            RESULT = messagebox.askyesno(
                title='Error',
                message='No password, was entered, try again?'
            )
            if not RESULT:
                return
            else:
                continue
        break
    PROGRESS_BAR_MESSAGE = Label(WINDOW, text=f'AES-128 encrypting the folder:\n{FOLDER_PATH},\nplease wait...')
    PROGRESS_BAR_MESSAGE.pack()
    WINDOW.update_idletasks()
    MESSAGE_WIDTH = PROGRESS_BAR_MESSAGE.winfo_reqwidth()
    PROGRESS_BAR = ttk.Progressbar(WINDOW, mode='indeterminate', length=MESSAGE_WIDTH)
    PROGRESS_BAR.pack()
    def finish_process(RESULT):
        PROGRESS_BAR.stop()
        PROGRESS_BAR.pack_forget()
        if RESULT[0]:
            PROGRESS_BAR_MESSAGE.config(text=RESULT[1])
        elif isinstance(RESULT[1], list):
            ERROR_MESSAGE = '\n'.join(RESULT[1])
            PROGRESS_BAR_MESSAGE.config(text=ERROR_MESSAGE)
        WINDOW.after(3000, PROGRESS_BAR_MESSAGE.pack_forget)
        enable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
    def start_process():
        disable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
        PROGRESS_BAR.start()
        RESULT = aes_128_encrypt_folder(FOLDER_PATH, PASSWORD)
        WINDOW.after(0, lambda: finish_process(RESULT))
    Thread(target=start_process, daemon=True).start()

def aes_128_decrypt_folder_thread(WINDOW, ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON):    
    PROMPT_TITLE='Choose A Folder, To Decrypt'
    FOLDER_PATH = folder_path_prompt(PROMPT_TITLE)
    if not FOLDER_PATH:
        return
    while True:
        PASSWORD = input_password_prompt(WINDOW).value
        if not PASSWORD:
            RESULT = messagebox.askyesno(
                title='Error',
                message='No password, was entered, try again?'
            )
            if not RESULT:
                return
            else:
                continue
        break
    PROGRESS_BAR_MESSAGE = Label(WINDOW, text=f'AES-128 decrypting the folder:\n{FOLDER_PATH},\nplease wait...')
    PROGRESS_BAR_MESSAGE.pack()
    WINDOW.update_idletasks()
    MESSAGE_WIDTH = PROGRESS_BAR_MESSAGE.winfo_reqwidth()
    PROGRESS_BAR = ttk.Progressbar(WINDOW, mode='indeterminate', length=MESSAGE_WIDTH)
    PROGRESS_BAR.pack()
    def finish_process(RESULT):
        PROGRESS_BAR.stop()
        PROGRESS_BAR.pack_forget()
        if RESULT[0]:
            PROGRESS_BAR_MESSAGE.config(text=RESULT[1])
        elif isinstance(RESULT[1], list):
            ERROR_MESSAGE = '\n'.join(RESULT[1])   
            PROGRESS_BAR_MESSAGE.config(text=ERROR_MESSAGE)
        WINDOW.after(3000, PROGRESS_BAR_MESSAGE.pack_forget)
        enable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
    def start_process():
        disable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
        PROGRESS_BAR.start()
        RESULT = aes_128_decrypt_folder(FOLDER_PATH, PASSWORD)
        WINDOW.after(0, lambda: finish_process(RESULT))
    Thread(target=start_process, daemon=True).start()

def aes_128_encrypt_file_thread(WINDOW, ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON):
    PROMPT_TITLE='Choose A File, To Encrypt'
    FILE_PATH = file_path_prompt(PROMPT_TITLE)
    if not FILE_PATH:
        return
    while True:
        PASSWORD = input_password_prompt(WINDOW).value
        if not PASSWORD:
            RESULT = messagebox.askyesno(
                title='Error',
                message='No password, was entered, try again?'
            )
            if not RESULT:
                return
            else:
                continue
        break
    PROGRESS_BAR_MESSAGE = Label(WINDOW, text=f'AES-128 encrypting the file:\n{FILE_PATH},\nplease wait...')
    PROGRESS_BAR_MESSAGE.pack()
    WINDOW.update_idletasks()
    MESSAGE_WIDTH = PROGRESS_BAR_MESSAGE.winfo_reqwidth()
    PROGRESS_BAR = ttk.Progressbar(WINDOW, mode='indeterminate', length=MESSAGE_WIDTH)
    PROGRESS_BAR.pack()
    def finish_process(RESULT):
        PROGRESS_BAR.stop()
        PROGRESS_BAR.pack_forget()
        PROGRESS_BAR_MESSAGE.config(text=RESULT[1])
        WINDOW.after(3000, PROGRESS_BAR_MESSAGE.pack_forget)
        enable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
    def start_process():
        disable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
        PROGRESS_BAR.start()
        RESULT = aes_128_encrypt_file(FILE_PATH, PASSWORD)
        WINDOW.after(3000, lambda: finish_process(RESULT))
    Thread(target=start_process, daemon=True).start()

def aes_128_decrypt_file_thread(WINDOW, ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON):
    PROMPT_TITLE='Choose A File, To Decrypt'
    FILE_PATH = file_path_prompt(PROMPT_TITLE)
    if not FILE_PATH:
        return
    while True:
        PASSWORD = input_password_prompt(WINDOW).value
        if not PASSWORD:
            RESULT = messagebox.askyesno(
                title='Error',
                message='No password, was entered, try again?'
            )
            if not RESULT:
                return
            else:
                continue
        break
    PROGRESS_BAR_MESSAGE = Label(WINDOW, text=f'AES-128 decrypting the file:\n{FILE_PATH},\nplease wait...')
    PROGRESS_BAR_MESSAGE.pack()
    WINDOW.update_idletasks()
    MESSAGE_WIDTH = PROGRESS_BAR_MESSAGE.winfo_reqwidth()
    PROGRESS_BAR = ttk.Progressbar(WINDOW, mode='indeterminate', length=MESSAGE_WIDTH)
    PROGRESS_BAR.pack()
    def finish_process(RESULT):
        PROGRESS_BAR.stop()
        PROGRESS_BAR.pack_forget()
        PROGRESS_BAR_MESSAGE.config(text=RESULT[1])
        WINDOW.after(3000, PROGRESS_BAR_MESSAGE.pack_forget)
        enable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
    def start_process():
        disable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
        PROGRESS_BAR.start()
        RESULT = aes_128_decrypt_file(FILE_PATH, PASSWORD)
        WINDOW.after(3000, lambda: finish_process(RESULT))
    Thread(target=start_process, daemon=True).start()

WINDOW = Tk()
WINDOW.configure(bg='#D3D5D4')
WIDTH = 900
HEIGHT = 500
X = (WINDOW.winfo_screenwidth() - WIDTH) // 2
Y = (WINDOW.winfo_screenheight() - HEIGHT) // 2
WINDOW.geometry(f'{WIDTH}x{HEIGHT}+{X}+{Y}')
WINDOW.title('AES-128 File Cryptor')
BUTTON_FRAME = Frame(WINDOW, bg='#D3D5D4')
BUTTON_FRAME.pack(expand=True)
ENCRYPT_FOLDER_BUTTON = Button(
    BUTTON_FRAME,
    text='Encrypt A Folder',
    width=18,
    font=('Times New Roman', 18, 'bold'),
    command=lambda: aes_128_encrypt_folder_thread(WINDOW, ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
)
ENCRYPT_FOLDER_BUTTON.pack(pady=10)
DECRYPT_FOLDER_BUTTON = Button(
    BUTTON_FRAME,
    text='Decrypt A Folder',
    width=18,
    font=('Times New Roman', 18, 'bold'),
    command=lambda: aes_128_decrypt_folder_thread(WINDOW, ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
)
DECRYPT_FOLDER_BUTTON.pack(pady=10)
ENCRYPT_FILE_BUTTON = Button(
    BUTTON_FRAME,
    text='Encrypt A File',
    width=18,
    font=('Times New Roman', 18, 'bold'),
    command=lambda: aes_128_encrypt_file_thread(WINDOW, ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
)
ENCRYPT_FILE_BUTTON.pack(pady=10)
DECRYPT_FILE_BUTTON = Button(
    BUTTON_FRAME,
    text='Decrypt A File',
    width=18,
    font=('Times New Roman', 18, 'bold'),
    command=lambda: aes_128_decrypt_file_thread(WINDOW, ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
)
DECRYPT_FILE_BUTTON.pack(pady=10)
WINDOW.mainloop()
