from os import getcwd, chdir
from os.path import basename, dirname
from sys import exit, argv
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
        print(f'Launched by:\nThis file\n')
        print(f'File name:\n{basename(__file__)}\n')
        print(f"File's CWD:\n{getcwd()}\n")
    elif dirname(argv[0]) == getcwd():
        print(f'Launched by:\nPython import\n')
        print(f'Importing file:\n{basename(argv[0])}\n')
        print(f"Importing file's CWD:\n{dirname(argv[0])}\n")
    else:
        print(f'Launched by:\nShell process\n')
        print(f'Shell process CWD:\n{getcwd()}\n')
    input('Press Enter, to exit: ')
except KeyboardInterrupt:
    close()
except Exception as ERROR:
    clear_terminal()
    print(f'{ERROR}\n')
    input('Press Enter, to exit: ')
    close()