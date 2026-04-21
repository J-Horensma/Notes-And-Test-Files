from os import chdir
from os.path import dirname
from time import sleep
from colorama import just_fix_windows_console

def clear_terminal():
   print('\033[H\033[2J', end='', flush=True)

def close():
    clear_terminal()
    print('Exiting...')
    sleep(1)
    exit()

just_fix_windows_console()

#WHEN LAUNCHING A PYTHON FILE, IMPORTING ANOTHER PYTHON FILE,
#THAT DETECTS THE CWD OF THE IMPORTING PYTHON FILE WITH "sys.argv[0]",
#MAKE SURE "os.chdir(os.path.dirname(__file__))", IS USED BEFORE IMPORTING,
#SO "sys.argv[0]" DOESN'T DETECT THE DEFAULT PYTHON PROFILE PATH.
chdir(dirname(__file__))
import direct_test