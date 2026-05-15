from os.path import isabs, exists, isfile
from inspect import currentframe
from re import fullmatch
from sqlite3 import connect
from base64 import urlsafe_b64encode
from secrets import token_bytes, compare_digest
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken

#THIS FUNCTION:
#1.) REQUIRES A LIST
#2.) CHECKS IF ANY ITEM, IN THE LIST, IS EMPTY, CONTINUES TO THE NEXT ITEM, 
#IF A NONE-UTF-8 BYTES ITEM, IS DETECTED, BY A DECODE FAILURE (MEANING, IT'S NOT EMPTY)
#3.) RETURNS "True", IF ANY ITEM, IN THE LIST, IS EMPTY, "False", IF NO LIST ITEMS, ARE EMPTY, OR RAISES A "TypeError"
def any_empty(LIST):
    if not isinstance(LIST, list):
        raise TypeError('[TypeError]\nFunction: "any_empty()"\nThe supplied list parameter, was not a list type.')
    for ITEM in LIST:
        if isinstance(ITEM, str):
            if not ITEM.strip():
                return True
        elif isinstance(ITEM, bytes):
            try:
                if not ITEM.decode(errors='ignore').strip():
                    return True
            except Exception:
                continue
        elif hasattr(ITEM, '__len__'):
            if len(ITEM) == 0:
                return True
        else:
            if not ITEM:
                return True
    return False

#THIS FUNCTION:
#1.) REQUIRES A LIST
#2.) CHECKS EVERY ITEM, IN THE LIST, AND STRIPS ANY STRING TYPE ITEM/S
#3.) RETURNS THE LIST, WITH ANY STRING TYPE ITEM/S, STRIPPED OR RAISES A "TypeError"
def strip_all(LIST):
    if not isinstance(LIST, list):
        raise TypeError('[TypeError]\nFunction: "strip_all()"\nThe supplied list parameter, was not a list type.')
    else:
        LIST = [VALUE.strip() if isinstance(VALUE, str) else VALUE for VALUE in LIST]
        return LIST

#THIS FUNCTION:
#1.) REQUIRES A DATABASE FILE PATH STRING
#2.) CHECKS FOR DATABASE FILE PATH ERRORS
#3.) RAISES ANY ERRORS FOUND
def db_file_path_error_check(DB_FILE_PATH):
    if any_empty([DB_FILE_PATH]):
        raise ValueError(f'[ValueError]\nFunction: "{currentframe().f_back.f_code.co_name}()"\nThe supplied database file path parameter, was empty.')
    elif not isinstance(DB_FILE_PATH, str):
        raise TypeError(f'[TypeError]\nFunction: "{currentframe().f_back.f_code.co_name}()"\nThe supplied database file path parameter, was not a string type.')
    elif not isabs(DB_FILE_PATH):
        raise ValueError(f'[ValueError]\nFunction: "{currentframe().f_back.f_code.co_name}()"\nThe supplied database file path parameter, was not an absolute path.')
    elif not exists(DB_FILE_PATH):
        raise FileNotFoundError(f'[FileNotFoundError]\nFunction: "{currentframe().f_back.f_code.co_name}()"\nThe supplied database file path parameter, does not exist.')
    elif not isfile(DB_FILE_PATH):
        raise FileNotFoundError(f'[FileNotFoundError]\nFunction: "{currentframe().f_back.f_code.co_name}()"\nThe supplied database file path parameter, was not a path to a file.')

#THIS FUNCTION:
#1.) REQUIRES A STRING
#2.) CHECKS IF THE STRING, IS QUOTED
#3.) RETURNS "True", IF THE STRING, IS QUOTED, OR "False", IF THE STRING, IS NOT QUOTED
def is_quoted(STRING):
    if STRING[0] == STRING[-1] and STRING[0] in ("'", '"') and STRING.count(STRING[0]) == 2:
        return True
    else:
        return False

