from tkinter import Tk, Label

def toggle_screen(event):
    return ROOT.attributes("-fullscreen", not ROOT.attributes("-fullscreen"))
    
ROOT = Tk()
ROOT.title('"tkinter" Test Application')

#THE "Tk().attributes()" METHOD, HAS A FULLSCREEN MODE.
#TO START FULLSCREEN MODE, USE "Tk().attributes('-fullscreen', True)".
ROOT.attributes('-fullscreen', True)

#TO TOGGLE FULLSCREEN MODE WITH THE "f11" KEY, USE "Tk().bind()",
#WITH A FUNCTION THAT RETURNS "Tk().attributes('-fullscreen', False)".
ROOT.bind("<F11>", toggle_screen)

LABEL = Label(ROOT, text='To toggle fullscreen mode, press the "f11" key.', font=('Arial', 28))
LABEL.pack(expand=True, fill='both')
ROOT.mainloop()