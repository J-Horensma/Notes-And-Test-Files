import sys, time
from os import chdir as chdir
from os.path import dirname as dirname
from sys import exit
from time import sleep
from colorama import just_fix_windows_console

def clear_terminal():
   print("\033[H\033[2J", end="", flush=True)

def close():
    clear_terminal()
    print('Exiting...')
    sleep(1)
    exit(0)

just_fix_windows_console()

try:
    chdir(dirname(__file__))
    import direct_test
except KeyboardInterrupt:
    close()
except Exception as ERROR:
    clear_terminal()
    print(f'Error:\n{ERROR}\n')
    input('Press Enter, to exit: ')
    close()