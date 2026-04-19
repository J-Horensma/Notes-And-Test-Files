from os import chdir, walk
from os.path import realpath, exists, relpath
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
    while True:
        clear_terminal()
        PATH = input('Enter a path, to scan: ')
        if not PATH:
            print('Empty input, was provided\n')
            input('Press Enter, to try again: ')
            clear_terminal()
            continue
        elif not exists(PATH):
            print(f'The following path, does not exist:\n{PATH}\n')
            input('Press Enter, to try again: ')
            clear_terminal()
            continue
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
        input('Press Enter, to try again: ')
except KeyboardInterrupt:
    close()
except Exception as ERROR:
    clear_terminal()
    print(f'{ERROR}\n')
    input('Press Enter, to exit: ')
    close()