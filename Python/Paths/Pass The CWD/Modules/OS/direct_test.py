from os import getcwd as getcwd
from os import chdir as chdir
from os.path import normpath
from os.path import basename
from os.path import dirname
from os.path import realpath
from sys import exit
from sys import argv
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
    print("NOTE:\nIn order to read the launching process' CWD, from this file,",'"sys.argv[0]" is used.\n')
    if __file__ == argv[0]:
        chdir(dirname(__file__))
        print(f'File name:\n{basename(__file__)}\n')
        print(f"Fle's CWD:\n{getcwd()}\n")
    elif dirname(argv[0]) == getcwd():
        print(f'Launched by:\nPython import\n')
        print(f'Importing file:\n{basename(realpath(argv[0]))}\n')
        print(f"Importing file's CWD:\n{dirname(realpath(argv[0]))}\n")
    else:
        print(f'Launched by:\nShell process\n')
        print(f'Shell process CWD:\n{getcwd()}\n')
    input('Press Enter, to exit: ')
except KeyboardInterrupt:
    close()
except Exception as ERROR:
    clear_terminal()
    print(f'Error:\n{ERROR}\n')
    input('Press Enter, to exit: ')
    close()