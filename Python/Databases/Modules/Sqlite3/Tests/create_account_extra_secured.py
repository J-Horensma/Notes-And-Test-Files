from os import system
from Functions.general_db_functions import get_hash_and_salt, table_exists, create_table, aes_128_encrypt, insert_row_values

while True:
    try:
        system('cls || clear')
        print('Create Account Simulation (Using An AES128 Bit Encrypted Password Hash)\n')
        print('Note: A database file (".db" or ".sqlite" file) and a database table, must be created first.')
        print('A database table, can be created, with the "create_table()" function (This test does that automatically, if the table, does not exist).')
        print('To check if a database table exists, the "table_exists()" function, can be used.')
        print('The "create_table.py" test file, can be used, to create a database table, with the "create_table()" function.\n')
        DB_FILE_PATH = input('Enter a database file path: ')
        DB_TABLE_NAME = input('Enter a database table name: ')
        USERNAME = input('Enter a username: ')
        PASSWORD = input('Enter a password: ')
        print('\nCreating a 16 byte length salt and a 32 byte length password hash...')
        PASSWORD_HASH_BYTES, SALT_BYTES = get_hash_and_salt(PASSWORD)
        print('Successfully created, a salt and password hash!\n')
        print('Verifying the database table exists...')
        if not table_exists(DB_FILE_PATH, DB_TABLE_NAME):
            print('The database table, does not exist, creating the table...')
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
        print('Encrypting the password hash, with the password hash, as a key,')
        print('before inserting it, into the DB...')
        
        #THE STANDARD CREATE ACCOUNT PROCESS, IS TO STORE A PASSWORD HASH AND SALT IN THE DATABASE,
        #(UNENCRYPTED, WHILE ENCRYPTING OTHER VALUES), THEN USE THE STORED SALT AND THE USER'S ENTERED PASSWORD, TO CREATE A NEW PASSWORD HASH,
        #THAT CAN BE MATCHED, TO THE STORED PASSWORD HASH. 
        #THE STANDARD METHOD, IS SECURE FROM EVERYONE, EXCEPT A DATABASE ADMIN,
        #BECAUSE THE PASSWORD HASH, USED TO DECRYPT THE OTHER VALUES, IS UNENCRYPTED AND VISIBLE TO A DATABASE ADMIN.
        #THIS PROCESS DOES THAT, BUT ENCRYPTS THE PASSWORD HASH, STORED ON THE DATABASE,
        #SO EVEN THE DATABASE ADMIN, CANNOT VIEW THE ENCRYPTED ITEMS,
        #WITHOUT THE USER'S PASSWORD, TO CREATE A MATCHING PASSWORD HASH, TO DECRYPT THE ENCRYPTED VALUES.
        #THE "aes_128_encrypt()" FUNCTION, ACCEPTS BOTH STRINGS AND BYTES, AS THE STRING PARAMETER, TO ENCRYPT.
        ENCRYPTED_PASSWORD_HASH_BYTES = aes_128_encrypt(PASSWORD_HASH, PASSWORD_HASH)

        print('Successfully encrypted, the password')
        print(f'Encrypted password hash bytes: {ENCRYPTED_HASH_BYTES}\n')
        print('Attempting to insert the new account details, into the database...')
        insert_row_values(DB_FILE_PATH, DB_TABLE_NAME, 'username, password_hash, salt', [USERNAME, ENCRYPTED_PASSWORD_HASH_BYTES, SALT_BYTES])
        print('Successfully created, an account!\n')
        input('Press Enter: ')
    except Exception as ERROR:
        if 'UNIQUE constraint failed:' in str(ERROR):
            print('The entered username, already exists!\n')
        else:
            print(f'{ERROR}\n')
        input('Press Enter: ')
        continue
