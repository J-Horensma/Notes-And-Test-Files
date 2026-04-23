from tkinter import Tk
from time import sleep
from platform import system

ROOT = Tk()

#THE "Tk().attributes()" METHOD, ALLOWS A FULLSCREEN OPTION
ROOT.attributes('-fullscreen', True)

ROOT.title('"tkinter" Test Application')
try:
    while True:
        ROOT.mainloop()
except Exception as ERROR:
    print(f'{ERROR}\n')
    exit(1)