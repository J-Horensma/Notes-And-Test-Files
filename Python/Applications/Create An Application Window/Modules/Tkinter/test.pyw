from tkinter import Tk
from time import sleep
from platform import system

#IN ORDER TO CREATE A WINDOW, THE "Tk()"
#FUNCTION IS CALLED, FROM THE "tkinter" LIBRARY.
ROOT = Tk()

#TO SET A WINDOW TITLE, THAT SHOWS, AT THE TOP
#OF THE WINDOW, USE "Tk().title('[TITLE HERE']')".
ROOT.title('"tkinter" Test Application')
try:
    while True:
        #TO RUN THE WINDOW, USE "Tk().mainloop()" 
        ROOT.mainloop()
except KeyboardInterrupt:
    exit(0)
except Exception as ERROR:
    print(f'{ERROR}\n')
    exit(1)
