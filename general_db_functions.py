from os.path import exists, isabs, isfile
from inspect import currentframe
from re import fullmatch
from sqlite3 import connect, Error
from base64 import b64encode, b64decode
from secrets import token_bytes, compare_digest
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
#1.) CHECKS THE FUNCTION NAME, OF THE FUNCTION CALLING THE FUNCTION,
#THAT CALLS THIS FUNCTION, FOR RAISED ERROR MESSAGES. 
def get_parent_function_name():
    PARENT_FUNCTION_NAME = currentframe().f_back.f_code.co_name
    return PARENT_FUNCTION_NAME

#THIS FUNCTION:
#1.) REQUIRES A DATABASE FILE PATH STRING
#2.) CHECKS FOR DATABASE FILE PATH ERRORS
#2.) RAISES ANY ERRORS FOUND
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
    if not isinstance(STRING, str):
        raise TypeError('[TypeError]\nFunction: "unquote()"\nThe supplied string parameter, was not a string.')
    if not STRING.strip():
        raise ValueError('[ValueError]\nFunction: "unquote()"\nThe supplied string parameter, was empty.')
    if STRING[0] == STRING[-1] and STRING[0] in ("'", '"') and STRING.count(STRING[0]) == 2:
        STRING = STRING.replace(STRING[0], '')
        return STRING
    else:
        return STRING

#THIS FUNCTION:
#1.) REQUIRES A STRING AND ACCEPTS AN OPTIONAL SALT BYTES PARAMETER
#2.) HASHES THE STRING TO SHA256 HASH BYTES
#3.) CREATES RANDOM SALT BYTES (IF NOT SUPPLIED, WITH THE OPTIONAL SALT BYTES PARAMETER)
#4.) BASE64 ENCODES THE HASH AND SALT BYTES TO STRINGS (FOR EASIER DATABASE STORAGE)
#5.) RETURNS BASE64 ENCODED HASH AND SALT STRINGS, AS A LIST
#NOTE: THIS FUNCTION, MEETS THE CRITERIA FOR "RFC 8018" AND "NIST SP 800‑63B",
#MEANING IT MEETS THE SECURITY STANDARDS, FOR HASHING PASSWORDS AND GENERATING SALTS, 
#TO BE STORED IN A DATABASE FOR LATER PASSWORD VERIFICATION.
def get_hash_and_salt(STRING, SALT_BYTES=None):
    SALT_BYTES = token_bytes(16) if SALT_BYTES is None else SALT_BYTES
    if not all([isinstance(STRING, str), isinstance(SALT_BYTES, bytes)]):
        raise TypeError(f'[TypeError]\nFunction: "get_hash_and_salt()"\nOne or more, supplied parameter/s, were not the correct type.')
    if not STRING.strip():
        raise ValueError(f'[ValueError]\nFunction: "get_hash_and_salt()"\nThe supplied string parameter, was empty.')
    HASH = pbkdf2_hmac(
        'sha256',
        STRING.encode('utf-8'),
        SALT_BYTES,
        100_000 #(THE NUMBER OF TIMES THE STRING AND SALT BYTES, ARE HASHED)
    )

    #SOMETIMES, A DATABASE WILL NOT ALLOW STORING RAW BYTES, WITHOUT PRE-CONFIGURATION,
    #TO AVOID THIS, CONVERT THE HASH AND SALT BYTES TO BASE64 STRINGS.
    BASE64_ENCODED_HASH = b64encode(HASH).decode('utf-8')
    BASE64_ENCODED_SALT = b64encode(SALT_BYTES).decode('utf-8')

    BASE64_ENCODED_HASH_AND_SALT_TUPLE = (BASE64_ENCODED_HASH, BASE64_ENCODED_SALT)
    return BASE64_ENCODED_HASH_AND_SALT_TUPLE

