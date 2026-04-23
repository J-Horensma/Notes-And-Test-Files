from tkinter import Tk
from time import sleep
from platform import system

def restore_screen():
    return ROOT.attributes('-fullscreen', False)
    
ROOT = Tk()

#THE "Tk().attributes()" METHOD, ALLOWS A FULLSCREEN OPTION.
ROOT.attributes('-fullscreen', True)

#TO CLOSE FULLSCREEN MODE WITH THE ESCAPE KEY, USE "Tk.bind()",
#CALLING A FUNCTION THAT USES "Tk.attributes('-fullscreen', False)".
ROOT.bind("<Escape>", restore_screen)

ROOT.title('"tkinter" Test Application')
try:
    while True:
        ROOT.mainloop()
except Exception as ERROR:
    print(f'{ERROR}\n')
    exit(1)