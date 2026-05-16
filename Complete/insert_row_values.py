from os import system
from Functions.sqlite3_account_functions import unquote, insert_row_values

while True:
    try:
        system('cls || clear')
        print('"insert_row_values()" Test\n')

        #TO INSERT ROW VALUES, INTO A DATABASE TABLE, A DATABASE FILE PATH STRING,
        #DATABASE TABLE NAME STRING, COLUMN/S STRING, AND A ROW VALUES LIST, ARE REQUIRED.
        DB_FILE_PATH = input('Enter a database file path: ')
        DB_TABLE_NAME = input('Enter a database table name: ')
        COLUMNS = input('Enter a comma separated list, of column/s, to insert row value/s into: ')
        ROW_VALUES = input('Enter a comma spearated list, of row value/s, to insert, into the column/s: ')
        
        ROW_VALUES = ROW_VALUES.split(',')
        insert_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_VALUES)
        print(f'The row value/s:\n{ROW_VALUES},\nwas/were inserted, into the column/s: {COLUMNS}\nin the database table: "{unquote(DB_TABLE_NAME)}".\n')
    except Exception as ERROR:
        print(f'{ERROR}\n')
    input('Press Enter: ')