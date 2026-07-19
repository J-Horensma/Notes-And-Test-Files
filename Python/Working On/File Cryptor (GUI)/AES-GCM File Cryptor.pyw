from threading import Thread
from tkinter import Tk, ttk, Frame, scrolledtext, Button, messagebox
from src.tkinter_functions import dropdown_menu_prompt, password_input_prompt, folder_path_prompt, file_path_prompt
from src.aes_gcm_crypt_functions import aes_gcm_encrypt_folder, aes_gcm_decrypt_folder, aes_gcm_encrypt_file, aes_gcm_decrypt_file

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

def aes_gcm_encrypt_folder_thread():
    PROMPT_TITLE = 'Choose A Folder, To Encrypt'
    FOLDER_PATH = folder_path_prompt(PROMPT_TITLE)
    if not FOLDER_PATH:
        return
    DROPDOWN_MENU_OPTIONS = ['AES-128-GCM (Least drive-space used)', 'AES-192-GCM', 'AES-256-GCM (Most secure)']
    PROMPT_TITLE = 'Select A Key Size:'
    PROMPT_MESSAGE = 'Select A Key Size:'
    SELECTED_ENCRYPTION = dropdown_menu_prompt(ROOT_WINDOW, DROPDOWN_MENU_OPTIONS, PROMPT_TITLE, PROMPT_MESSAGE)
    if not SELECTED_ENCRYPTION:
        return
    KEY_SIZE = int(SELECTED_ENCRYPTION[4:7])
    while True:
        PASSWORD = password_input_prompt(ROOT_WINDOW)
        if PASSWORD is None:
            return
        elif not PASSWORD:
            RESULT = messagebox.askyesno(
                title='Error',
                message='No password, was entered, try again?'
            )
            if not RESULT:
                return
            else:
                continue
        else:
            break
    ACTIVITY_LOG.config(state='normal')
    ACTIVITY_LOG.insert('insert', f'AES-{KEY_SIZE}-GCM encrypting the folder:\n{FOLDER_PATH},\nplease wait...\n')
    ACTIVITY_LOG.config(state='disabled')
    ACTIVITY_LOG.see('end')
    PROGRESS_BAR = ttk.Progressbar(ROOT_WINDOW, mode='indeterminate', length=900)
    PROGRESS_BAR.pack()
    def finish_process(RESULT):
        PROGRESS_BAR.stop()
        PROGRESS_BAR.pack_forget()
        enable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
        ACTIVITY = RESULT[1]
        ACTIVITY_LOG.config(state='normal')
        ACTIVITY_LOG.insert('insert', f'{ACTIVITY}\n\n')
        ACTIVITY_LOG.config(state='disabled')
        ACTIVITY_LOG.see('end')
    def start_process():
        disable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
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
        PASSWORD = password_input_prompt(ROOT_WINDOW)
        if not PASSWORD:
            RESULT = messagebox.askyesno(
                title='Error',
                message='No password, was entered, try again?'
            )
            if not RESULT:
                return
            else:
                continue
        else:
            break
    ACTIVITY_LOG.config(state='normal')
    ACTIVITY_LOG.insert('insert', f'AES-GCM decrypting the folder:\n{FOLDER_PATH},\nplease wait...\n\n')
    ACTIVITY_LOG.config(state='disabled')
    ACTIVITY_LOG.see('end')
    PROGRESS_BAR = ttk.Progressbar(ROOT_WINDOW, mode='indeterminate', length=900)
    PROGRESS_BAR.pack()
    def finish_process(RESULT):
        PROGRESS_BAR.stop()
        PROGRESS_BAR.pack_forget()
        enable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
        ACTIVITY = '\n'.join(RESULT[1]) if isinstance(RESULT[1], list) else RESULT[1]
        ACTIVITY_LOG.config(state='normal')
        ACTIVITY_LOG.insert('insert', f'{ACTIVITY}\n\n')
        ACTIVITY_LOG.config(state='disabled')
        ACTIVITY_LOG.see('end')
    def start_process():
        disable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
        PROGRESS_BAR.start()
        RESULT = aes_gcm_decrypt_folder(FOLDER_PATH, PASSWORD)
        ROOT_WINDOW.after(0, lambda: finish_process(RESULT))
    Thread(target=start_process, daemon=True).start()

