from tkinter import Tk

#IN ORDER TO CREATE AN APPLICATION WINDOW, 
#THE "tkinter.Tk()" CLASS IS CALLED.
ROOT = Tk()

#TO CREATE AND SET THE WINDOW SIZE, BY HEIGHT AND WIDTH, IN PIXELS,
#AND CENTER THE WINDOW, WHEN NOT IN FULLSCREEN MODE, USE THE FOLLOWING:
WIDTH = 900
HEIGHT = 500
X = (ROOT.winfo_screenwidth() - WIDTH) // 2
Y = (ROOT.winfo_screenheight() - HEIGHT) // 2
ROOT.geometry(f'{WIDTH}x{HEIGHT}+{X}+{Y}')

#TO SET A WINDOW TITLE, THAT SHOWS AT THE TOP OF THE WINDOW, 
#USE "tkinter.Tk().title('[TITLE HERE]')".
ROOT.title('Test Application')

#TO RUN THE APPLICATION WINDOW, USE "tkinter.Tk().mainloop()".
ROOT.mainloop()