#NOTE: WHEN CREATING AN "sqlite3" DATABASE TABLE WITH SPECIAL CHARACTERS
#(CHARACTERS OTHER THAN aA-zZ, 0-9, and "_"),
#YOU MUST USE A TABLE NAME, WITH QUOTES SURROUNDING THE NAME. 
#THIS MAY GET CONFUSING, WHEN QUERYING THE DB FOR THAT TABLE NAME,
#BECAUSE THE DB STORES IT WITHOUT THE SURROUNDING QUOTES.
#WHEN QUERYING THE DB FOR A TABLE NAME, THAT INCLUDES SPECIAL CHARACTERS,
#DO NOT INCLUDE THE SURROUNDING QUOTES, USED TO CREATE THE TABLE, IN THE QUERY.
#THE SURROUNDING QUOTES, ARE ONLY USED TO CREATE A TABLE WITH SPECIAL CHARACTERS,
#NOT TO QUERY A TABLE, WITH SPECIAL CHARACTERS.
#THE "unquote()" FUNCTION, CAN BE USED TO UNQUOTE A DATABASE TABLE NAME.

#THIS FUNCTION:
#1.) REQUIRES A STRING
#2.) UNQUOTES THE STRING, IF THE STRING, IS QUOTED
#3.) RETURNS THE STRING, UNQUOTED, OR RAISES AN ERROR
def unquote(STRING):
    if not any_empty([STRING]):
        raise ValueError('[ValueError]\nFunction: "unquote()"\nThe supplied string parameter, was empty.')
    if not isinstance(STRING, str):
        raise TypeError('[TypeError]\nFunction: "unquote()"\nThe supplied string parameter, was not a string type.')
    if STRING[0] == STRING[-1] and STRING[0] in ("'", '"') and STRING.count(STRING[0]) == 2:
        STRING = STRING.replace(STRING[0], '')
        return STRING
    else:
        return STRING

#THIS FUNCTION:
#1.) REQUIRES A STRING OR BYTES AND 32 BIT PASSWORD HASH BYTES
#2.) ENCRYPTS THE STRING TO AES-128 ENCRYPTED BYTES, USING THE SUPPLIED PASSWORD HASH BYTES,
#AS A KEY, FOR THE ENCRYPTION/DECRYPTION, OF THE STRING
#3.) RETURNS THE STRING, AES-128 BIT ENCRYPTED, OR RAISES AN ERROR
def aes_128_encrypt(STRING, PASSWORD_HASH_BYTES):
    if any_empty([STRING, PASSWORD_HASH_BYTES]):
        raise ValueError('[ValueError]\nFunction: "aes_128_encrypt()"\nOne or more, supplied parameter/s, were empty.')
    elif not isinstance(PASSWORD_HASH_BYTES, bytes):
        raise TypeError('[TypeError]\nFunction: "aes_128_encrypt()"\nThe supplied password hash bytes parameter, was not a bytes type.')
    
    #NOTE: THE CRYPTOGRAPHY LIBRARY'S "Fernet()" FUNCTION,
    #REQUIRES A 32 BYTE KEY, THAT IS URL SAFE BASE64 ENCODED.
    CIPHER = Fernet(urlsafe_b64encode(PASSWORD_HASH_BYTES))

    if not isinstance(STRING, bytes):
        STRING = str(STRING).encode()
    ENCRYPTED_STRING_BYTES = CIPHER.encrypt(STRING)
    return ENCRYPTED_STRING_BYTES

#THIS FUNCTION:
#1.) REQUIRES AES-128 BIT ENCRYPTED BYTES AND PASSWORD HASH BYTES
#2.) DECRYPTS THE AES-128 BIT ENCRYPTED BYTES, USING THE PASSWORD HASH BYTES VALUE,
#THAT WAS USED TO ENCRYPT THE ORIGINAL STRING
#3.) RETURNS THE DECRYPTED PLAINTEXT STRING OR RAISES AN ERROR
def aes_128_decrypt(ENCRYPTED_STRING_BYTES, PASSWORD_HASH_BYTES):
    if any_empty([ENCRYPTED_STRING_BYTES, PASSWORD_HASH_BYTES]):
        raise ValueError('[ValueError]\nFunction: "aes_128_decrypt()"\nOne or more, supplied parameter/s, were empty.')
    elif not all([isinstance(ITEM, bytes) for ITEM in [ENCRYPTED_STRING_BYTES, PASSWORD_HASH_BYTES]]):
        raise TypeError('[TypeError]\nFunction: "aes_128_decrypt()"\nOne or more, supplied parameter/s, were not a bytes type.')
    CIPHER = Fernet(urlsafe_b64encode(PASSWORD_HASH_BYTES))
    try:
        PLAINTEXT_STRING = CIPHER.decrypt(ENCRYPTED_STRING_BYTES)
    except InvalidToken:
        return 0
    return PLAINTEXT_STRING

