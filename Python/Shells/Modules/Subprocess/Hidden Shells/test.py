from sys import argv
from os import name, getcwd, chdir
from os.path import dirname
from time import sleep
import subprocess
from colorama import just_fix_windows_console

def clear_terminal():
   print('\033[H\033[2J', end='', flush=True)

def close():
    clear_terminal()
    print('Exiting...')
    sleep(1)
    exit()

just_fix_windows_console()

def hidden_shell(COMMAND):
    try:

        #IF ON WINDOWS
        if name == 'nt': 
            SHELL = subprocess.run(
                COMMAND,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

        #IF ON LINUX OR MAC
        else:
            SHELL = subprocess.run(
                COMMAND,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        return SHELL.stdout.strip(), SHELL.stderr.strip(), SHELL.returncode
    except Exception as ERROR:
        return '', str(ERROR), 1

try:
    while True:
        chdir(dirname(__file__))
        COMMAND = input(f'{getcwd()}>').strip()
        SHELL_OUTPUT, ERROR, RETURN_CODE = hidden_shell(COMMAND)

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