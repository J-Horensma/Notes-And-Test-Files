from threading import Thread
from time import sleep
from tkinter import Tk, ttk, Label, Button
from Functions.tkinter_functions import input_string_prompt, folder_path_prompt
from Functions.aes_128_crypt_functions import aes_128_encrypt_folder, aes_128_decrypt_folder

def aes_128_encrypt_folder_thread(WINDOW):
    FOLDER_PATH = folder_path_prompt('Choose A Folder, To Encrypt')
    WINDOW.withdraw()
    PASSWORD = input_string_prompt(WINDOW, 'Enter A Password, To Encrypt The Folder:')
    WINDOW.deiconify()
    PROGRESS_BAR_MESSAGE = Label(WINDOW, text="Encrypting the folder, please wait...")
    PROGRESS_BAR_MESSAGE.pack()
    PROGRESS_BAR = ttk.Progressbar(WINDOW, mode='indeterminate')
    PROGRESS_BAR.pack()
    PROGRESS_BAR.start()
    def run():
        aes_128_encrypt_folder(FOLDER_PATH, PASSWORD)
        PROGRESS_BAR_MESSAGE.config(text='Encryption complete!')
        PROGRESS_BAR.stop()
        PROGRESS_BAR.pack_forget()
        sleep(1)
        PROGRESS_BAR_MESSAGE.pack_forget()
    ENCRYPT_FOLDER_THREAD = Thread(target=run, daemon=True)
    ENCRYPT_FOLDER_THREAD.start()

def aes_128_decrypt_folder_thread(WINDOW):
    WINDOW.withdraw()
    FOLDER_PATH = folder_path_prompt('Choose A Folder, To Decrypt')
    PASSWORD = input_string_prompt(WINDOW, 'Enter The Password, To Decrypt The Folder:')
    WINDOW.deiconify()
    PROGRESS_BAR_MESSAGE = Label(WINDOW, text="Decrypting the folder, please wait...")
    PROGRESS_BAR_MESSAGE.pack()
    PROGRESS_BAR = ttk.Progressbar(WINDOW, mode='indeterminate')
    PROGRESS_BAR.pack()
    PROGRESS_BAR.start()
    def run():
        aes_128_decrypt_folder(FOLDER_PATH, PASSWORD)
        PROGRESS_BAR_MESSAGE.config(text='Decryption complete!')
        PROGRESS_BAR.stop()
        PROGRESS_BAR.pack_forget()
        sleep(1)
        PROGRESS_BAR_MESSAGE.pack_forget()
    ENCRYPT_FOLDER_THREAD = Thread(target=run, daemon=True)
    ENCRYPT_FOLDER_THREAD.start()

WINDOW = Tk()
WINDOW.configure(bg='#D3D5D4')
WIDTH = 900
HEIGHT = 500
X = (WINDOW.winfo_screenwidth() - WIDTH) // 2
Y = (WINDOW.winfo_screenheight() - HEIGHT) // 2
WINDOW.geometry(f'{WIDTH}x{HEIGHT}+{X}+{Y}')
ENCRYPT_FOLDER_BUTTON = Button(WINDOW, text='Encrypt A Folder', width=18, font=('Times New Roman', 18, 'bold'), command=lambda: aes_128_encrypt_folder_thread(WINDOW))
ENCRYPT_FOLDER_BUTTON.pack(side='left', expand=True)
DECRYPT_FOLDER_BUTTON = Button(WINDOW, text='Decrypt A Folder', width=18, font=('Times New Roman', 18, 'bold'), command=lambda: aes_128_decrypt_folder_thread(WINDOW))
DECRYPT_FOLDER_BUTTON.pack(side='left', expand=True)
WINDOW.mainloop()