#THIS FUNCTION:
#1.) REQUIRES A STRING AND ACCEPTS AN OPTIONAL SALT BYTES PARAMETER
#2.) CREATES RANDOM SALT BYTES (IF NOT SUPPLIED, WITH THE OPTIONAL SALT BYTES PARAMETER)
#3.) ENCODES THE STRING, TO BYTES (IF NOT ALREADY A BYTES TYPE)
#4.) HASHES THE STRING BYTES, WITH THE PBKDF2 HMAC HASHING ALGORITHM, 
#USING THE "SHA256" HASH FUNCTION, WITH A SALT, AND 200,000 ITERATIONS
#5.) RETURNS THE STRING HASH BYTES AND SALT BYTES, AS A LIST, OR RAISES AN ERROR
#NOTE: THIS FUNCTION, MEETS THE CRITERIA FOR "RFC 8018" AND "NIST SP 800‑63B",
#MEANING IT MEETS THE SECURITY STANDARDS FOR HASHING PASSWORDS AND GENERATING SALTS, 
#TO BE STORED IN A DATABASE, FOR LATER PASSWORD VERIFICATION.
def get_hash_and_salt(STRING, SALT_BYTES=None):
    if any_empty([STRING]):
        raise ValueError('[ValueError]\nFunction: "get_hash_and_salt()"\nThe supplied string parameter, was empty.')
    elif SALT_BYTES is not None and not isinstance(SALT_BYTES, bytes):
        raise TypeError('[TypeError]\nFunction: "get_hash_and_salt()"\nThe supplied salt bytes parameter, was not a bytes type.')
    
    #NOTE: A 16 BYTE SALT, IS REQUIRED, FOR THE HASH TO BE GENERATED.
    SALT_BYTES = token_bytes(16) if SALT_BYTES is None else SALT_BYTES
    HASH_BYTES = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32, #(THE NUMBER OF BYTES, IN LENGTH, THE HASH SHOULD BE)
        salt=SALT_BYTES,
        iterations=200_000 #(THE NUMBER OF TIMES THE STRING BYTES PARAMETER, IS HASHED)
    )
    STRING_BYTES = str(STRING).encode() if not isinstance(STRING, bytes) else STRING
    
    #NOTE: THE STRING, MUST BE ENCODED TO A BYTES TYPE, BEFORE DERIVING A HASH FOR IT.
    HASH_BYTES = HASH_BYTES.derive(STRING_BYTES)

    HASH_AND_SALT_BYTES = [HASH_BYTES, SALT_BYTES]
    return HASH_AND_SALT_BYTES

#THIS FUNCTION:
#1.) REQUIRES A PASSWORD STRING, DATABASE STORED HASH BYTES, AND DB STORED SALT BYTES
#2.) CONVERTS THE PASSWORD STRING, TO HASH BYTES, USING THE DB STORED SALT BYTES,
#SO THE RESULTING PASSWORD HASH, MATCHES THE DB STORED HASH, IF THE SUPPLIED PASSWORD STRING, 
#IS THE SAME AS THE ORIGINAL PASSWORD STRING, USED TO CREATE THE DB STORED HASH BYTES
#3.) COMPARES THE PASSWORD HASH BYTES, TO THE DATABASE STORED HASH BYTES
#4.) RETURNS "True", IF THE PASSWORD HASHES MATCH, OR "False", IF THEY DO NOT MATCH OR AN ERROR OCCURS
def is_password_valid(PASSWORD_STRING, DB_STORED_HASH_BYTES, DB_STORED_SALT_BYTES):
    try:
        NEW_HASH_BYTES, _ = get_hash_and_salt(PASSWORD_STRING, DB_STORED_SALT_BYTES)
        BOOLEAN = bool(compare_digest(NEW_HASH_BYTES, DB_STORED_HASH_BYTES))
        return BOOLEAN
    except:
        return False

