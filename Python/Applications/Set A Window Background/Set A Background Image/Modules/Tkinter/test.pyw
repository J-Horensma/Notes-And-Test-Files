from os import chdir
from os.path import dirname
from tkinter import Tk, Label, PhotoImage

ROOT = Tk()
ROOT.geometry('800x600')
ROOT.title('"tkinter" Test Application')

#TO SET THE CWD, TO THE CURRENT FILE'S PATH,
#SO IMAGES ARE LOCATED, IN RELATION TO THE CURRENT FILE'S PATH,
#USE "os.chdir(os.path.dirname(__file__))".
chdir(dirname(__file__))

#TO SET A BACKGROUND IMAGE, SET A VARIABLE FOR "tkinter.PhotoImage(file='[IMAGE PATH HERE]')" AND
#SET THAT VARIABLE, IN A LABEL, AS THE "image" OPTION, LIKE SO: "LABEL_VARIABLE = Label(tkinter.Tk(), image=[VARIABLE HERE])".
BACKGROUND_IMAGE = PhotoImage(file='Images/python.png', format='png')
BACKGROUND_LABEL = Label(ROOT, image=BACKGROUND_IMAGE)

#IF YOU WANT TO PLACE ELEMENTS ON TOP OF THE BACKGROUND IMAGE, 
#USE THE ".place()" METHOD, WHEN SETTING THE BACKGROUND IMAGE.
BACKGROUND_LABEL.place(relheight=1, relwidth=1)

LABEL = Label(ROOT, text='Test Application Title', font=('Helvetica', 28, ('italic','bold')))
LABEL.pack(expand=True, anchor='n', padx=20, pady=20)

ROOT.mainloop()
