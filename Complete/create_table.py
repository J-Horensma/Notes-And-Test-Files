from os import system
from Functions.sqlite3_account_functions import unquote, create_table

try:
    system('cls || clear')
    print('"create_table()" Test\n')

    #TO CREATE A DATABASE TABLE, DATABASE FILE PATH, DATABASE TABLE NAME,
    #AND COLUMN/S INFO STRINGS, ARE REQUIRED.
    DB_FILE_PATH = input('Enter a database file path: ')
    DB_TABLE_NAME = input('Enter a database table name: ')
    COLUMNS_INFO = '''
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    username TEXT NOT NULL UNIQUE,
    password_hash BLOB NOT NULL,
    salt BLOB NOT NULL
    '''

    create_table(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS_INFO)

    #THE "unquote()" FUNCTION, CAN UNQUOTE A STRING, IF THE STRING IS QUOTED.
    #THE "unquote()" FUNCTION, IS USEFUL, WHEN WORKING WITH TABLE NAMES.
    print(f'The table: "{unquote(DB_TABLE_NAME)}",\nwas created, in the database.\n')
except Exception as ERROR:
    print(f'{ERROR}\n')
input('Press Enter: ')