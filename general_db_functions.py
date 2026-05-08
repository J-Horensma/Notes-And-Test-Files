from os.path import exists, isabs, isfile
from re import fullmatch
from binascii import hexlify, unhexlify
from secrets import token_bytes
from hmac import compare_digest
from sqlite3 import connect, Error, OperationalError
from hashlib import pbkdf2_hmac

#NOTE: WHEN CREATING AN "sqlite3" DATABASE TABLE WITH SPECIAL CHARACTERS
#(CHARACTERS OTHER THAN aA-zZ, 0-9, and "_"),
#YOU MUST USE A TABLE NAME, WITH QUOTES SURROUNDING THE NAME. 
#THIS MAY GET CONFUSING, WHEN QUERYING THE DB FOR THAT TABLE NAME,
#AS THE DB STORES IT WITHOUT THE SURROUNDING QUOTES.
#WHEN QUERYING THE DB FOR A TABLE NAME, THAT INCLUDES SPECIAL CHARACTERS,
#DO NOT INCLUDE THE SURROUNDING QUOTES, USED TO CREATE THE TABLE, IN THE QUERY.

#NOTE: THE "unquote()" FUNCTION, CAN BE USED TO UNQUOTE A DB TABLE NAME.

#THIS FUNCTION:
#1.) REQUIRES A DATABASE FILE PATH AND THE NAME OF THE FUNCTION CALLING THIS FUNCTION
#2.) CHECKS FOR DATABASE FILE PATH ERRORS
#2.) RAISES ANY ERRORS FOUND
def db_file_path_error_check(DB_FILE_PATH, FUNCTION_NAME):
    if not all([DB_FILE_PATH.strip(), FUNCTION_NAME.strip()]):
        raise ValueError(f'[ValueError]\nFunction: {FUNCTION_NAME}\nOne or more, supplied values, were empty.')
    elif not isabs(DB_FILE_PATH):
        raise ValueError(f'[ValueError]\nFunction: {FUNCTION_NAME}\nThe supplied database file path, was not an absolute path.')
    elif not exists(DB_FILE_PATH):
        raise FileNotFoundError(f'[FileNotFoundError]\nFunction: {FUNCTION_NAME}\nThe supplied database file path, does not exist.')
    elif not isfile(DB_FILE_PATH):
        raise FileNotFoundError(f'[ValueError]\nFunction: {FUNCTION_NAME}\nThe supplied database file path, was not a path to a file.')

#THIS FUNCTION:
#1.) REQUIRES A STRING
#2.) CHECKS IF A STRING IS QUOTED
#3.) RETURNS "True", IF THE STRING IS QUOTED OR "False", IF IT IS NOT QUOTED
def is_quoted(STRING):
    if STRING[0] == STRING[-1] and STRING[0] in ("'", '"') and STRING.count(STRING[0]) == 2:
        return True
    else:
        return False
    
#THIS FUNCTION:
#1.) REQUIRES A STRING
#2.) CHECKS IF A STRING IS QUOTED
#3.) RETURNS THE STRING, UNQUOTED
def unquote(STRING):
    if not STRING.strip():
        raise ValueError('[ValueError]\nFunction: unquote()\nThe supplied string, was empty.')
    if STRING[0] == STRING[-1] and STRING[0] in ("'", '"') and STRING.count(STRING[0]) == 2:
        return STRING.replace(STRING[0], '')
    else:
        return STRING

#THIS FUNCTION:
#1.) REQUIRES A PASSWORD STRING, TO BE HASHED, AND ACCEPTS AN OPTIONAL SALT BYTES PARAMETER
#2.) CONVERTS THE PASSWORD STRING TO SHA256 HASH BYTES
#3.) CREATES RANDOM SALT BYTES (IF NOT SUPPLIED, WITH THE OPTIONAL "SALT" PARAMETER)
#4.) CONVERTS THE HASH BYTES AND SALT BYTES, TO HEX STRINGS
#5.) RETURNS A HEX FORMATTED PASSWORD HASH AND A SALT, AS A LIST
#NOTE: THIS FUNCTION MEETS THE CRITERIA FOR "RFC 8018" AND "NIST SP 800‑63B",
#MEANING IT MEETS THE SECURITY STANDARDS, FOR HASHING PASSWORDS AND GENERATING SALTS, 
#TO BE STORED IN A DATABASE, FOR LATER PASSWORD VERIFICATION.
def get_hash_and_salt_hex(PASSWORD, SALT_BYTES=None):
    SALT_BYTES = token_bytes(16) if SALT_BYTES is None else SALT_BYTES
    if not PASSWORD:
        raise ValueError('[ValueError]\nFunction: get_hash_and_salt_hex()\nThe supplied password value, was empty.')
    HASH = pbkdf2_hmac(
        'sha256',
        PASSWORD.encode('utf-8'), #NOTE: THE SUPPLIED PASSWORD, MUST BE ENCODED TO BYTES, BEFORE HASHING.
        SALT_BYTES,
        100_000 #(THE NUMBER OF TIMES THE PASSWORD AND SALT BYTES, ARE HASHED)
    )

    #SOMETIMES, A DATABASE WILL NOT ALLOW STORING RAW BYTES, WITHOUT PRE-CONFIGURATION,
    #TO AVOID THIS, CONVERT THE HASH AND SALT BYTES TO HEX STRINGS.
    HASH_HEX = HASH.hex()
    SALT_HEX = SALT_BYTES.hex()
    
    return [HASH_HEX, SALT_HEX]

