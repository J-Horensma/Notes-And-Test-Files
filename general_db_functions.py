from os.path import exists, isabs, isfile
from inspect import currentframe
import ast
from re import fullmatch
from sqlite3 import connect
from base64 import urlsafe_b64encode, urlsafe_b64decode
from secrets import token_bytes, compare_digest
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

#NOTE: WHEN CREATING AN "sqlite3" DATABASE TABLE WITH SPECIAL CHARACTERS
#(CHARACTERS OTHER THAN aA-zZ, 0-9, and "_"),
#YOU MUST USE A TABLE NAME, WITH QUOTES SURROUNDING THE NAME. 
#THIS MAY GET CONFUSING, WHEN QUERYING THE DB FOR THAT TABLE NAME,
#AS THE DB STORES IT WITHOUT THE SURROUNDING QUOTES.
#WHEN QUERYING THE DB FOR A TABLE NAME, THAT INCLUDES SPECIAL CHARACTERS,
#DO NOT INCLUDE THE SURROUNDING QUOTES, USED TO CREATE THE TABLE, IN THE QUERY.
#THE SURROUNDING QUOTES, ARE ONLY USED TO CREATE A TABLE WITH SPECIAL CHARACTERS,
#NOT TO QUERY A TABLE, WITH SPECIAL CHARACTERS.

#NOTE: THE "unquote()" FUNCTION, CAN BE USED TO UNQUOTE A DATABASE TABLE NAME.

#THIS FUNCTION:
#1.) REQUIRES A LIST
#2.) ITERATES EVERY ITEM, IN THE LIST, AND STRIPS ALL STRING TYPE ITEMS
#3.) RETURNS A LIST, WITH ALL STRING TYPE ITEMS, STRIPPED
def strip_all(LIST):
    if not isinstance(LIST, list):
        raise ValueError('[ValueError]\nFunction: "strip_all()"\nThe supplied value, was not a list type.')
    else:
        LIST = [VALUE.strip() if isinstance(VALUE, str) else VALUE for VALUE in LIST]
        return LIST

#THIS FUNCTION:
#1.) REQUIRES A LIST AND AN OBJECT TYPE
#2.) ITERATES EVERY ITEM, IN THE LIST, AND CHECKS IF ALL ITEMS ARE THE SPECIFIED OBJECT TYPE
#3.) RETURNS "True" IF ALL ITEMS, IN THE LIST, ARE THE SPECIFIED OBJECT TYPE, OR "False",
#IF 1 OR MORE ITEM/S, IN THE LIST, ARE NOT THE SPECIFIED OBJECT TYPE
def all_items_are(LIST, TYPE):
    BOOLEAN = True if all([isinstance(ITEM, TYPE) for ITEM in LIST]) else False
    return BOOLEAN

#THIS FUNCTION:
#1.) REQUIRES A DATABASE FILE PATH STRING
#2.) CHECKS FOR DATABASE FILE PATH ERRORS
#3.) RAISES ANY ERRORS FOUND
def db_file_path_error_check(DB_FILE_PATH):
    if not isinstance(DB_FILE_PATH, str):
        raise TypeError(f'[TypeError]\nFunction: "{currentframe().f_back.f_code.co_name}()"\nThe supplied database file path, was not a string.')
    if not DB_FILE_PATH.strip():
        raise ValueError(f'[ValueError]\nFunction: "{currentframe().f_back.f_code.co_name}()"\nThe supplied database file path, was empty.')
    if not isabs(DB_FILE_PATH):
        raise ValueError(f'[ValueError]\nFunction: "{currentframe().f_back.f_code.co_name}()"\nThe supplied database file path, was not an absolute path.')
    if not exists(DB_FILE_PATH):
        raise FileNotFoundError(f'[FileNotFoundError]\nFunction: "{currentframe().f_back.f_code.co_name}()"\nThe supplied database file path, does not exist.')
    if not isfile(DB_FILE_PATH):
        raise FileNotFoundError(f'[ValueError]\nFunction: "{currentframe().f_back.f_code.co_name}()"\nThe supplied database file path, was not a path to a file.')