#THIS FUNCTION:
#1.) REQUIRES PASSWORD, DATABASE STORED BASE64 ENCODED HASH STRING, AND DB STORED BASE64 ENCODED SALT STRINGS
#2.) CONVERTS THE DATABASE STORED BASE64 ENCODED SALT STRING, TO BYTES
#3.) CONVERTS THE PASSWORD TO A BASE64 ENCODED HASH STRING, USING THE DATABASE STORED BASE64 ENCODED SALT STRING
#4.) COMPARES THE HASH STRING, TO THE DATABASE STORED HASH STRING
#5.) RETURNS "True" IF THE HASHES MATCH, OR "False" IF THEY DO NOT MATCH OR AN ERROR OCCURS
def is_password_valid(PASSWORD, DB_STORED_BASE64_ENCODED_HASH, DB_STORED_BASE64_ENCODED_SALT):
    try:
        DB_STORED_HASH_BYTES = b64decode(DB_STORED_BASE64_ENCODED_HASH)
        DB_STORED_SALT_BYTES = b64decode(DB_STORED_BASE64_ENCODED_SALT)
        BASE64_ENCODED_HASH, _ = get_hash_and_salt(PASSWORD, DB_STORED_SALT_BYTES)
        HASH_BYTES = b64decode(BASE64_ENCODED_HASH)
        BOOLEAN = compare_digest(HASH_BYTES, DB_STORED_HASH_BYTES)
        return BOOLEAN
    except Exception as ERROR:
        return False

#THIS FUNCTION:
#1.) REQUIRES DATABASE FILE PATH AND DB TABLE NAME STRINGS
#2.) CHECKS IF A DB TABLE, ALREADY EXISTS
#3.) RETURNS "True" IF THE TABLE EXISTS, OR "False" IF IT DOES NOT EXIST OR AN ERROR OCCURS
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
#WITH THE COLUMN/S INFO, SPECIFYING THE COLUMN NAMES AND ATTRIBUTES, SEPARATED BY COMMAS,
#E.G.: 
#COLUMNS_INFO = '''
#id INTEGER PRIMARY KEY, 
#username TEXT NOT NULL UNIQUE, #(TYPE: TEXT, INSERTED ROW VALUES CANNOT BE EMPTY, ROW VALUES MUST BE UNIQUE)
#password_hash TEXT NOT NULL, 
#password_salt TEXT NOT NULL
#'''
#2.) CREATES A DATABASE TABLE, WITH THE SUPPLIED TABLE NAME AND COLUMN/S INFO
#3.) RAISES ANY ERRORS
def create_table(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS_INFO):
    try:
        if not all([isinstance(VALUE, str) for VALUE in (DB_TABLE_NAME, DB_TABLE_NAME, COLUMNS_INFO)]):
            raise TypeError('[TypeError]\nFunction: "create_table()"\nOne or more, supplied parameter/s, were not the a string type.')
        if not all([VALUE.strip() for VALUE in (DB_FILE_PATH,DB_TABLE_NAME, COLUMNS_INFO)]):
            raise ValueError('[ValueError]\nFunction: "create_table()"\nOne or more supplied parameter/s, were empty.')
        db_file_path_error_check(DB_FILE_PATH)
        if is_quoted(DB_TABLE_NAME) or bool(fullmatch(r'[A-Za-z0-9_]+', DB_TABLE_NAME)):
            TEMP_DB_TABLE_NAME = unquote(DB_TABLE_NAME) if is_quoted(DB_TABLE_NAME) else DB_TABLE_NAME
            if table_exists(DB_FILE_PATH, TEMP_DB_TABLE_NAME):
                raise ValueError('[ValueError]\nFunction: "create_table()"\nThe supplied database table name, already exists.')
        else:
            raise ValueError('[ValueError]\nFunction: "create_table()"\nThe supplied database table name, was invalid.\nWhen creating a database table, the table name, must be surrounded with quotes,\nto include characters other than letters, numbers, and underscores.')
        DB_CONNECTION = connect(DB_FILE_PATH)
        DB_CONNECTION_CURSOR = DB_CONNECTION.cursor()
        DB_CONNECTION_CURSOR.execute(f'CREATE TABLE {DB_TABLE_NAME} ({COLUMNS_INFO});')
        DB_CONNECTION.commit()
        DB_CONNECTION.close()
    except Error as ERROR:
        raise Error(f'[Error]\nFunction: "create_table()"\n{ERROR}')

