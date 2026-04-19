from os import environ
from os import getcwd
from os import chdir
from os.path import isabs
from os.path import expandvars
from os.path import normpath
from os.path import realpath
from os.path import dirname
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

#CHANGE THE CWD TO THIS FILES PATH,
#SO "os.path.realpath()", CONVERTS DOT-MATRIXES IN RELATION TO THE PATH OF THIS FILE,
#INSTEAD OF THE DEFAULT PYTHON PROFILE PATH.
chdir(dirname(__file__))

#ADD WINDOWS ENVIRONMENT VARIABLES, NOT INCLUDED IN THE "os.path.expandvars()" FUNCTION
environ['CD'] = dirname(__file__) 

try:
    PATH = input('Enter a path, to convert: ')
    if PATH:
        EXPANDED_VARIABLES = expandvars(PATH)
        print(f'\nExpanded environment variables:\n{EXPANDED_VARIABLES}\n')
        OS_NORMALIZED_PATH = normpath(EXPANDED_VARIABLES)
        print(f'OS normalized slashes:\n{OS_NORMALIZED_PATH}\n')

        #THE "os.path.abspath()" AND "os.path.realpath()" FUNCTIONS,
        #PREPEND NON-ABSOLUTE PATHS, WITH THE CWD.
        #TO AVOID THIS, WITH NON-EXISTING PATHS OR ENVIRONMENT VARIABLES,
        #THAT DO NOT RETURN A PATH, LIKE "%USERNAME%", USE THE BELOW METHOD:
        if isabs(OS_NORMALIZED_PATH):
            RESOLVED_PATH = OS_NORMALIZED_PATH
        elif '.' in OS_NORMALIZED_PATH:
            RESOLVED_PATH = realpath(OS_NORMALIZED_PATH)
        else:
            RESOLVED_PATH = OS_NORMALIZED_PATH
        print(f'Resolved dot-sequences and symbolic links:\n{RESOLVED_PATH}\n')
        input('Press Enter, to exit: ')
except KeyboardInterrupt:
    close()
except Exception as ERROR:
    clear_terminal()
    print(f'Error:\n{ERROR}\n')
    input('Press Enter, to exit: ')
    close()