def aes_gcm_encrypt_file_thread(ROOT_WINDOW, ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON, ACTIVITY_LOG):
    PROMPT_TITLE='Choose A File, To Encrypt'
    FILE_PATH = file_path_prompt(PROMPT_TITLE)
    if not FILE_PATH:
        return
    while True:
        PASSWORD = password_input_prompt(ROOT_WINDOW)
        if not PASSWORD:
            RESULT = messagebox.askyesno(
                title='Error',
                message='No password, was entered, try again?'
            )
            if not RESULT:
                return
            else:
                continue
        else:
            break
    ACTIVITY_LOG.config(state='normal')
    ACTIVITY_LOG.insert('insert', f'AES-128 encrypting the file:\n{FILE_PATH},\nplease wait...\n\n')
    ACTIVITY_LOG.config(state='disabled')
    ACTIVITY_LOG.see('end')
    PROGRESS_BAR = ttk.Progressbar(ROOT_WINDOW, mode='indeterminate', length=900)
    PROGRESS_BAR.pack()
    def finish_process(RESULT):
        PROGRESS_BAR.stop()
        PROGRESS_BAR.pack_forget()
        enable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
        ACTIVITY = '\n'.join(RESULT[1]) if isinstance(RESULT[1], list) else RESULT[1]
        ACTIVITY_LOG.config(state='normal')
        ACTIVITY_LOG.insert('insert', f'{ACTIVITY}\n\n')
        ACTIVITY_LOG.config(state='disabled')
        ACTIVITY_LOG.see('end')
    def start_process():
        disable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
        PROGRESS_BAR.start()
        RESULT = aes_gcm_encrypt_file(FILE_PATH, PASSWORD)
        ROOT_WINDOW.after(0, lambda: finish_process(RESULT))
    Thread(target=start_process, daemon=True).start()

def aes_gcm_decrypt_file_thread(ROOT_WINDOW, ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON, ACTIVITY_LOG):
    PROMPT_TITLE='Choose A File, To Decrypt'
    FILE_PATH = file_path_prompt(PROMPT_TITLE)
    if not FILE_PATH:
        return
    while True:
        PASSWORD = password_input_prompt(ROOT_WINDOW)
        if not PASSWORD:
            RESULT = messagebox.askyesno(
                title='Error',
                message='No password, was entered, try again?'
            )
            if not RESULT:
                return
            else:
                continue
        else:
            break
    ACTIVITY_LOG.config(state='normal')
    ACTIVITY_LOG.insert('insert', f'AES-GCM decrypting the file:\n{FILE_PATH},\nplease wait...\n\n')
    ACTIVITY_LOG.config(state='disabled')
    ACTIVITY_LOG.see('end')
    PROGRESS_BAR = ttk.Progressbar(ROOT_WINDOW, mode='indeterminate', length=900)
    PROGRESS_BAR.pack()
    def finish_process(RESULT):
        PROGRESS_BAR.stop()
        PROGRESS_BAR.pack_forget()
        enable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
        ACTIVITY = '\n'.join(RESULT[1]) if isinstance(RESULT[1], list) else RESULT[1]
        ACTIVITY_LOG.config(state='normal')
        ACTIVITY_LOG.insert('insert', f'{ACTIVITY}\n\n')
        ACTIVITY_LOG.config(state='disabled')
        ACTIVITY_LOG.see('end')
    def start_process():
        disable_buttons(ENCRYPT_FOLDER_BUTTON, DECRYPT_FOLDER_BUTTON, ENCRYPT_FILE_BUTTON, DECRYPT_FILE_BUTTON)
        PROGRESS_BAR.start()
        RESULT = aes_gcm_decrypt_file(FILE_PATH, PASSWORD)
        ROOT_WINDOW.after(0, lambda: finish_process(RESULT))
    Thread(target=start_process, daemon=True).start()

ROOT_WINDOW = Tk()
ROOT_WINDOW.configure(bg='#D3D5D4')
WIDTH = 900
HEIGHT = 500
X = (ROOT_WINDOW.winfo_screenwidth() - WIDTH) // 2
Y = (ROOT_WINDOW.winfo_screenheight() - HEIGHT) // 2
ROOT_WINDOW.geometry(f'{WIDTH}x{HEIGHT}+{X}+{Y}')
ROOT_WINDOW.title('AES-GCM File Cryptor')
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