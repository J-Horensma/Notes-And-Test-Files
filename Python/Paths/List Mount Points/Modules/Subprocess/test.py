from os import getcwd
from os.path import exists
from string import ascii_uppercase
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

def list_mounts():

    #NOTE: WORKS ON WINDOWS AND LINUX

    #IF ON WINDOWS:
    if system() == 'Windows':

        #NOTE: IN PYTHON, DOUBLE BACKSLASHES ("\\") ARE OUTPUT AS A SINGLE BACKSLASH ("\").
        #A SECOND BACKSLASH ("\"), IS NECCESSARY TO ESCAPE THE ESCAPE CHARACTER BACKSLASH ("\"), ITSELF.
        MOUNT_POINTS = [f"{MOUNT}:\\" for MOUNT in ascii_uppercase if exists(f"{MOUNT}:\\")]
        return MOUNT_POINTS
    
    #IF ON LINUX:
    elif system() == 'Linux':
        OUTPUT, ERROR, RETURN_CODE = console("findmnt | awk '{print $1}'")
        if not ERROR:
            MOUNT_POINTS = []
            for LINE in OUTPUT.split('\n'):
                if LINE != 'TARGET' and len(LINE) > 1:
                    MOUNT_POINTS.append(LINE[2:].strip())
            return MOUNT_POINTS
        else:
            raise OSError(f'Error: "list_mounts()"\nUnable to list mount-points\nMake sure the "util-linux" package, is installed')
    else:
        raise OSError(f'''Error: "list_mounts()":\nOnly supports Windows and Linux\nMac OS and other OS', are not yet supported''')
    
try:
    while True:
        clear_console()
        print('Mount-point list:')
        print('-----------------')
        MOUNT_POINTS = list_mounts()
        for LINE in MOUNT_POINTS:
            if LINE is not None:
                print(LINE)
        input('\nPress Enter, to try again: ')
except KeyboardInterrupt:
    close()
except Exception as ERROR:
    print(f'{ERROR}\n')
    input('Press Enter, to exit: ')
    exit(1)