#THIS FUNCTION:
#1.) REQUIRES A PASSWORD STRING, DATABASE STORED HASH HEX STRING, AND DB STORED SALT HEX STRING
#2.) CONVERTS THE DATABASE STORED SALT HEX STRING, TO BYTES
#3.) CONVERTS THE PASSWORD TO A HASH HEX STRING, USING THE DATABASE STORED SALT
#4.) COMPARES THE PASSWORD HASH HEX STRING, TO THE DATABASE STORED HASH HEX STRING
#5.) RETURNS "True" IF THE HASHES MATCH, OR "False" IF THEY DO NOT MATCH
def verify_password(PASSWORD, DB_STORED_HASH_HEX, DB_STORED_SALT_HEX):
    DB_STORED_SALT_BYTES = bytes.fromhex(DB_STORED_SALT_HEX)
    HASH_HEX, _ = get_password_hash_and_salt(PASSWORD, DB_STORED_SALT_BYTES)
    return compare_digest(HASH_HEX, DB_STORED_HASH_HEX)

#THIS FUNCTION:
#1.) REQUIRES A DATABASE FILE PATH AND A DB TABLE NAME
#2.) CHECKS IF A DB TABLE, ALREADY EXISTS
#3.) RETURNS "True" IF THE TABLE EXISTS, OR "False" IF IT DOES NOT EXIST
def table_exists(DB_FILE_PATH, DB_TABLE_NAME):
        try:
            DB_CONNECTION = connect(DB_FILE_PATH)
            DB_CONNECTION_CURSOR = DB_CONNECTION.cursor()
            DB_CONNECTION_CURSOR.execute('SELECT name FROM sqlite_master WHERE type="table" AND name=?;', (DB_TABLE_NAME,))
            RESULT = DB_CONNECTION_CURSOR.fetchone() is not None
            DB_CONNECTION.close()
            return RESULT
        except:
            return False

#THIS FUNCTION:
#1.) REQUIRES A DATABASE FILE PATH, DB TABLE NAME, AND THE COLUMN INFO, FOR THE TABLE
#2.) CREATES A DATABASE TABLE, WITH THE SUPPLIED TABLE NAME AND COLUMNS INFO
#3.) RAISES ANY ERRORS
def create_table(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS_INFO):
    try:
        if not all([DB_FILE_PATH.strip(), DB_TABLE_NAME.strip(), COLUMNS_INFO.strip()]):
            raise ValueError('[ValueError]\nFunction: create_table()\nOne or more supplied values, were empty.')
        db_file_path_error_check(DB_FILE_PATH, 'create_table()')
        if is_quoted(DB_TABLE_NAME) or bool(fullmatch(r'[A-Za-z0-9_]+', DB_TABLE_NAME)):
            TEMP_DB_TABLE_NAME = unquote(DB_TABLE_NAME) if is_quoted(DB_TABLE_NAME) else DB_TABLE_NAME
            if table_exists(DB_FILE_PATH, TEMP_DB_TABLE_NAME):
                raise ValueError('[ValueError]\nFunction: create_table()\nThe supplied database table name, already exists.')
        else:
            raise ValueError('[ValueError]\nFunction: create_table()\nThe supplied database table name, was invalid.\nWhen creating a database table, the table name, must be surrounded with quotes,\nto include characters other than letters, numbers, and underscores.')
        DB_CONNECTION = connect(DB_FILE_PATH)
        DB_CONNECTION_CURSOR = DB_CONNECTION.cursor()
        DB_CONNECTION_CURSOR.execute(f'CREATE TABLE {DB_TABLE_NAME} ({COLUMNS_INFO});')
        DB_CONNECTION.commit()
        DB_CONNECTION.close()
    except Error as ERROR:
        raise Error(f'[Error]\nFunction: create_table()\n{ERROR}')

