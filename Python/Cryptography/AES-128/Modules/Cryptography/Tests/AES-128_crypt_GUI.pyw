from time import sleep
from threading import Thread
from tkinter import Tk, ttk, Label, Button
from Functions.tkinter_functions import input_string_prompt, folder_path_prompt
from Functions.aes_128_crypt_functions import aes_128_encrypt_folder, aes_128_decrypt_folder

def disable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON):
    ENCRYPT_FOLDER_BUTTON.config(state='disabled')
    DECRYPT_FOLDER_BUTTON.config(state='disabled')

def enable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON):
    ENCRYPT_FOLDER_BUTTON.config(state='normal')
    DECRYPT_FOLDER_BUTTON.config(state='normal')

def aes_128_encrypt_folder_thread(WINDOW, ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON):
    FOLDER_PATH = folder_path_prompt('Choose A Folder, To Encrypt')
    PASSWORD = input_string_prompt(WINDOW, 'Enter A Password, To Encrypt The Folder:')
    PROGRESS_BAR_MESSAGE = Label(WINDOW, text=f'AES-128 encrypting the folder:\n{FOLDER_PATH},\nplease wait...')
    PROGRESS_BAR_MESSAGE.pack()
    PROGRESS_BAR = ttk.Progressbar(WINDOW, mode='indeterminate', length=len(PROGRESS_BAR_MESSAGE.cget('text')) * 2.5)
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
        enable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON)
    def start_process():
        disable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON)
        PROGRESS_BAR.start()
        RESULT = aes_128_encrypt_folder(FOLDER_PATH, PASSWORD)
        WINDOW.after(0, lambda: finish_process(RESULT))
    Thread(target=start_process, daemon=True).start()

def aes_128_decrypt_folder_thread(WINDOW, ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON):    
    FOLDER_PATH = folder_path_prompt('Choose A Folder, To Decrypt')
    PASSWORD = input_string_prompt(WINDOW, 'Enter A Password, To Decrypt The Folder:')
    PROGRESS_BAR_MESSAGE = Label(WINDOW, text=f'AES-128 decrypting the folder:\n{FOLDER_PATH},\nplease wait...')
    PROGRESS_BAR_MESSAGE.pack()
    PROGRESS_BAR = ttk.Progressbar(WINDOW, mode='indeterminate', length=len(PROGRESS_BAR_MESSAGE.cget('text')) * 2.5)
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
        enable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON)
    def start_process():
        disable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON)
        PROGRESS_BAR.start()
        RESULT = aes_128_decrypt_folder(FOLDER_PATH, PASSWORD)
        WINDOW.after(0, lambda: finish_process(RESULT))
    Thread(target=start_process, daemon=True).start()

WINDOW = Tk()
WINDOW.configure(bg='#D3D5D4')
WIDTH = 900
HEIGHT = 500
X = (WINDOW.winfo_screenwidth() - WIDTH) // 2
Y = (WINDOW.winfo_screenheight() - HEIGHT) // 2
WINDOW.geometry(f'{WIDTH}x{HEIGHT}+{X}+{Y}')
ENCRYPT_FOLDER_BUTTON = Button(
    WINDOW,
    text='Encrypt A Folder',
    width=18,
    font=('Times New Roman', 18, 'bold'),
    command=lambda: aes_128_encrypt_folder_thread(WINDOW, ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON)
)
ENCRYPT_FOLDER_BUTTON.pack(side='left', expand=True)
DECRYPT_FOLDER_BUTTON = Button(
    WINDOW,
    text='Decrypt A Folder',
    width=18,
    font=('Times New Roman', 18, 'bold'),
    command=lambda: aes_128_decrypt_folder_thread(WINDOW, ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON)
)
DECRYPT_FOLDER_BUTTON.pack(side='left', expand=True)
WINDOW.mainloop()