from os import system
from Functions.sqlite3_account_functions import get_hash_and_salt, table_exists, create_table, aes_128_decrypt, select_row_values, is_password_valid

while True:
    try:
        system('cls || clear')
        print('Account Login Simulation (Standard Method)\n')

        #TO SELECT AN ACCOUNT'S ROW VALUE/S, FROM A DATABASE TABLE,
        #WITH THE "select_row_values()" FUNCTION, A DATABASE FILE PATH,
        #DATABASE TABLE NAME, COMMA SEPARATED COLUMN NAME/S, TO SELECT THE ROW VALUE/S FROM, 
        #COLUMN CONTAINING A UNIQUE IDENTIFYER FOR EACH ROW, THE UNIQUE ROW IDENTIFIER VALUE, FOR THAT COLUMN,
        #THE USERNAME, AND THE PASSWORD, ARE REQUIRED.
        DB_FILE_PATH = input('Enter a database file path: ')
        DB_TABLE_NAME = input('Enter a database table name: ')
        COLUMNS = 'password_hash, salt'
        ROW_ID_COLUMN = 'username'
        USERNAME = input('Enter your username: ')
        ROW_ID_VALUE = USERNAME
        PASSWORD = input('Enter your password: ')
        
        if select_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_ID_COLUMN, ROW_ID_VALUE):
            SELECTED_ROW_VALUES = select_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_ID_COLUMN, ROW_ID_VALUE)
            STORED_PASSWORD_HASH_BYTES = SELECTED_ROW_VALUES[0]
            STORED_SALT_BYTES = SELECTED_ROW_VALUES[1]
            print('Successfully selected, the database stored password hash and salt!')
            print(f'Database stored password hash:\n{STORED_PASSWORD_HASH_BYTES}')
            print(f'Database stored salt:\n{STORED_SALT_BYTES}\n')
        else:
            raise Exception(f'An account for: {USERNAME}\ndoes not exist.')
        print('Creating a new password hash, with the user entered password and database stored salt...')
        NEW_PASSWORD_HASH_BYTES, STORED_SALT_BYTES = get_hash_and_salt(PASSWORD, STORED_SALT_BYTES)
        print(f'New password hash:\n{NEW_PASSWORD_HASH_BYTES}\n')
        print('Matching the database stored password hash, to the new password hash,')
        print('created by the user entered password and the database stored salt...')
        
        #IN A STANDARD LOGIN METHOD, THE UNENCRYPTED DATABASE STORED PASSWORD HASH, 
        #IS MATCHED TO A NEW PASSWORD HASH, CREATED WITH THE USER'S ENTERED PASSWORD
        #AND THE UNENCRYPTED DATABASE STORED SALT, USED TO CREATE THE ORIGINAL PASSWORD HASH.
        #THE "is_password_valid()" FUNCTION, CAN BE USED, IN THE STANDARD METHOD, TO PASSWORD HASH MATCH.
        if not is_password_valid(PASSWORD, STORED_PASSWORD_HASH_BYTES, STORED_SALT_BYTES):
            print('The incorrect password, was entered!\n')
        else:
            print('The password, was correct, login successful!\n')

        input('Press Enter: ')
    except Exception as ERROR:
        print(f'{ERROR}\n')
        input('Press Enter: ')
        continue