#THIS FUNCTION:
#1.) REQUIRES A STRING
#2.) CHECKS IF THE STRING IS QUOTED
#3.) RETURNS "True", IF THE STRING IS QUOTED, OR "False", IF THE STRING IS NOT QUOTED
def is_quoted(STRING):
    if STRING[0] == STRING[-1] and STRING[0] in ("'", '"') and STRING.count(STRING[0]) == 2:
        return True
    else:
        return False
    
#THIS FUNCTION:
#1.) REQUIRES A STRING
#2.) CHECKS IF THE STRING IS QUOTED
#3.) RETURNS THE STRING, UNQUOTED
def unquote(STRING):
    if not isinstance(STRING, str):
        raise TypeError('[TypeError]\nFunction: "unquote()"\nThe supplied string parameter, was not a string type.')
    if not STRING.strip():
        raise ValueError('[ValueError]\nFunction: "unquote()"\nThe supplied string parameter, was empty.')
    if STRING[0] == STRING[-1] and STRING[0] in ("'", '"') and STRING.count(STRING[0]) == 2:
        STRING = STRING.replace(STRING[0], '')
        return STRING
    else:
        return STRING

#THIS FUNCTION:
#1.) REQUIRES A STRING AND PASSWORD HASH BYTES
#2.) ENCRYPTS THE STRING TO AES-128 ENCRYPTED BYTES, USING THE SUPPLIED PASSWORD HASH BYTES,
#AS A KEY, FOR THE ENCRYPTION
#3.) RETURNS THE STRING, "AES-128" BIT ENCRYPTED
def aes_128_encrypt(ENCRYPTED_STRING_BYTES, HASH_BYTES):
    #if not all((isinstance(VALUE, bytes) for VALUE in (STRING, HASH_BYTES))):
        #raise TypeError(f'[TypeError]\nFunction: "aes_128_encrypt()"\nOne or more, supplied parameter/s, were not the correct type.')
    #if not all((VALUE.strip() for VALUE in (STRING, HASH_BYTES))):
        #raise ValueError(f'[ValueError]\nFunction: "aes_128_encrypt()"\nOne or more, supplied parameter/s, were empty.')
    CIPHER = Fernet(urlsafe_b64encode(HASH_BYTES))
    ENCRYPTED_STRING_BYTES = CIPHER.encrypt(ENCRYPTED_STRING_BYTES).decode()
    return ENCRYPTED_STRING_BYTES

#THIS FUNCTION:
#1.) REQUIRES A "AES-128" BIT ENCRYPTED STRING AND PASSWORD HASH BYTES
#2.) DECRYPTS THE "AES-128" BIT ENCRYPTED STRING, USING THE PASSWORD HASH BYTES,
#THAT WAS USED TO ENCRYPT THE STRING, AND DECODES THE DECRYPTED BYTES TO A STRING
#3.) RETURNS THE DECRYPTED STRING
def aes_128_decrypt(DECODED_ENCRYPTED_BYTES, HASH_BYTES):
    #if not all((isinstance(VALUE, str) for VALUE in (ENCRYPTED_BYTES, HASH_BYTES))):
        #raise TypeError(f'[TypeError]\nFunction: "aes_128_decrypt()"\nOne or more, supplied parameter/s, were not the correct type.')
    #if not all((VALUE.strip() for VALUE in (ENCRYPTED_BYTES, PASSWORD_HASH))):
        #raise ValueError(f'[ValueError]\nFunction: "aes_128_decrypt()"\nThe supplied encrypted string parameter, was empty.')
    CIPHER = Fernet(urlsafe_b64encode(HASH_BYTES))
    PLAINTEXT_STRING = CIPHER.decrypt(DECODED_ENCRYPTED_BYTES)
    return PLAINTEXT_STRING

