from os import system
from Functions.sqlite3_account_functions import delete_row

while True:
    try:
        system('cls || clear')
        print('"delete_row()" Test\n')

        #TO DELETE A ROW, FROM A DATABASE TABLE, A DATABASE FILE PATH,
        #DATABASE TABLE NAME, COLUMN CONTAINING A UNIQUE IDENTIFYER FOR EACH ROW, 
        #AND THE UNIQUE ROW VALUE FOR THAT COLUMN, ARE REQUIRED.
        DB_FILE_PATH = input('Enter a database file path: ')
        DB_TABLE_NAME = input('Enter a database table name: ')
        ROW_ID_COLUMN = input('Enter the name, of the column, containing the row identifying value: ')
        ROW_ID_VALUE = input('Enter the row identifying value, for the entered column: ')

        delete_row(DB_FILE_PATH, DB_TABLE_NAME, ROW_ID_COLUMN, ROW_ID_VALUE)
        print(f'The row identified, by the row identifying value: "{ROW_ID_VALUE}",\nwas deleted.\n')
    except Exception as ERROR:
        print(f'{ERROR}\n')
    input('Press Enter: ')