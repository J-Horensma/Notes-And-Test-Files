from os import system
from Functions.general_db_functions import get_hash_and_salt, table_exists, create_table, aes_128_decrypt, select_row_values, is_password_valid

while True:
    try:
        system('cls || clear')
        print('Account Login Simulation (Using An AES128 Bit Encrypted Password Hash)\n')
        DB_FILE_PATH = input('Enter a database file path: ')
        DB_TABLE_NAME = input('Enter a database table name: ')
        COLUMNS = 'password_hash, salt'
        USERNAME = input('Enter your username: ')
        ROW_ID_COLUMN = 'username'
        ROW_ID_VALUE = USERNAME
        PASSWORD = input('Enter your password: ')
        print('Selecting the database stored encrypted password hash and salt bytes, for that username...')
        if select_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_ID_COLUMN, ROW_ID_VALUE):
            SELECTED_ROW_VALUES = select_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_ID_COLUMN, ROW_ID_VALUE)
            ENCRYPTED_STORED_PASSWORD_HASH_BYTES = SELECTED_ROW_VALUES[0]
            STORED_SALT_BYTES = SELECTED_ROW_VALUES[1]
            print('Successfully selected, the stored hash and salt, from the database!')
            print(f'Database stored encrypted password hash: {ENCRYPTED_STORED_PASSWORD_HASH_BYTES}')
            print(f'Database stored salt: {STORED_SALT_BYTES}\n')
        else:
            raise ValueError('No account exists, for that username!\n')
        print("Creating a new password hash, with the user's entered password and database stored salt...")
        NEW_PASSWORD_HASH_BYTES, STORED_SALT_BYTES = get_hash_and_salt(PASSWORD, STORED_SALT_BYTES)
        print(f'New password hash: {NEW_PASSWORD_HASH_BYTES}')
        print('Decrypting, the stored password hash...')

        #IN THE "login_extra_secured.py" VERSION, "bool()", CAN BE USED TO CAPTURE A "True" OR "False",
        #IN ORDER TO DETERMINE IF THE "aes_128_decrypt()" FUNCTION, WAS SUCCESSFUL.
        #IF THE OPERATION RETURNS "False", WHEN "bool()" IS USED,
        #THE DATABASE STORED PASSWORD HASH, DOES NOT MATCH THE PASSWORD HASH,
        #CREATED BY THE USER'S ENTERED PASSWORD AND THE DATABASE STORED SALT.
        #WHEN THIS EXTRA SECURED LOGIN METHOD IS USED, THE FAILED DECRYPTION,
        #OF THE PASSWORD HASH, DETERMINES IF THE USER'S ENTERED PASSWORD,
        #WAS CORRECT. IN A STANDARD LOGIN METHOD, THE UNENCRYPTED PASSWORD HASHES CAN BE MATCHED, WITH THE "is_password_valid()" FUNCTION.
        if not bool(aes_128_decrypt(ENCRYPTED_STORED_PASSWORD_HASH_BYTES, NEW_PASSWORD_HASH_BYTES)):
            print('The incorrect password, was entered!\n')
        else:
            print('The password, was correct, login was successful!\n')
            
        input('Press Enter: ')
    except Exception as ERROR:
        print(f'{ERROR}\n')
        input('Press Enter: ')
        continue