from os.path import isfile as isfile
from os.path import isdir as isdir
from os.path import isabs as isabs
from os.path import basename as basename
from os.path import dirname as dirname
from os.path import splitdrive as splitdrive
from os.path import splitext as splitext
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
    PATH = input('Enter a path, to separate: ')
    PATH_TYPE = 'File' if isfile(PATH) else 'Directory' if isdir(PATH) else 'Unknown'
    DRIVE, MIDDLE_AND_END = splitdrive(PATH)
    print(f'Path type:\n{PATH_TYPE}\n')
    print(f'Path drive name:\n{DRIVE}\n')
    if isfile(PATH):
        print(f'File name:\n{basename(PATH)}\n')
        print(f'File path:\n{PATH}\n')
        print(f'File extension:\n{splitext(PATH)}\n')
    elif isdir(PATH):
        print(f'Directory name:\n{basename(PATH)}\n')
        print(f'Directory path:\n{PATH}\n')
except KeyboardInterrupt:
    close()
except Exception as ERROR:
    clear_terminal()
    print(f'Error:\n{ERROR}\n')
    input('Press Enter, to exit: ')
    close()