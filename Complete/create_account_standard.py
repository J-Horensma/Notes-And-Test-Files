from os import system
from Functions.sqlite3_account_functions import get_hash_and_salt, table_exists, create_table, aes_128_encrypt, insert_row_values

while True:
    try:
        system('cls || clear')
        print('Create Account Simulation (Standard Method)\n')
        print('Note: A database file (".db" or ".sqlite" file) must be created first.')
        
        #TO CREATE AN ACCOUNT ROW, IN THE DATABASE TABLE,
        #WITH THE "insert_row_values()" FUNCTION, A DATABASE FILE PATH STRING, 
        #DATABASE TABLE NAME STRING, ACCOUNT INFORMATION STRINGS, PASSWORD HASH BYTES, AND SALT BYTES, ARE REQUIRED.
        DB_FILE_PATH = input('Enter a database file path: ')
        DB_TABLE_NAME = input('Enter a database table name: ')
        USERNAME = input('Enter a username: ')
        PASSWORD = input('Enter a password: ')

        print('\nCreating a 16 byte length salt and a 32 byte length password hash...')

        #TO GET A SECURE PASSWORD HASH, THAT CANNOT BE REVERTED,
        #TO THE ORIGINAL PASSWORD, THE "get_hash_and_salt()" FUNCTION, CAN BE USED.
        PASSWORD_HASH_BYTES, SALT_BYTES = get_hash_and_salt(PASSWORD)

        print('Successfully created, a password hash and salt!')
        print(f'Password hash: {PASSWORD_HASH_BYTES}')
        print(f'Salt: {SALT_BYTES}\n')
        print('Verifying the database table exists...')
        if not table_exists(DB_FILE_PATH, DB_TABLE_NAME):
            print('The database table, does not exist, creating the table...')

            #WHEN INSERTING BYTES TYPE/S, INTO THE DATABASE,
            #"BLOB" COLUMN/S, IS/ARE NECCESSARY.
            COLUMNS_INFO = '''
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash BLOB NOT NULL,
            salt BLOB NOT NULL
            '''

            create_table(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS_INFO)
            print('The database table, was created successfully!\n')
        else:
            print('The database table, already exists!\n')
        print('Attempting to insert the new account details, into the database...')
        insert_row_values(DB_FILE_PATH, DB_TABLE_NAME, 'username, password_hash, salt', [USERNAME, PASSWORD_HASH_BYTES, SALT_BYTES])
        print('Successfully created, an account!\n')
        input('Press Enter: ')
        
    #TO CATCH AN EXCEPTION, FOR AN ATTEMPTED INSERT, OF A ROW VALUE, THAT HAS A COLUMN, 
    #CONTAINING A "UNIQUE" CONSTRAINT (DATABASE TABLE RULE, THAT ONLY ONE OF THAT VALUE, CAN EXIST, IN THAT COLUMN, OF THE TABLE), 
    #IN THE DATABASE, LIKE "username", ABOVE, USE THE BELOW:
    except Exception as ERROR:
        if 'UNIQUE constraint failed:' in str(ERROR):
            print('The entered username, already exists!\n')
        else:
            print(f'{ERROR}\n')
        input('Press Enter: ')
        continue