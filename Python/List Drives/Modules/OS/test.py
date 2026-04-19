from os import name, sep, listdrives
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
    print(' -------------')
    print('| Drive list: |')
    print(' -------------')
    for INDEX, DRIVE in enumerate(listdrives()):
        INDEX += 1
        DRIVE = DRIVE.replace(sep, '') if name == 'nt' else DRIVE
        print(f'{INDEX}.) Drive: {DRIVE}')
    input('\nPress Enter, to exit: ')
except KeyboardInterrupt:
    close()
except Exception as ERROR:
    clear_terminal()
    print(f'{ERROR}\n')
    input('Press Enter, to exit: ')
    close()