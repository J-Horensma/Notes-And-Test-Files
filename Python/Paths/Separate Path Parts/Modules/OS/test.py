from sys import exit
from os.path import exists, isfile, isdir, splitdrive, splitext, basename
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

try:
    while True:
        clear_terminal()
        PATH = input('Enter a path, to separate: ').strip()
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
        PATH_TYPE = 'File' if isfile(PATH) else 'Directory' if isdir(PATH) else 'Unknown'
        DRIVE, MIDDLE_AND_END = splitdrive(PATH)
        print('Path type:')
        print('----------')
        print(f'{PATH_TYPE}\n')
        print('Path drive:')
        print('-----------')
        print(f'{DRIVE}\n')
        if isfile(PATH):
            print('File name:')
            print('----------')
            print(basename(PATH))
            print(f'File path:\n{PATH}\n')
            print('File extension:')
            print('---------------')
            print(f'{splitext(PATH)}\n')
        elif isdir(PATH):
            print('Directory name:')
            print('---------------')
            print(f'{basename(PATH)}\n')
            print('Directory path:')
            print('---------------')
            print(f'{PATH}\n')
        input('Press Enter, to try again: ')
except KeyboardInterrupt:
    close()
except Exception as ERROR:
    clear_terminal()
    print(f'{ERROR}\n')
    input('Press Enter, to exit: ')
    close()