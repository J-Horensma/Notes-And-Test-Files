from os import chdir, walk
from os.path import realpath, exists, relpath
from time import sleep
from platform import system

#IF THIS FILE, IS LAUNCHED BY WINDOWS:
if system() == 'Windows':
    from colorama import just_fix_windows_console
    just_fix_windows_console()

def clear_console():
   print('\033[H\033[2J', end='', flush=True)

def close():
    clear_console()
    print('Exiting...')
    sleep(1)
    exit(0)

try:
    while True:
        clear_console()
        PATH = input('Enter a path, to recursively scan: ').strip()
        if not PATH:
            print('Empty input, was provided\n')
            input('Press Enter, to try again: ')
            clear_console()
            continue
        elif not exists(PATH):
            print(f'The following path, does not exist:\n{PATH}\n')
            input('Press Enter, to try again: ')
            clear_console()
            continue
        else:
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
    clear_console()
    print(f'{ERROR}\n')
    input('Press Enter, to exit: ')
    exit(1)