#THIS FUNCTION:
#1.) REQUIRES DATABASE FILE PATH AND DB TABLE NAME STRINGS
#2.) CHECKS IF A DB TABLE, ALREADY EXISTS
#3.) RETURNS "True", IF THE TABLE EXISTS, OR "False", IF IT DOES NOT EXIST OR AN ERROR OCCURS
def table_exists(DB_FILE_PATH, DB_TABLE_NAME):
        try:
            DB_CONNECTION = connect(DB_FILE_PATH)
            DB_CONNECTION_CURSOR = DB_CONNECTION.cursor()

            #NOTE: "sqlite3", REQUIRES A SEQUENCE (TUPLE OR LIST), FOR PARAMETERS, IN A PARAMETERIZED QUERY.
            #WHEN "VARIABLE = 'test'; tuple(VARIABLE)", IS USED, THE RESULT IS "('t', 'e', 's', 't')", THEREFOR,
            #DIRECTLY SETTING A TUPLE WITH "(VARIABLE,)", IS NECCESSARY, WHEN USING A TUPLE (MUST INCLUDE THE COMMA, FOR SINGLE ITEM TUPLES).
            #TUPLES, ARE RECOMMENDED FOR USE WITH LISTS, CONSISTING OF 1-3 ITEMS.
            DB_CONNECTION_CURSOR.execute('SELECT name FROM sqlite_master WHERE type="table" AND name=?;', (DB_TABLE_NAME,))

            BOOLEAN = DB_CONNECTION_CURSOR.fetchone() is not None
            DB_CONNECTION.close()
            return BOOLEAN
        except:
            return False

#THIS FUNCTION:
#1.) REQUIRES DATABASE FILE PATH, DB TABLE NAME, AND COLUMN/S INFO STRINGS,
#WITH THE COLUMN/S INFO PARAMETER, CONTAINING THE COLUMN NAMES AND ATTRIBUTES, SEPARATED BY COMMAS,
#E.G.: 
#COLUMNS_INFO = '''
#id INTEGER PRIMARY KEY, 
#username TEXT NOT NULL UNIQUE, #(TYPE IS TEXT, INSERTED ROW VALUES CANNOT BE EMPTY, ROW VALUES MUST BE UNIQUE, IN THE TABLE'S COLUMN)
#password_hash BLOB NOT NULL, 
#salt BLOB NOT NULL
#'''
#2.) CREATES A DATABASE TABLE, WITH THE SUPPLIED TABLE NAME AND COLUMN/S INFO
#3.) RAISES ANY ERRORS FOUND
def create_table(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS_INFO):
    try:
        if any_empty([DB_FILE_PATH, DB_TABLE_NAME, COLUMNS_INFO]):
            raise ValueError('[ValueError]\nFunction: "create_table()"\nOne or more, supplied parameter/s, were empty.')
        elif not all([isinstance(ITEM, str) for ITEM in [DB_FILE_PATH, DB_TABLE_NAME, COLUMNS_INFO]]):
            raise TypeError('[TypeError]\nFunction: "create_table()"\nOne or more, supplied parameter/s, were not a string type.')
        db_file_path_error_check(DB_FILE_PATH)
        if is_quoted(DB_TABLE_NAME) or bool(fullmatch(r'[A-Za-z0-9_]+', DB_TABLE_NAME)):
            DB_TABLE_NAME = unquote(DB_TABLE_NAME) if is_quoted(DB_TABLE_NAME) else DB_TABLE_NAME
            if table_exists(DB_FILE_PATH, DB_TABLE_NAME):
                raise ValueError('[ValueError]\nFunction: "create_table()"\nThe supplied database table name, already exists.')
        else:
            raise ValueError('[ValueError]\nFunction: "create_table()"\nThe supplied database table name parameter, was invalid.\nWhen creating a database table, the table name, must be surrounded with quotes,\nto include characters other than letters, numbers, and underscores.')
        DB_CONNECTION = connect(DB_FILE_PATH)
        DB_CONNECTION_CURSOR = DB_CONNECTION.cursor()
        DB_CONNECTION_CURSOR.execute(f'CREATE TABLE {DB_TABLE_NAME} ({COLUMNS_INFO});')
        DB_CONNECTION.commit()
        DB_CONNECTION.close()
    except Exception as ERROR:
        raise Exception(f'[Exception]\nFunction: "create_table()"\n{ERROR}')

