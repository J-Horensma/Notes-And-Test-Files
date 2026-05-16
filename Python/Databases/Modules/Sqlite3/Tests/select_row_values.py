from os import system
from Functions.sqlite3_account_functions import select_row_values

while True:
    try:
        system('cls || clear')
        print('"select_row_values()" Test\n')

        #TO SELECT ROW VALUE/S, FROM A DATABASE TABLE, A DATABASE FILE PATH,
        #DATABASE TABLE NAME, COMMA SEPARATED COLUMN NAME/S, TO SELECT THE ROW VALUE/S FROM, 
        #COLUMN CONTAINING A UNIQUE IDENTIFYER FOR EACH ROW, AND THE UNIQUE ROW IDENTIFIER VALUE FOR THAT COLUMN,
        #ARE REQUIRED.
        DB_FILE_PATH = input('Enter a database file path: ')
        DB_TABLE_NAME = input('Enter a database table name: ')
        COLUMNS = input('Enter a comma separated list, of column/s, to select the value/s from: ')
        ROW_ID_COLUMN = input('Enter the name, of the column, containing the row identifying value: ')
        ROW_ID_VALUE = input('Enter the row identifying value, for the entered column: ')
        if not bool(select_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_ID_COLUMN, ROW_ID_VALUE)):
            raise Exception(f'[Exception], A row containing, the supplied row id value, in the cloumn: "{ROW_ID_COLUMN}",\ndoes not exist.')
        SELECTED_ROW_VALUES = select_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_ID_COLUMN, ROW_ID_VALUE)
        print(f'The selected row value/s list:\n{SELECTED_ROW_VALUES}\n')
    except Exception as ERROR:
        print(f'{ERROR}\n')
    input('Press Enter: ')