#THIS FUNCTION:
#1.) REQUIRES A STRING AND ACCEPTS AN OPTIONAL SALT BYTES PARAMETER
#2.) CREATES RANDOM SALT BYTES (IF NOT SUPPLIED, WITH THE OPTIONAL SALT BYTES PARAMETER)
#3.) ENCODES THE STRING TO BYTES, USING UTF-8 ENCODING
#4.) HASHES THE STRING BYTES AND SALT BYTES, WITH THE PBKDF2 HMAC HASHING ALGORITHM, 
#USING THE "SHA256" HASH FUNCTION, AND 200,000 ITERATIONS
#5.) RETURNS THE STRING HASH BYTES AND SALT HASH BYTES, AS A TUPLE
#NOTE: THIS FUNCTION, MEETS THE CRITERIA FOR "RFC 8018" AND "NIST SP 800‑63B",
#MEANING IT MEETS THE SECURITY STANDARDS FOR HASHING PASSWORDS AND GENERATING SALTS, 
#TO BE STORED IN A DATABASE, FOR LATER PASSWORD VERIFICATION.
def get_hash_and_salt(STRING_BYTES, SALT=None):
    SALT = token_bytes(16) if SALT is None else SALT
    HASH_BYTES = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=200_000 #(THE NUMBER OF TIMES THE STRING AND SALT BYTES, ARE HASHED)
    )
    HASH = HASH_BYTES.derive(STRING_BYTES)
    STRING_TEST = str(SALT)
    print(f'Salt before (str): {STRING_TEST}')
    print(f'Type: {type(STRING_TEST)}')
    print(f'Salt after (bytes): {ast.literal_eval(fr"{STRING_TEST}")}')
    print(f'Type: {type(ast.literal_eval(fr"{STRING_TEST}"))}')
    HASH_AND_SALT_TUPLE = (HASH, SALT)
    return HASH_AND_SALT_TUPLE

#THIS FUNCTION:
#1.) REQUIRES A PASSWORD STRING, DATABASE STORED PASSWORD HASH BYTES, AND DB STORED SALT HASH BYTES
#2.) CONVERTS THE PASSWORD STRING, TO HASH BYTES, USING THE DB STORED SALT BYTES,
#SO THE RESULTING PASSWORD HASH, MATCHES THE DB STORED HASH, IF THE SUPPLIED PASSWORD STRING, 
#IS THE SAME AS THE ORIGINAL PASSWORD STRING, USED TO CREATE THE DB STORED HASH BYTES.
#3.) COMPARES THE PASSWORD HASH BYTES, TO THE DATABASE STORED HASH BYTES
#4.) RETURNS "True" IF THE PASSWORD HASHES MATCH, OR "False", IF THEY DO NOT MATCH OR AN ERROR OCCURS
def is_password_valid(PASSWORD, DB_STORED_HASH_BYTES, DB_STORED_SALT_BYTES):
    try:
        NEW_HASH_BYTES, _ = get_hash_and_salt(PASSWORD.encode(), DB_STORED_SALT_BYTES)
        BOOLEAN = compare_digest(NEW_HASH_BYTES, DB_STORED_HASH_BYTES)
        return BOOLEAN
    except Exception as ERROR:
        return False

#THIS FUNCTION:
#1.) REQUIRES DATABASE FILE PATH AND DB TABLE NAME STRINGS
#2.) CHECKS IF A DB TABLE, ALREADY EXISTS
#3.) RETURNS "True" IF THE TABLE EXISTS, OR "False", IF IT DOES NOT EXIST OR AN ERROR OCCURS
def table_exists(DB_FILE_PATH, DB_TABLE_NAME):
        try:
            DB_CONNECTION = connect(DB_FILE_PATH)
            DB_CONNECTION_CURSOR = DB_CONNECTION.cursor()
            DB_CONNECTION_CURSOR.execute('SELECT name FROM sqlite_master WHERE type="table" AND name=?;', (DB_TABLE_NAME,))
            BOOLEAN = DB_CONNECTION_CURSOR.fetchone() is not None
            DB_CONNECTION.close()
            return BOOLEAN
        except:
            return False

