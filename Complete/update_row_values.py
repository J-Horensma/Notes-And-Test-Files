from os import system
from Functions.sqlite3_account_functions import unquote, select_row_values, update_row_values

while True:
    try:
        system('cls || clear')
        print('"update_row_values()" Test\n')
        
        #TO UPDATE THE ROW VALUE/S, IN A DATABASE TABLE, A DATABASE FILE PATH STRING, DATABASE TABLE NAME STRING,
        #COLUMN/S STRING, ROW VALUES LIST, ROW ID COLUMN STRING, AND ROW ID VALUE STRING, ARE REQUIRED.
        DB_FILE_PATH = input('Enter a database file path: ')
        DB_TABLE_NAME = input('Enter a database table name: ')
        COLUMNS = input('Enter a comma separated list, of column/s, to update the row value/s of: ')
        ROW_VALUES = input('Enter a comma spearated list, of row value/s, to insert, into the column/s: ')
        ROW_ID_COLUMN = input('Enter the name, of the column, containing the row identifying value: ')
        ROW_ID_VALUE = input('Enter the row identifying value, for the entered column: ')

        ROW_VALUES = ROW_VALUES.split(',')
        OLD_ROW_VALUES = select_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_ID_COLUMN, ROW_ID_VALUE)
        update_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_VALUES, ROW_ID_COLUMN, ROW_ID_VALUE)
        print(f'The column/s: {COLUMNS},')
        print(f'in the row identified by: {ROW_ID_VALUE}')
        print(f'was/were updated.\n')
    except Exception as ERROR:
        print(f'{ERROR}\n')
    input('Press Enter: ')