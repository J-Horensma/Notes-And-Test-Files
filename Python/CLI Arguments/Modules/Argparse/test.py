from sys import stderr, argv
from argparse import ArgumentParser

#NOTE: THIS IS HOW A PYTHON CLI, IS NORMALLY PARSED:

try:

    #START THE PARSER:
    PARSER = ArgumentParser()

    #DISPLAY THE HELP MENU, WHEN NO ARGUMENTS ARE PASSED, TO THIS FILE:
    if len(argv) == 1:
        PARSER.print_help(stderr)
        input('\nPress Enter, to exit: ')
        exit(0)

    #ADD ARGUMENTS, TO PARSE:
    PARSER.add_argument('--argument_1', help='The 1st argument')
    PARSER.add_argument('--argument_2', help='The 2nd argument')
    PARSER.add_argument('--argument_3', help='The 3rd argument')
    #NOTE: THE HELP SECTION, FOR EACH ARGUMENT, IS ADDED BY THE "help" OPTION.
    #NOTE: "argparse.ArgumentParser()", ACCEPTS ARGUMENT VALUES WITH SPACES, WHEN THE SPACED VALUES ARE QUOTED,
    #AND WILL RETURN THE SUPPLIED VALUES, WITHOUT QUOTES.
    
    #PARSE THE ARGUMENTS:
    ARGUMENTS = PARSER.parse_args()

    #DO SOMETHING, WITH THE ARGUMENTS:
    print(f'Argument 1: {ARGUMENTS.argument_1}')
    print(f'Argument 2: {ARGUMENTS.argument_2}')
    print(f'Argument 3: {ARGUMENTS.argument_3}')
    
except Exception as ERROR:
    print(ERROR)
    input('\nPress Enter, to exit: ')
    exit(1)