#THIS FUNCTION:
#1.) REQUIRES DATABASE FILE PATH, DB TABLE NAME, COLUMN/S, AND ROW VALUES STRINGS
#2.) INSERTS 1 OR MORE ROW VALUES, INTO THE COLUMN/S NAME/S
#3.) RAISES ANY ERRORS
def insert_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_VALUES):
    try:
        if not all([isinstance(VALUE, str) for VALUE in (DB_TABLE_NAME, DB_TABLE_NAME, COLUMNS, ROW_VALUES)]):
            raise TypeError('[TypeError]\nFunction: "insert_row_values()"\nOne or more, supplied parameter/s, were not a string type.')
        if not all([VALUE.strip() for VALUE in [DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_VALUES]]):
            raise ValueError('[ValueError]\nFunction: "insert_row_values()"\nOne or more supplied parameter/s, were empty.')
        db_file_path_error_check(DB_FILE_PATH)
        if not is_quoted(DB_TABLE_NAME) and not bool(fullmatch(r'[A-Za-z0-9_]+', DB_TABLE_NAME)):
            raise ValueError('[ValueError]\nFunction: "insert_row_values()"\nThe supplied database table name, was invalid.\nWhen inserting row values into a database table, the table name, must be surrounded with quotes,\nto include characters other than letters, numbers, and underscores.')
        CONNECTION = connect(DB_FILE_PATH)
        CURSOR = CONNECTION.cursor()
        PLACEHOLDERS = ', '.join(['?' for COLUMN_NAME in COLUMNS.split(',')])

        #NOTE: THE ROW VALUES TO INSERT INTO THE DATABASE TABLE, 
        #MUST BE CONVERTED TO A LIST, BEFORE, BEING PASSED TO THE 
        #"sqlite3.connect.cursor.execute()" FUNCTION, SO THE DATABASE
        #DOES NOT SEE IT AS A SINGLE VALUE TO INSERT, EVEN WHEN IT'S NOT,
        #WHICH LEADS TO A DATABASE ERROR, BEING RAISED. 
        #TUPLES CAN BE ITERATED, LIKE A LIST, BUT THEY ARE SEEN AS A SINGLE VALUE,
        #WHEN PASSED, TO THE "INSERT" STATEMENT, 
        #IN THE "sqlite3.connect.cursor.execute()" FUNCTION.
        ROW_VALUES_LIST = [str(VALUE).strip() for VALUE in ROW_VALUES.split(',')]

        CURSOR.execute(f'INSERT INTO {DB_TABLE_NAME} ({COLUMNS}) VALUES ({PLACEHOLDERS})', ROW_VALUES_LIST)
        CONNECTION.commit()
        CONNECTION.close()
    except Error as ERROR:
        raise Error(f'[Error]\nFunction: "insert_row_values()"\n{ERROR}')

#THIS FUNCTION:
#1.) REQUIRES DATABASE FILE PATH, DB TABLE NAME, COLUMN/S, ROW ID COLUMN, AND ROW VALUE STRINGS
#2.) SELECTS 1 OR MORE ROW VALUES AND ALLOWS SPECIFYING THE WILDCARD "*" VALUE,
#IN THE "COLUMNS" PARAMETER, TO SELECT ALL COLUMNS
#3.) RETURNS THE SELECTED ROW VALUES AS A LIST OR RAISES AN ERROR:
def select_row_values(DB_FILE_PATH, DB_TABLE_NAME, COLUMNS, ROW_ID_COLUMN, ROW_ID_VALUE):
    try:
        if not all([DB_FILE_PATH.strip(), DB_TABLE_NAME.strip(), COLUMNS.strip(),ROW_ID_COLUMN.strip(), ROW_ID_VALUE.strip()]):
            raise ValueError('[ValueError]\nFunction: "select_row_values()"\nOne or more supplied parameter/s, were empty.')
        db_file_path_error_check(DB_FILE_PATH)
        if not bool(fullmatch(r'[A-Za-z0-9_]+', DB_TABLE_NAME)) and not is_quoted(DB_TABLE_NAME):
            raise ValueError('[ValueError]\nFunction: "select_row_values()"\nThe supplied database table name, was invalid.\nWhen selecting row values from a database table, the table name, must be surrounded with quotes,\nto include characters other than letters, numbers, and underscores.')
        CONNECTION = connect(DB_FILE_PATH)
        CURSOR = CONNECTION.cursor()
        CURSOR = CONNECTION.cursor()
        CURSOR.execute(f'SELECT {COLUMNS} FROM {DB_TABLE_NAME} WHERE {ROW_ID_COLUMN} = ?', (ROW_ID_VALUE,))
        SELECTED_ROW_VALUES_TUPLE = CURSOR.fetchone()
        CONNECTION.close()
        return SELECTED_ROW_VALUES_TUPLE
    except Error as ERROR:
        raise Error(f'[Error]\nFunction: "select_row_values()"\n{ERROR}')