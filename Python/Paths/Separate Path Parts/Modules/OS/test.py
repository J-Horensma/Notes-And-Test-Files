from os.path import exists, splitdrive, splitext, isfile, isdir, basename
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
        print(f'Path type:\n{PATH_TYPE}\n')
        print(f'Path drive name:\n{DRIVE}\n')
        if isfile(PATH):
            print(f'File name:\n{basename(PATH)}\n')
            print(f'File path:\n{PATH}\n')
            print(f'File extension:\n{splitext(PATH)}\n')
        elif isdir(PATH):
            print(f'Directory name:\n{basename(PATH)}\n')
            print(f'Directory path:\n{PATH}\n')
        input('Press Enter, to try again: ')
except KeyboardInterrupt:
    close()
except Exception as ERROR:
    clear_terminal()
    print(f'{ERROR}\n')
    input('Press Enter, to exit: ')
    close()