#THIS FUNCTION:
#1.) REQUIRES A DATABASE FILE PATH STRING, DB TABLE NAME STRING, COLUMN/S STRING, AND ROW VALUE/S TUPLE/LIST
#2.) INSERTS 1 OR MORE ROW VALUE/S, INTO THE DB TABLE
#3.) RAISES ANY ERRORS FOUND
def insert_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_VALUES):
    try:
        if any_empty([DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_VALUES]):
            raise ValueError('[ValueError]\nFunction: "insert_row_values()"\nOne or more, supplied parameter/s, were empty.')
        elif not all([isinstance(VALUE, str) for VALUE in [DB_FILE_PATH, DB_TABLE_NAME, COLUMNS]]):
            raise TypeError('[TypeError]\nFunction: "insert_row_values()"\nOnly the row values parameter, should be a non-string type.')
        elif not isinstance(ROW_VALUES, tuple) and not isinstance(ROW_VALUES, list):
            raise TypeError('[TypeError]\nFunction: "insert_row_values()"\nThe supplied row values parameter, was not a tuple or list type.')
        db_file_path_error_check(DB_FILE_PATH)
        if not is_quoted(DB_TABLE_NAME) and not bool(fullmatch(r'[A-Za-z0-9_]+', DB_TABLE_NAME)):
            raise ValueError('[ValueError]\nFunction: "insert_row_values()"\nThe supplied database table name parameter, was invalid.\nWhen inserting row values into a database table, the table name, must be surrounded with quotes,\nto include characters other than letters, numbers, and underscores.')
        CONNECTION = connect(DB_FILE_PATH)
        CURSOR = CONNECTION.cursor()
        PLACEHOLDERS = ', '.join(['?' for COLUMN_NAME in COLUMNS.split(',')])
        CURSOR.execute(f'INSERT INTO {DB_TABLE_NAME} ({COLUMNS}) VALUES ({PLACEHOLDERS});', ROW_VALUES)
        CONNECTION.commit()
        CONNECTION.close()
    except Exception as ERROR:
        raise Exception(f'[Exception]\nFunction: "insert_row_values()"\n{ERROR}')

#THIS FUNCTION:
#1.) REQUIRES DATABASE FILE PATH, DB TABLE NAME, COLUMN/S, ROW ID COLUMN, AND ROW ID VALUE STRINGS
#2.) SELECTS 1 OR MORE ROW VALUE/S AND ALLOWS SPECIFYING THE WILDCARD VALUE ("*"),
#IN THE COLUMN/S PARAMETER, TO SELECT ALL COLUMNS OF THE IDENTIFIED ROW
#3.) RETURNS THE SELECTED ROW VALUE/S, AS A LIST, OR RAISES AN ERROR
def select_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_ID_COLUMN, ROW_ID_VALUE):
    try:
        if any_empty([DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_ID_COLUMN, ROW_ID_VALUE]):
            raise ValueError('[ValueError]\nFunction: "select_row_values()"\nOne or more, supplied parameter/s, were empty.')
        elif not all([isinstance(VALUE, str) for VALUE in [DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_ID_COLUMN, ROW_ID_VALUE]]):
            raise TypeError('[TypeError]\nFunction: "select_row_values()"\nOne or more, parameter/s, were a non-string type.')
        db_file_path_error_check(DB_FILE_PATH)
        if not bool(fullmatch(r'[A-Za-z0-9_]+', DB_TABLE_NAME)) and not is_quoted(DB_TABLE_NAME):
            raise ValueError('[ValueError]\nFunction: "select_row_values()"\nThe supplied database table name parameter, was invalid.\nWhen selecting row values from a database table, the table name, must be surrounded with quotes,\nto include characters other than letters, numbers, and underscores.')
        CONNECTION = connect(DB_FILE_PATH)
        CURSOR = CONNECTION.cursor()
        CURSOR = CONNECTION.cursor()
        ROW_ID_VALUE = (ROW_ID_VALUE,)
        CURSOR.execute(f'SELECT {COLUMNS} FROM {DB_TABLE_NAME} WHERE {ROW_ID_COLUMN} = ?;', ROW_ID_VALUE)
        SELECTED_ROW_VALUES = list(CURSOR.fetchone())
        CONNECTION.close()
        return SELECTED_ROW_VALUES
    except Exception as ERROR:
        raise Exception(f'[Exception]\nFunction: "select_row_values()"\n{ERROR}')

