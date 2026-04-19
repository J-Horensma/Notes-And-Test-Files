from os import chdir, walk
from os.path import basename, relpath, realpath
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
    PATH = input('Enter a path, to scan: ')
    chdir(PATH)
    print(f'Scanning: {PATH}')
    print(len(f'Scanning: {PATH}') * '-')
    for ROOT, FOLDERS, FILES in walk(PATH):
        CURRENT_DIRECTORY = realpath(relpath(ROOT, PATH))
        print(f'{CURRENT_DIRECTORY}')
        print(len(CURRENT_DIRECTORY) * '-')
        for FOLDER in FOLDERS:
            print(f'   |=>  {FOLDER}')
        for FILE in FILES:
            print(f'        |=> {FILE}')
        print()
    input('Press Enter, to exit: ')
except KeyboardInterrupt:
    close()
except Exception as ERROR:
    clear_terminal()
    print(f'Error:\n{ERROR}\n')
    input('Press Enter, to exit: ')
    close()