#THIS FUNCTION:
#1.) REQUIRES DATABASE FILE PATH, DB TABLE NAME, AND COLUMN/S INFO STRINGS,
#WITH THE COLUMN/S INFO, CONTAINING THE COLUMN NAMES AND ATTRIBUTES, SEPARATED BY COMMAS,
#E.G.: 
#COLUMNS_INFO = '''
#id INTEGER PRIMARY KEY, 
#username TEXT NOT NULL UNIQUE, #(TYPE: TEXT, INSERTED ROW VALUES CANNOT BE EMPTY, ROW VALUES MUST BE UNIQUE, IN THE TABLE'S COLUMN)
#password_hash TEXT NOT NULL, 
#salt BLOB NOT NULL
#'''
#2.) CREATES A DATABASE TABLE, WITH THE SUPPLIED TABLE NAME AND COLUMN/S INFO
#3.) RAISES ANY ERRORS FOUND
def create_table(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS_INFO):
    try:
        if not all(isinstance(VALUE, str) for VALUE in (DB_FILE_PATH, DB_TABLE_NAME, COLUMNS_INFO)):
            raise TypeError('[TypeError]\nFunction: "create_table()"\nOne or more, supplied parameter/s, were not a string type.')
        if not all(VALUE.strip() for VALUE in (DB_FILE_PATH, DB_TABLE_NAME, COLUMNS_INFO)):
            raise ValueError('[ValueError]\nFunction: "create_table()"\nOne or more, supplied parameter/s, were empty.')
        db_file_path_error_check(DB_FILE_PATH)
        if is_quoted(DB_TABLE_NAME) or bool(fullmatch(r'[A-Za-z0-9_]+', DB_TABLE_NAME)):
            DB_TABLE_NAME = unquote(DB_TABLE_NAME) if is_quoted(DB_TABLE_NAME) else DB_TABLE_NAME
            if table_exists(DB_FILE_PATH, DB_TABLE_NAME):
                raise ValueError('[ValueError]\nFunction: "create_table()"\nThe supplied database table name, already exists.')
        else:
            raise ValueError('[ValueError]\nFunction: "create_table()"\nThe supplied database table name, was invalid.\nWhen creating a database table, the table name, must be surrounded with quotes,\nto include characters other than letters, numbers, and underscores.')
        DB_CONNECTION = connect(DB_FILE_PATH)
        DB_CONNECTION_CURSOR = DB_CONNECTION.cursor()
        DB_CONNECTION_CURSOR.execute(f'CREATE TABLE {DB_TABLE_NAME} ({COLUMNS_INFO});')
        DB_CONNECTION.commit()
        DB_CONNECTION.close()
    except Exception as ERROR:
        raise Exception(f'[Exception]\nFunction: "create_table()"\n{ERROR}')

#THIS FUNCTION:
#1.) REQUIRES DATABASE FILE PATH, DB TABLE NAME, COLUMN/S, AND ROW VALUE/S STRINGS
#2.) INSERTS 1 OR MORE ROW VALUE/S
#3.) RAISES ANY ERRORS FOUND
def insert_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_VALUES):
    try:
        if not all(isinstance(VALUE, str) for VALUE in [DB_FILE_PATH, DB_TABLE_NAME, COLUMNS]):
            raise TypeError('[TypeError]\nFunction: "insert_row_values()"\nOnly the row values parameter, can be a non-string type.')
        if not all([VALUE.strip() for VALUE in [DB_FILE_PATH, DB_TABLE_NAME, COLUMNS]]):
            raise ValueError('[ValueError]\nFunction: "insert_row_values()"\nOne or more, supplied parameter/s, were empty.')
        db_file_path_error_check(DB_FILE_PATH)
        if not is_quoted(DB_TABLE_NAME) and not bool(fullmatch(r'[A-Za-z0-9_]+', DB_TABLE_NAME)):
            raise ValueError('[ValueError]\nFunction: "insert_row_values()"\nThe supplied database table name, was invalid.\nWhen inserting row values into a database table, the table name, must be surrounded with quotes,\nto include characters other than letters, numbers, and underscores.')
        CONNECTION = connect(DB_FILE_PATH)
        CURSOR = CONNECTION.cursor()
        PLACEHOLDERS = ', '.join(['?' for COLUMN_NAME in COLUMNS.split(',')])

        #NOTE: THE ROW VALUE/S TO INSERT, INTO THE DATABASE TABLE, 
        #MUST BE CONVERTED TO A LIST, BEFORE, BEING PASSED TO THE 
        #"sqlite3.connect.cursor.execute()" FUNCTION, WHEN THE FUNCTION IS PARAMETERIZED.
        #TUPLES CAN BE ITERATED, LIKE A LIST, BUT THEY ARE SEEN AS A SINGLE VALUE,
        #BY THE "sqlite3" DB.
        #ROW_VALUES_LIST = [VALUE.strip() for VALUE in ROW_VALUES.split(',') if isinstance(VALUE, str)]

        CURSOR.execute(f'INSERT INTO {DB_TABLE_NAME} ({COLUMNS}) VALUES ({PLACEHOLDERS});', ROW_VALUES)
        CONNECTION.commit()
        CONNECTION.close()
        return True
    except Exception as ERROR:
        if 'UNIQUE constraint failed' in str(ERROR):
            return False
        raise Exception(f'[Exception]\nFunction: "insert_row_values()"\n{ERROR}')

