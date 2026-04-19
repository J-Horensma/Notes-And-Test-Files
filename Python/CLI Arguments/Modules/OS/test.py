from sys import exit
from time import sleep
from argparse import ArgumentParser
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
    #START THE PARSER
    PARSER = ArgumentParser()

    #ADD ARGUMENTS TO PARSE:
    PARSER.add_argument('--argument_1', help="The 1st argument")
    PARSER.add_argument('--argument_2', help="The 2nd argument")
    PARSER.add_argument('--argument_3', help="The 3rd argument")
    #NOTE: THE PARSER ACCEPTS ARGUMENTS WITH SPACES, WHEN THE ARGUMENTS ARE QUOTED,
    #AND WILL OUTPUT THE ARGUMENTS WITH SPACES, WITHOUT THE QUOTES.
    
    #START THE PARSER
    ARGUMENTS = PARSER.parse_args()

    #DO SOMETHING WITH THE ARGUMENTS:
    print(f'Argument 1: {ARGUMENTS.argument_1}')
    print(f'Argument 2: {ARGUMENTS.argument_2}')
    print(f'Argument 3: {ARGUMENTS.argument_3}')
    input('Press Enter to continue...')
except KeyboardInterrupt:
    close()
except Exception as ERROR:
    clear_terminal()
    print(f'{ERROR}\n')
    input('Press Enter, to exit: ')
    close()