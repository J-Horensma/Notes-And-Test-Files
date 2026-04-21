from os import getcwd, chdir
from os.path import dirname
from time import sleep
from platform import system

#IF THIS FILE, IS LAUNCHED BY WINDOWS:
if system() == 'Windows':
    from subprocess import run, PIPE, CREATE_NO_WINDOW
    from colorama import just_fix_windows_console
    just_fix_windows_console()

#IF THIS FILE, IS LAUNCHED BY LINUX OR MAC:
else:
    from subprocess import run, PIPE

def clear_console():
   print('\033[H\033[2J', end='', flush=True)

def close():
    clear_console()
    print('Exiting...')
    sleep(1)
    exit(0)

def console(COMMAND):
    
    #NOTE: WORKS ON WINDOWS, LINUX, AND MAC
    
    #IF ON WINDOWS:
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

    #IF ON LINUX OR MAC:
    else:
        SHELL = run(
            COMMAND,
            shell=True,
            cwd=getcwd(),
            stdout=PIPE,
            stderr=PIPE,
            text=True
        )
    
    #THIS FUNCTION, RETURNS A TUPLE, INCLUDING OUTPUT, ERRORS, AND A RETURN CODE, INSTEAD OF CATCHING "subprocess" ERRORS WITH AN EXCEPTION.
    #THIS ENSURES, A REMOTE SHELL, CALLING THIS FUNCTION, DOES NOT HANG FROM A "subprocess" ERROR.
    return SHELL.stdout.strip(), SHELL.stderr.strip(), SHELL.returncode

try:
    while True:
        chdir(dirname(__file__))
        COMMAND = input(f'{getcwd()}>').strip()
        SHELL_OUTPUT, ERROR, RETURN_CODE = console(COMMAND)
        if RETURN_CODE == 0:
            print(f'{SHELL_OUTPUT}')
        else:
            print(f'{ERROR}\n')
except KeyboardInterrupt:
    close()
except Exception as ERROR:
    clear_console()
    print(f'{ERROR}\n')
    input('Press Enter, to exit: ')
    exit(1)