#THIS FUNCTION:
#1.) REQUIRES DATABASE FILE PATH, DB TABLE NAME, COLUMN/S, ROW ID COLUMN, AND ROW ID VALUE STRINGS
#2.) SELECTS 1 OR MORE ROW VALUES AND ALLOWS SPECIFYING THE WILDCARD "*" VALUE,
#IN THE "COLUMNS" PARAMETER, TO SELECT ALL COLUMNS
#3.) RETURNS THE SELECTED ROW VALUES, AS A LIST, OR RAISES AN ERROR
def select_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_ID_COLUMN, ROW_ID_VALUE):
    try:
        if not all(isinstance(VALUE, str) for VALUE in [DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_ID_COLUMN]):
            raise TypeError('[TypeError]\nFunction: "select_row_values()"\nOnly the row values parameter, can be a non-string type.')
        if not all(VALUE.strip() for VALUE in [DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_ID_COLUMN]):
            raise ValueError('[ValueError]\nFunction: "select_row_values()"\nOne or more, supplied parameter/s, were empty.')
        db_file_path_error_check(DB_FILE_PATH)
        if not bool(fullmatch(r'[A-Za-z0-9_]+', DB_TABLE_NAME)) and not is_quoted(DB_TABLE_NAME):
            raise ValueError('[ValueError]\nFunction: "select_row_values()"\nThe supplied database table name, was invalid.\nWhen selecting row values from a database table, the table name, must be surrounded with quotes,\nto include characters other than letters, numbers, and underscores.')
        CONNECTION = connect(DB_FILE_PATH)
        CURSOR = CONNECTION.cursor()
        CURSOR = CONNECTION.cursor()
        ROW_ID_VALUE_TUPLE = (ROW_ID_VALUE,)
        CURSOR.execute(f'SELECT {COLUMNS} FROM {DB_TABLE_NAME} WHERE {ROW_ID_COLUMN} = ?;', ROW_ID_VALUE_TUPLE)
        SELECTED_ROW_VALUES = CURSOR.fetchone()
        CONNECTION.close()
        return list(SELECTED_ROW_VALUES)
    except Exception as ERROR:
        raise Exception(f'[Exception]\nFunction: "select_row_values()"\n{ERROR}')

