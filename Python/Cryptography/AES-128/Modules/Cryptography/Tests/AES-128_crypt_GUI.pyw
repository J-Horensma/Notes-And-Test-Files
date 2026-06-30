from threading import Thread
from tkinter import Tk, ttk, Label, Button
from Functions.tkinter_functions import input_string_prompt, folder_path_prompt
from Functions.aes_128_crypt_functions import aes_128_encrypt_folder, aes_128_decrypt_folder

def disable_buttons(ENCRYPT_BTN, DECRYPT_BTN):
    ENCRYPT_BTN.config(state='disabled')
    DECRYPT_BTN.config(state='disabled')

def enable_buttons(ENCRYPT_BTN, DECRYPT_BTN):
    ENCRYPT_BTN.config(state='normal')
    DECRYPT_BTN.config(state='normal')

def aes_128_encrypt_folder_thread(WINDOW, ENCRYPT_BTN, DECRYPT_BTN):
    FOLDER_PATH = folder_path_prompt('Choose A Folder, To Encrypt')
    PASSWORD = input_string_prompt(WINDOW, 'Enter A Password, To Encrypt The Folder:')
    disable_buttons(ENCRYPT_BTN, DECRYPT_BTN)
    PROGRESS_BAR_MESSAGE = Label(WINDOW, text="AES-128 encrypting the folder, please wait...")
    PROGRESS_BAR_MESSAGE.pack()
    PROGRESS_BAR = ttk.Progressbar(WINDOW, mode='indeterminate', length=238)
    PROGRESS_BAR.pack()
    PROGRESS_BAR.start()
    def finish(RESULT):
        PROGRESS_BAR.stop()
        PROGRESS_BAR.pack_forget()
        if RESULT[0]:
            PROGRESS_BAR_MESSAGE.config(text=f'Successfully encrypted the folder\{}!')
            WINDOW.after(1000, PROGRESS_BAR_MESSAGE.pack_forget)
        elif RESULT[1] == 'ALREADY_AES_128_ENCRYPTED':
            PROGRESS_BAR_MESSAGE.config(text='The folder, already contains an AES-128 encrypted file.')
            WINDOW.after(1000, PROGRESS_BAR_MESSAGE.pack_forget)
        else:
            PROGRESS_BAR_MESSAGE.config(text=RESULT[1])
            WINDOW.after(1000, PROGRESS_BAR_MESSAGE.pack_forget)
        enable_buttons(ENCRYPT_BTN, DECRYPT_BTN)
    def run():
        RESULT = aes_128_encrypt_folder(FOLDER_PATH, PASSWORD)
        WINDOW.after(0, lambda: finish(RESULT))
    Thread(target=run, daemon=True).start()

def aes_128_decrypt_folder_thread(WINDOW, ENCRYPT_BTN, DECRYPT_BTN):
    FOLDER_PATH = folder_path_prompt('Choose A Folder, To Decrypt')
    PASSWORD = input_string_prompt(WINDOW, 'Enter The Password, To Decrypt The Folder:')
    disable_buttons(ENCRYPT_BTN, DECRYPT_BTN)
    PROGRESS_BAR_MESSAGE = Label(WINDOW, text="AES-128 decrypting the folder, please wait...")
    PROGRESS_BAR_MESSAGE.pack()
    PROGRESS_BAR = ttk.Progressbar(WINDOW, mode='indeterminate', length=238)
    PROGRESS_BAR.pack()
    PROGRESS_BAR.start()
    def finish(RESULT):
        PROGRESS_BAR.stop()
        PROGRESS_BAR.pack_forget()
        if RESULT[0]:
            PROGRESS_BAR_MESSAGE.config(text='Success!')
            WINDOW.after(1000, PROGRESS_BAR_MESSAGE.pack_forget)
        else:
            if RESULT[1] == 'INCORRECT_AES_128_FILE_DECRYPTION_PASSWORD':
                PROGRESS_BAR_MESSAGE.config(text='Incorrect password, try again!')
                WINDOW.after(1000, PROGRESS_BAR_MESSAGE.pack_forget)
            else:
                PROGRESS_BAR_MESSAGE.config(text='Success!')
                WINDOW.after(1000, PROGRESS_BAR_MESSAGE.pack_forget)
        enable_buttons(ENCRYPT_BTN, DECRYPT_BTN)
    def run():
        RESULT = aes_128_decrypt_folder(FOLDER_PATH, PASSWORD)
        WINDOW.after(0, lambda: finish(RESULT))
    Thread(target=run, daemon=True).start()

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
