from tkinter import Tk, Label

def toggle_fullscreen(event):
    return ROOT.attributes("-fullscreen", not ROOT.attributes("-fullscreen"))
    
ROOT = Tk()
ROOT.geometry('800x600')
ROOT.title('"tkinter" Test Application')

#THE "tkinter.Tk().attributes()" METHOD, HAS A FULLSCREEN MODE.
#TO START FULLSCREEN MODE, USE "tkinter.Tk().attributes('-fullscreen', True)"
ROOT.attributes('-fullscreen', True)

#TO TOGGLE FULLSCREEN MODE WITH THE "f11" KEY, USE "tkinter.Tk().bind()",
#WITH A FUNCTION THAT RETURNS "tkinter.Tk().attributes('-fullscreen', False)".
ROOT.bind("<F11>", toggle_fullscreen)

LABEL = Label(ROOT, text='To toggle fullscreen mode, press the "f11" key.', font=('Arial', 28, 'bold'))
LABEL.pack(expand=True)
ROOT.mainloop()
