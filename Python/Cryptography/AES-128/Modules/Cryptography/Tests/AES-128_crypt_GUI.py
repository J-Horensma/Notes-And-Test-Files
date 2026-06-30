from tkinter import Tk, Button

def encrypt_folder():
    pass
def decrypt_folder():
    pass
WINDOW = Tk()
WINDOW.configure(bg='#D3D5D4')
WIDTH = 900
HEIGHT = 500
X = (WINDOW.winfo_screenwidth() - WIDTH) // 2
Y = (WINDOW.winfo_screenheight() - HEIGHT) // 2
WINDOW.geometry(f'{WIDTH}x{HEIGHT}+{X}+{Y}')
ENCRYPT_FOLDER_BUTTON = Button(WINDOW, text='Encrypt A Folder', width=18, font=('Times New Roman', 18, 'bold'), command=lambda: encrypt_folder())
ENCRYPT_FOLDER_BUTTON.pack(side='left', expand=True)
DECRYPT_FOLDER_BUTTON = Button(WINDOW, text='Decrypt A Folder', width=18, font=('Times New Roman', 18, 'bold'), command=lambda: decrypt_folder())
DECRYPT_FOLDER_BUTTON.pack(side='left', expand=True)
WINDOW.mainloop()