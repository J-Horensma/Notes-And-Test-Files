from sys import argv
from os import getcwd, chdir
from os.path import basename, dirname
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
    print('''NOTE:\nIn order to read the launching process' CWD, from this file, "sys.argv[0]" is used.''')
    print('The "sys.argv" list, returns the full path to the CWD, of the process launching the file,')
    print('as the first list entry (0), except when the file itself calls it, then it returns the name of the file.\n')
    
    #IF THIS FILES NAME ("__file__"), MATCHES THE FIRST ENTRY IN THE "sys.argv" LIST, 
    #IT IS THIS FILE CALLING THE CODE
    if __file__ == argv[0]:
        chdir(dirname(__file__))
        print(f'Launched by:\nThis file\n')
        print(f'File name:\n{basename(__file__)}\n')
        print(f"File's CWD:\n{getcwd()}\n")
    
    #NOTE: AN IMPORTING PYTHON FILE, MUST USE "os.chdir(os.path.dirname(__file__))",
    #BEFORE IMPORTING THIS FILE, IN ORDER FOR "os.getcwd()", TO BE MATCHED TO "os.path.dirname(sys.argv[0])".
    #IF "os.getcwd()" MATCHES "os.path.dirname(sys.argv[0])", ANOTHER PYTHON FILE IS IMPORTING THIS FILE.
    elif getcwd() == dirname(argv[0]):
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