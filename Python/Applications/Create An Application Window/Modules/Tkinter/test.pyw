from tkinter import Tk
from time import sleep
from platform import system

#IF THIS FILE, IS LAUNCHED BY WINDOWS:
if system() == 'Windows':
    from subprocess import run, PIPE, CREATE_NO_WINDOW
    from colorama import just_fix_windows_console
    just_fix_windows_console()

def clear_console():
   print('\033[H\033[2J', end='', flush=True)

def close():
    clear_console()
    print('Exiting...')
    sleep(1)
    exit(0)

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
    close()
except Exception as ERROR:
    clear_console()
    print(f'{ERROR}\n')
    input('Press Enter, to exit: ')
    exit(1)