#THIS FUNCTION:
#1.) REQUIRES DATABASE FILE PATH, DB TABLE NAME, COLUMN/S, ROW VALUE/S, ROW ID COLUMN, AND ROW ID VALUE STRINGS
#2.) UPDATES 1 OR MORE ROW VALUES, IN THE ROW IDENTIFIED, BY THE ROW ID COLUMN AND ROW ID VALUE STRINGS
#3.) RAISES ANY ERRORS FOUND
def update_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_VALUES, ROW_ID_COLUMN, ROW_ID_VALUE):
    try:
        if any_empty([DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_VALUES, ROW_ID_COLUMN, ROW_ID_VALUE]):
            raise ValueError('[ValueError]\nFunction: "update_row_values()"\nOne or more, supplied parameter/s, were empty.')
        if not all([isinstance(VALUE, str) for VALUE in [DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_ID_COLUMN]]):
            raise TypeError('[TypeError]\nFunction: "update_row_values()"\nOnly the row values parameter, should be a non-string type.')
        if not isinstance(ROW_VALUES, tuple) and not isinstance(ROW_VALUES, list):
            raise TypeError('[TypeError]\nFunction: "update_row_values()"\nThe supplied row values parameter, was not a tuple or list type.')
        db_file_path_error_check(DB_FILE_PATH)
        if not bool(fullmatch(r'[A-Za-z0-9_]+', DB_TABLE_NAME)) and not is_quoted(DB_TABLE_NAME):
            raise ValueError('[ValueError]\nFunction: "update_row_values()"\nThe supplied database table name, was invalid.\nWhen updating row values in a database table, the table name, must be surrounded with quotes,\nto include characters other than letters, numbers, and underscores.')
        CONNECTION = connect(DB_FILE_PATH)
        CURSOR = CONNECTION.cursor()
        PLACEHOLDERS = ', '.join([f'{COLUMN_NAME} = ?' for COLUMN_NAME in COLUMNS.split(',')])
        ROW_VALUES += (ROW_ID_VALUE,)
        CURSOR.execute(f'UPDATE {DB_TABLE_NAME} SET {PLACEHOLDERS} WHERE {ROW_ID_COLUMN} = ?;', ROW_VALUES)
        CONNECTION.commit()
        CONNECTION.close()
    except Exception as ERROR:
        raise Exception(f'[Exception]\nFunction: "update_row_values()"\n{ERROR}')

#THIS FUNCTION:
#1.) REQUIRES DATABASE FILE PATH, DB TABLE NAME, ROW ID COLUMN, AND ROW ID VALUE STRINGS
#2.) DELETES THE ROW IDENTIFIED, BY THE ROW ID COLUMN AND ROW ID VALUE STRINGS
#3.) RAISES ANY ERRORS FOUND
def delete_row(DB_FILE_PATH, DB_TABLE_NAME, ROW_ID_COLUMN, ROW_ID_VALUE):
    try:
        if any_empty([DB_FILE_PATH, DB_TABLE_NAME, ROW_ID_COLUMN, ROW_ID_VALUE]):
            raise ValueError('[ValueError]\nFunction: "delete_row()"\nOne or more, supplied parameter/s, were empty.')
        if not all([isinstance(VALUE, str) for VALUE in [DB_FILE_PATH, DB_TABLE_NAME, ROW_ID_COLUMN, ROW_ID_VALUE]]):
            raise TypeError('[TypeError]\nFunction: "delete_row()"\nOne or more, supplied parameter/s, were not a string type.')
        db_file_path_error_check(DB_FILE_PATH)
        if not bool(fullmatch(r'[A-Za-z0-9_]+', DB_TABLE_NAME)) and not is_quoted(DB_TABLE_NAME):
            raise ValueError('[ValueError]\nFunction: "delete_row()"\nThe supplied database table name, was invalid.\nWhen deleting a row from a database table, the table name, must be surrounded with quotes,\nto include characters other than letters, numbers, and underscores.')
        CONNECTION = connect(DB_FILE_PATH)
        CURSOR = CONNECTION.cursor()
        ROW_ID_VALUE = (ROW_ID_VALUE,)
        CURSOR.execute(f'DELETE FROM {DB_TABLE_NAME} WHERE {ROW_ID_COLUMN} = ?;', ROW_ID_VALUE)
        CONNECTION.commit()
        CONNECTION.close()
    except Exception as ERROR:
        raise Exception(f'[Exception]\nFunction: "delete_row()"\n{ERROR}')