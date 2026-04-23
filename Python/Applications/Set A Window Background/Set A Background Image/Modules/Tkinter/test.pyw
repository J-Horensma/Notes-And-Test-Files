from os import chdir
from os.path import dirname
from tkinter import Tk, Label, PhotoImage

ROOT = Tk()
ROOT.geometry('800x600')
ROOT.title('"tkinter" Test Application')

#TO SET A BACKGROUND IMAGE, TO THE WINDOW, USE THE BELOW METHOD:
chdir(dirname(__file__))
BACKGROUND_IMAGE = PhotoImage(file="Images/python.png")
BACKGROUND_LABEL = Label(ROOT, image=BACKGROUND_IMAGE)
BACKGROUND_LABEL.place(x=0, y=0, relwidth=1, relheight=1)

ROOT.mainloop()