#THIS FUNCTION:
#1.) REQUIRES A DATABASE FILE PATH, DB TABLE NAME, COLUMN NAMES, AND ROW VALUES
#2.) INSERTS 1 OR MORE ROW VALUES, INTO THE COLUMN/S NAME/S
#3.) RAISES ANY ERRORS
def insert_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_VALUES):
    try:
        if not all([DB_FILE_PATH.strip(), DB_TABLE_NAME.strip(), COLUMNS.strip(), ROW_VALUES.strip()]):
            raise ValueError('[ValueError]\nFunction: insert_row_values()\nOne or more supplied values, were empty.')
        db_file_path_error_check(DB_FILE_PATH, 'insert_row_values()')
        if not is_quoted(DB_TABLE_NAME) and not bool(fullmatch(r'[A-Za-z0-9_]+', DB_TABLE_NAME)):
            raise ValueError('[ValueError]\nFunction: insert_row_values()\nThe supplied database table name, was invalid.\nWhen inserting row values into a database table, the table name, must be surrounded with quotes,\nto include characters other than letters, numbers, and underscores.')
        CONNECTION = connect(DB_FILE_PATH)
        CURSOR = CONNECTION.cursor()
        PLACEHOLDERS = ', '.join(['?' for COLUMN_NAME in COLUMNS.split(',')])
        ROW_VALUES_ARRAY = list(str(VALUE).strip() for VALUE in ROW_VALUES.split(','))
        CURSOR.execute(f'INSERT INTO {DB_TABLE_NAME} ({COLUMNS}) VALUES ({PLACEHOLDERS})', ROW_VALUES_ARRAY)
        CONNECTION.commit()
        CONNECTION.close()
    except Error as ERROR:
        raise Error(f'[Error]\nFunction: select_row_values()\n{ERROR}')

#THIS FUNCTION:
#1.) SELECTS 1 OR MORE ROW VALUES AND ALLOWS SPECIFYING THE WILDCARD "*" VALUE,
#IN THE "COLUMNS" PARAMETER, TO SELECT ALL COLUMNS
#2.) RETURNS THE SELECTED ROW VALUES AS A LIST OR RAISES AN ERROR:
def select_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_ID_COLUMN, ROW_ID_VALUE):
    try:
        if not all([DB_FILE_PATH.strip(), DB_TABLE_NAME.strip(), COLUMNS.strip(),ROW_ID_COLUMN.strip(), ROW_ID_VALUE.strip()]):
            raise ValueError('[ValueError]\nFunction: select_row_values()\nOne or more supplied values, were empty.')
        db_file_path_error_check(DB_FILE_PATH, 'select_row_values')
        if not bool(fullmatch(r'[A-Za-z0-9_]+', DB_TABLE_NAME)) and not is_quoted(DB_TABLE_NAME):
            raise ValueError('[ValueError]\nFunction: insert_row_values()\nThe supplied database table name, was invalid.\nWhen selecting row values from a database table, the table name, must be surrounded with quotes,\nto include characters other than letters, numbers, and underscores.')
        CONNECTION = connect(DB_FILE_PATH)
        CURSOR = CONNECTION.cursor()
        CURSOR = CONNECTION.cursor()
        CURSOR.execute(f'SELECT {COLUMNS} FROM {DB_TABLE_NAME} WHERE {ROW_ID_COLUMN} = ?', (ROW_ID_VALUE,))
        ROW_VALUES_TUPLE = CURSOR.fetchone()
        CONNECTION.close()

        #IF THE DATABASE RETURNS THE REQUESTED ROW VALUES, THEY ARE RETURNED AS A TUPLE.
        #THIS FUNCTION, CONVERTS THE TUPLE TO A LIST, FOR ITERATION CONVENIENCE.
        SELECTED_ROW_VALUES_LIST = ', '.join([str(VALUE) for VALUE in ROW_VALUES_TUPLE]).split(',')

        return SELECTED_ROW_VALUES_LIST
    except Error as ERROR:
        raise Error(f'[Error]\nFunction: select_row_values()\n{ERROR}')