#THIS FUNCTION:
#1.) REQUIRES DATABASE FILE PATH, DB TABLE NAME, COLUMN/S, ROW VALUE/S, ROW ID COLUMN, AND ROW ID VALUE STRINGS
#2.) UPDATES 1 OR MORE ROW VALUES, IN THE ROW IDENTIFIED, BY THE ROW ID COLUMN AND ROW ID VALUE
#3.) RAISES ANY ERRORS FOUND
def update_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_VALUES, ROW_ID_COLUMN, ROW_ID_VALUE):
    try:
        if not all(isinstance(VALUE, str) for VALUE in [DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_ID_COLUMN]):
            raise TypeError('[TypeError]\nFunction: "update_row_values()"\nOne or more, supplied parameter/s, were not a string type.')
        if not all(VALUE.strip() for VALUE in [DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_VALUES, ROW_ID_COLUMN, ROW_ID_VALUE] if isinstance(VALUE, str)):
            raise ValueError('[ValueError]\nFunction: "update_row_values()"\nOne or more, supplied parameter/s, were empty.')
        db_file_path_error_check(DB_FILE_PATH)
        if not bool(fullmatch(r'[A-Za-z0-9_]+', DB_TABLE_NAME)) and not is_quoted(DB_TABLE_NAME):
            raise ValueError('[ValueError]\nFunction: "update_row_values()"\nThe supplied database table name, was invalid.\nWhen updating row values in a database table, the table name, must be surrounded with quotes,\nto include characters other than letters, numbers, and underscores.')
        CONNECTION = connect(DB_FILE_PATH)
        CURSOR = CONNECTION.cursor()
        PLACEHOLDERS = ', '.join([f'{COLUMN_NAME} = ?' for COLUMN_NAME in COLUMNS.split(',')])
        ROW_VALUES_LIST = [VALUE.strip() for VALUE in ROW_VALUES.split(',') if isinstance(VALUE, str)]
        ROW_VALUES_LIST += [ROW_ID_VALUE]
        CURSOR.execute(f'UPDATE {DB_TABLE_NAME} SET {PLACEHOLDERS} WHERE {ROW_ID_COLUMN} = ?;', ROW_VALUES_LIST)
        CONNECTION.commit()
        CONNECTION.close()
    except Exception as ERROR:
        raise Exception(f'[Exception]\nFunction: "update_row_values()"\n{ERROR}')

#THIS FUNCTION:
#1.) REQUIRES DATABASE FILE PATH, DB TABLE NAME, ROW ID COLUMN, AND ROW ID VALUE STRINGS
#2.) DELETES THE ROW IDENTIFIED BY THE ROW ID COLUMN AND ROW ID VALUE
#3.) RAISES ANY ERRORS FOUND
def delete_row(DB_FILE_PATH, DB_TABLE_NAME, ROW_ID_COLUMN, ROW_ID_VALUE):
    try:
        if not all((isinstance(VALUE, str) for VALUE in [DB_FILE_PATH, DB_TABLE_NAME, ROW_ID_COLUMN, ROW_ID_VALUE])):
            raise TypeError('[TypeError]\nFunction: "delete_row()"\nOne or more, supplied parameter/s, were not a string type.')
        if not all((VALUE.strip() for VALUE in [DB_FILE_PATH, DB_TABLE_NAME, ROW_ID_COLUMN, ROW_ID_VALUE] if isinstance(VALUE, str))):
            raise ValueError('[ValueError]\nFunction: "delete_row()"\nOne or more, supplied parameter/s, were empty.')
        db_file_path_error_check(DB_FILE_PATH)
        if not bool(fullmatch(r'[A-Za-z0-9_]+', DB_TABLE_NAME)) and not is_quoted(DB_TABLE_NAME):
            raise ValueError('[ValueError]\nFunction: "delete_row()"\nThe supplied database table name, was invalid.\nWhen deleting a row from a database table, the table name, must be surrounded with quotes,\nto include characters other than letters, numbers, and underscores.')
        CONNECTION = connect(DB_FILE_PATH)
        CURSOR = CONNECTION.cursor()
        ROW_ID_VALUE_TUPLE = (ROW_ID_VALUE,)
        CURSOR.execute(f'DELETE FROM {DB_TABLE_NAME} WHERE {ROW_ID_COLUMN} = ?;', ROW_ID_VALUE_TUPLE)
        CONNECTION.commit()
        CONNECTION.close()
    except Exception as ERROR:
        raise Exception(f'[Exception]\nFunction: "delete_row()"\n{ERROR}')