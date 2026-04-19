from os import environ, getcwd, chdir
from os.path import expandvars, normpath, realpath, dirname
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

#CHANGE THE CWD, WITH "os.chdir()", TO THIS FILES PATH,
#SO "os.path.realpath()", CONVERTS DOT-MATRIXES IN RELATION TO THE PATH OF THIS FILE,
#INSTEAD OF THE DEFAULT PYTHON PROFILE PATH, AS "os.path.realpath()" RELATES NON-ABSOLUTE PATHS, WITH THE CWD.
chdir(dirname(__file__))

#ADD WINDOWS ENVIRONMENT VARIABLES, NOT INCLUDED IN THE "os.path.expandvars()" FUNCTION
environ['CD'] = getcwd()

try:
    while True:
        clear_terminal()
        PATH = input('Enter a path, to convert: ')
        if not PATH:
                print('Empty input, was provided\n')
                input('Press Enter, to try again: ')
                clear_terminal()
                continue
        EXPANDED_VARIABLES = expandvars(PATH)
        print(f'\nExpanded environment variables:\n{EXPANDED_VARIABLES}\n')
        OS_NORMALIZED_PATH = normpath(EXPANDED_VARIABLES)
        print(f'OS normalized slashes:\n{OS_NORMALIZED_PATH}\n')

        #THE "os.path.abspath()" AND "os.path.realpath()" FUNCTIONS,
        #PREPEND NON-ABSOLUTE PATHS, WITH THE CWD.
        #TO AVOID THIS, WITH NON-EXISTING PATHS OR ENVIRONMENT VARIABLES,
        #THAT DO NOT RETURN A PATH, LIKE "%USERNAME%", USE THE BELOW METHOD:
        if '.' in OS_NORMALIZED_PATH:
            RESOLVED_PATH = realpath(OS_NORMALIZED_PATH)
        else:
            RESOLVED_PATH = OS_NORMALIZED_PATH
        print(f'Resolved dot-sequences and symbolic links:\n{RESOLVED_PATH}\n')
        input('Press Enter, to try again: ')
except KeyboardInterrupt:
    close()
except Exception as ERROR:
    clear_terminal()
    print(f'{ERROR}\n')
    input('Press Enter, to exit: ')
    close()