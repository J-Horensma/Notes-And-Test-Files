from os import system
from Functions.sqlite3_account_functions import table_exists

while True:
    try:
        system('cls || clear')
        print('"table_exists()" Test\n')
        print('Note: Normally, when querying a database table, with special characters in the table name,')
        print('you must surround the table name, in quotes, the opposite is true, when checking if a table exists,')
        print('with the "table_exists()" function.')
        print('The "table_exists()" function, only returns "True" or "False" (No errors),')
        print('so a quoted table name, will not be caught.\n')
        
        #TO CHECK IF A DATABASE TABLE EXISTS, IN THE DATABASE,
        #DATABASE FILE PATH AND DATABASE TABLE NAME STRINGS, ARE REQUIRED.
        DB_FILE_PATH = input('Enter a database file path: ')
        DB_TABLE_NAME = input('Enter a database table name: ')
        
        BOOLEAN = table_exists(DB_FILE_PATH, DB_TABLE_NAME)
        print(f'Database table exists: {BOOLEAN}\n')
    except Exception as ERROR:
        print(f'{ERROR}\n')
    input('Press Enter: ')