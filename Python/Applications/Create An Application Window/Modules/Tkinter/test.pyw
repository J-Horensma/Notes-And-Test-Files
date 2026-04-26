from tkinter import Tk

#IN ORDER TO CREATE AN APPLICATION WINDOW, THE "tkinter.Tk()"
#CLASS IS CALLED, FROM "tkinter".
ROOT = Tk()

#TO SET THE WINDOW SIZE, BY HEIGHT AND WIDTH, IN PIXELS,
#USE "tkinter.Tk().geometry('[WIDTH HERE]x[HEIGHT HERE]')".
ROOT.geometry('800x600')

#TO SET A WINDOW TITLE, THAT SHOWS AT THE TOP
#OF THE WINDOW, USE "tkinter.Tk().title('[TITLE HERE]')".
ROOT.title('"tkinter" Test Application')

#TO RUN THE APPLICATION WINDOW, USE "tkinter.Tk().mainloop()".
ROOT.mainloop()
