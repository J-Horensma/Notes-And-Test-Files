from os import getcwd, chdir
from os.path import dirname
from platform import system
from time import sleep
from subprocess import run, PIPE, CREATE_NO_WINDOW
from colorama import just_fix_windows_console

def clear_terminal():
   print('\033[H\033[2J', end='', flush=True)

def close():
    clear_terminal()
    print('Exiting...')
    sleep(1)
    exit()

just_fix_windows_console()

def shell(COMMAND):
        
        #NOTE: WORKS ON WINDOWS, LINUX, AND MAC
        
        #IF ON WINDOWS
            if system() == 'Windows': 
                SHELL = run(
                    COMMAND,
                    shell=True,
                    cwd=getcwd(),
                    creationflags=CREATE_NO_WINDOW,
                    stdout=PIPE,
                    stderr=PIPE,
                    text=True
                )

            #IF ON LINUX OR MAC
            else:
                SHELL = run(
                    COMMAND,
                    shell=True,
                    cwd=getcwd(),
                    stdout=PIPE,
                    stderr=PIPE,
                    text=True
                )
            
            #THIS FUNCTION, RETURNS A TUPLE, INCLUDING THE "subprocess" RETURN STRING, ANY ERRORS, AND A RETURN CODE, INSTEAD OF CATCHING "subprocess" ERRORS WITH AN EXCEPTION.
            #THIS ENSURES, A REMOTE SHELL CALLING THIS FUNCTION, DOES NOT HANG FROM A "subprocess" ERROR.
            return SHELL.stdout.strip(), SHELL.stderr.strip(), SHELL.returncode

try:
    while True:
        chdir(dirname(__file__))
        COMMAND = input(f'{getcwd()}>').strip()
        SHELL_OUTPUT, ERROR, RETURN_CODE = shell(COMMAND)

        if RETURN_CODE == 0:
            print(f'{SHELL_OUTPUT}')
        else:
            print(f'{ERROR}\n')
            input('Press Enter, to exit: ')
            close()
except KeyboardInterrupt:
    close()
except Exception as ERROR:
    clear_terminal()
    print(f'{ERROR}\n')
    input('Press Enter, to exit: ')
    close()