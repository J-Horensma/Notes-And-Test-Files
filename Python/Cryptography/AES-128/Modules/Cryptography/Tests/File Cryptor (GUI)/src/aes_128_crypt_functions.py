from io import IOBase
from os import walk, replace, remove, fsync
from os.path import join, isdir, isfile, islink
from struct import pack, unpack
from base64 import urlsafe_b64encode
from secrets import token_bytes
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet, InvalidToken

#THIS FUNCTION:
#1.) REQUIRES A PASSWORD STRING
#2.) ACCEPTS AN OPTIONAL, 16-BYTE SALT BYTES
#3.) IF A 16-BYTE SALT, IS NOT SUPPLIED, A 16-BYTE SALT IS GENERATED
#4.) THE 16-BYTE SALT, IS USED TO GENERATE A 32-BYTE KEY, USING THE PBKDF2 KEY DERIVATION FUNCTION, WITH 200,000 ITERATIONS OF SHA256 HASHES
#5.) RETURNS A LIST, CONTAINING THE 32-BYTE KEY AND 16-BYTE SALT
def generate_key_and_salt(PASSWORD, SALT_BYTES=None):
    if not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "generate_key_and_salt()"\nThe supplied password parameter, was not a string type.')
    elif PASSWORD is None or PASSWORD.strip() == '':
        raise ValueError('[ValueError]\nFunction: "generate_key_and_salt()"\nThe supplied password parameter, was empty.')
    elif SALT_BYTES is not None and not isinstance(SALT_BYTES, bytes):
        raise TypeError('[TypeError]\nFunction: "generate_key_and_salt()"\nThe supplied salt bytes parameter, was not a bytes type.')
    elif SALT_BYTES is not None and len(SALT_BYTES) != 16:
        raise ValueError('[ValueError]\nFunction: "generate_key_and_salt()"\nThe supplied salt bytes parameter, was not 16 bytes long.')
    try:
        SALT_BYTES = token_bytes(16) if SALT_BYTES is None else SALT_BYTES
        KEY_DERIVATION_FUNCTION = PBKDF2HMAC(
            algorithm=SHA256(),
            length=32,
            salt=SALT_BYTES,
            iterations=200_000
        )
        KEY_BYTES = KEY_DERIVATION_FUNCTION.derive(PASSWORD.encode())
        return [KEY_BYTES, SALT_BYTES]
    except Exception as ERROR:
        raise Exception(f'[Exception]\nFunction: "generate_key_and_salt()"\n{ERROR}')

#THIS FUNCTION:
#1.) REQUIRES A FILE OBJECT OPENED, IN 'rb' MODE
#2.) CHECKS IF THE FILE IS EMPTY, IS AES-128 ENCRYPTED, AND IF THE SALT HEADER INTEGRITY IS CORRUPTED
#3.) RETURNS A LIST, CONTAINING THE SALT BYTES, FROM THE SALT HEADER AND THE TOTAL BYTES SIZE, OF THE SALT HEADER
def check_aes_128_salt_header(FILE):
    if not isinstance(FILE, IOBase) or 'r' not in FILE.mode or 'b' not in FILE.mode:
        raise TypeError('[TypeError]\nFunction: "check_aes_128_salt_header()"\nThe supplied file parameter, was not a file object, in read bytes mode.')
    try:
        TOTAL_SIZE = 0
        #READ THE FIRST 4 BYTES (THE SALT HEADER SIZE)
        SIZE_DATA = FILE.read(4)
        if not SIZE_DATA:
            FILE.seek(0)
            return [None, 'FILE_EMPTY']
        (HEADER_SIZE,) = unpack('>I', SIZE_DATA)
        #SALT HEADER SANITY CHECK
        if HEADER_SIZE <= 0 or HEADER_SIZE > 1024:
            FILE.seek(0)
            return [None, 'NOT_AES_128_ENCRYPTED']
        #READ THE SALT BYTES
        SALT_BYTES = FILE.read(HEADER_SIZE)
        if len(SALT_BYTES) != 16:
            FILE.seek(0)
            return [None, 'AES_128_SALT_HEADER_CORRUPTED']
        #TOTAL HEADER SIZE = 4 BYTES (SIZE DATA) + SALT BYTES
        TOTAL_SIZE = 4 + HEADER_SIZE
        #RESET THE FILE POINTER
        FILE.seek(0)
        return [SALT_BYTES, TOTAL_SIZE]
    except Exception as ERROR:
        raise Exception(f'[Exception]\nFunction: "check_aes_128_salt_header()"\n{ERROR}')
    
#THIS FUNCTION:
#1.) REQUIRES FOLDER PATH AND PASSWORD STRINGS
#2.) RECURSIVELY AES-128 ENCRYPTS ALL FILES, WITHIN THE SUPPLIED FOLDER PATH, SECURELY (ANY FILE TYPE)
def aes_128_encrypt_folder(FOLDER_PATH, PASSWORD):
    if not isinstance(FOLDER_PATH, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_encrypt_folder()"\nThe supplied folder path parameter, was not a string type.')
    elif not isdir(FOLDER_PATH):
        raise NotADirectoryError('[NotADirectoryError]\nFunction: "aes_128_encrypt_folder()"\nThe supplied folder path parameter, was not a path to an existing folder.')
    elif not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_encrypt_folder()"\nThe supplied password parameter, was not a string type.')
    elif not PASSWORD.strip():
        raise ValueError('[ValueError]\nFunction: "aes_128_encrypt_folder()"\nThe supplied password parameter, was empty.')
    try:
        for ROOT, DIRECTORIES, FILES in walk(FOLDER_PATH):
            FILES = [FILE for FILE in FILES if not FILE.startswith('.') and not FILE.endswith('ini') and not islink(join(ROOT, FILE))]
            ERRORS = []
            for FILE_NAME in FILES:
                FILE_PATH = join(ROOT, FILE_NAME)
                RESULT = aes_128_encrypt_file(FILE_PATH, PASSWORD)
                if 'ALREADY_AES_128_ENCRYPTED' in RESULT[1]:
                    ERRORS.append(RESULT[1])
                elif 'FILE_EMPTY' in RESULT[1]:
                    ERRORS.append(RESULT[1])
        if ERRORS:
            return [False, ERRORS]
        else:
            return [True, f'AES_128_FOLDER_ENCRYPTION_SUCCESSULL:\n{FOLDER_PATH}']
    except Exception as ERROR:
        raise Exception(f'[Exception]\nFunction: "aes_128_encrypt_folder()"\n{ERROR}\n{FOLDER_PATH}')

#THIS FUNCTION:
#1.) REQUIRES FOLDER PATH AND PASSWORD STRINGS
#2.) RECURSIVELY AES-128 DECRYPTS ALL FILES, WITHIN THE SUPPLIED FOLDER PATH, SECURELY (IF THE SUPPLIED PASSWORD, IS CORRECT)
def aes_128_decrypt_folder(FOLDER_PATH, PASSWORD):
    if not isinstance(FOLDER_PATH, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_decrypt_folder()"\nThe supplied folder path parameter, was not a string type.')
    elif not isdir(FOLDER_PATH):
        raise NotADirectoryError('[NotADirectoryError]\nFunction: "aes_128_decrypt_folder()"\nThe supplied folder path parameter, was not a path to an existing folder.')
    elif not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_decrypt_folder()"\nThe supplied password parameter, was not a string type.')
    elif not PASSWORD.strip():
        raise ValueError('[ValueError]\nFunction: "aes_128_decrypt_folder()"\nThe supplied password parameter, was empty.')
    try:
        for ROOT, DIRECTORIES, FILES in walk(FOLDER_PATH):
            FILES = [FILE for FILE in FILES if not FILE.startswith('.') and not FILE.endswith('ini') and not islink(join(ROOT, FILE))]
            ERRORS = []
            for FILE_NAME in FILES:
                FILE_PATH = join(ROOT, FILE_NAME)
                RESULT = aes_128_decrypt_file(FILE_PATH, PASSWORD)
                if 'NOT_AES_128_ENCRYPTED' in RESULT[1]:
                    ERRORS.append(RESULT[1])
                elif 'FILE_EMPTY' in RESULT[1]:
                    ERRORS.append(RESULT[1])
                elif 'AES_128_SALT_HEADER_CORRUPTED' in RESULT[1]:
                    ERRORS.append(RESULT[1])
                elif 'AES_128_ENCRYPTED_DATA_CORRUPTED' in RESULT[1]:
                    ERRORS.append(RESULT[1])
                elif 'INCORRECT_PASSWORD' in RESULT[1]:
                    ERRORS.append(RESULT[1])
        if ERRORS:
            return [False, ERRORS]
        else:
            return [True, f'AES_128_FOLDER_DECRYPTION_SUCCESS:\n{FOLDER_PATH}']
    except Exception as ERROR:
        raise Exception(f'[Exception]\nFunction: "aes_128_decrypt_folder()"\n{ERROR}\n{FOLDER_PATH}')

#1.) REQUIRES FILE PATH AND PASSWORD STRINGS
#2.) ACCEPTS AN OPTIONAL BLOCK SIZE INTEGER
#3.) AES-128 ENCRYPTS THE FILE, IN THE SUPPLIED FILE PATH, SECURELY (ANY FILE TYPE)
def aes_128_encrypt_file(FILE_PATH, PASSWORD, BLOCK_SIZE=None):
    if not isinstance(FILE_PATH, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_encrypt_file()"\nThe supplied file path parameter, was not a string type.')
    elif not isfile(FILE_PATH):
        raise FileNotFoundError('[FileNotFoundError]\nFunction: "aes_128_encrypt_file()"\nThe supplied file path parameter, was not a path to an existing file.')
    elif not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_encrypt_file()"\nThe supplied password parameter, was not a string type.')
    elif not PASSWORD.strip():
        raise ValueError('[ValueError]\nFunction: "aes_128_encrypt_file()"\nThe supplied password parameter, was empty.')
    try:
        BLOCK_SIZE = 65536 if BLOCK_SIZE is None else BLOCK_SIZE
        #CREATE A 32-BYTE KEY AND 16-BYTE SALT, USING THE "generate_key_and_salt()" FUNCTION AND THE USER-ENTERED PASSWORD, 
        #THEN WRITE THE SALT BYTES TO THE FILE, AS A HEADER, FOR LATER CREATION OF A MATCHING KEY, 
        #WHEN THE USER-ENTERED PASSWORD, IS CORRECT
        KEY_BYTES, SALT_BYTES = generate_key_and_salt(PASSWORD)
        #USE THE KEY, TO CREATE A CIPHER FOR THE AES-128 ENCRYPTION
        CIPHER = Fernet(urlsafe_b64encode(KEY_BYTES))
        with open(FILE_PATH, 'rb') as INFILE:
            #VALIDATE THE FILE, IS NOT ALREADY AES-128 ENCRYPTED OR EMPTY
            CHECK_SALT_HEADER_RESULT = check_aes_128_salt_header(INFILE)
            if CHECK_SALT_HEADER_RESULT[0]:
                return [False, f'ALREADY_AES_128_ENCRYPTED:\n{FILE_PATH}']
            elif CHECK_SALT_HEADER_RESULT[1] == 'FILE_EMPTY':
                return [False, f'FILE_EMPTY:\n{FILE_PATH}']
            #RESET THE FILE POINTER, AFTER THE SALT HEADER CHECK
            INFILE.seek(0)
            with open(FILE_PATH + '.tmp', 'wb') as OUTFILE:
                #WRITE 4 BYTES OF DATA, CONTAINING THE SIZE, IN BYTES,
                #BEFORE THE SALT BYTES HEADER, PLUS THE SALT BYTES HEADER
                OUTFILE.write(pack('>I', len(SALT_BYTES)) + SALT_BYTES)
                #ENCRYPT THE PLAINTEXT DATA, IN CHUNKS (TO ALLOW ENCRYPTION OF ALL FILE TYPES)
                while True:
                    PLAINTEXT_CHUNK = INFILE.read(BLOCK_SIZE)
                    if not PLAINTEXT_CHUNK:
                        break
                    ENCRYPTED_CHUNK = CIPHER.encrypt(PLAINTEXT_CHUNK)
                    #DELETE EACH PLAINTEXT DATA CHUNK, AFTER ENCRYPTION, TO PREVENT ANY PLAINTEXT DATA FROM BEING STORED, IN THE MEMORY
                    del PLAINTEXT_CHUNK
                    OUTFILE.write(pack('>I', len(ENCRYPTED_CHUNK)) + ENCRYPTED_CHUNK)
                    #DELETE EACH ENCRYPTED DATA CHUNK, AFTER WRITING TO THE ".tmp" FILE, TO PREVENT ANY ENCRYPTED DATA FROM BEING STORED, IN THE MEMORY
                    del ENCRYPTED_CHUNK
        #OVERWRITE THE ORIGINAL FILE'S PLAINTEXT CONTENTS WITH RANDOM BYTES,
        #BEFORE DELETION, TO PREVENT THE RECOVERY OF ANY PLAINTEXT DATA, FROM THE DRIVE
        with open(FILE_PATH, 'r+b') as RANDOM_BYTES_OVERWRITE_FILE:
            while True:
                PLAINTEXT_CHUNK = RANDOM_BYTES_OVERWRITE_FILE.read(BLOCK_SIZE)
                if not PLAINTEXT_CHUNK:
                    break
                RANDOM_BYTES_OVERWRITE_FILE.seek(-len(PLAINTEXT_CHUNK), 1)
                RANDOM_BYTES_OVERWRITE_FILE.write(token_bytes(len(PLAINTEXT_CHUNK)))
                #DELETE EACH PLAINTEXT DATA CHUNK, AFTER EACH RANDOM BYTES OVERWRITE, 
                #TO PREVENT ANY PLAINTEXT DATA FROM BEING STORED, IN THE MEMORY
                del PLAINTEXT_CHUNK
            RANDOM_BYTES_OVERWRITE_FILE.flush()
            fsync(RANDOM_BYTES_OVERWRITE_FILE.fileno())
        #DELETE THE ORIGINAL FILE AND RENAME THE ".tmp" FILE, TO THE ORIGINAL FILE NAME
        replace(FILE_PATH + '.tmp', FILE_PATH)
        return [True, f'AES_128_FILE_ENCRYPTION_SUCCESSFULL:\n{FILE_PATH}']
    except Exception as ERROR:
        try:
            remove(FILE_PATH + '.tmp')
            raise Exception(f'[Exception]\nFunction: "aes_128_encrypt_file()"\n{ERROR}\n{FILE_PATH}')
        except:
            raise Exception(f'[Exception]\nFunction: "aes_128_encrypt_file()"\n{ERROR}\n{FILE_PATH}\nAdditionally, the temp file: {FILE_PATH + '.tmp'},\nwas unable to be deleted.')

#THIS FUNCTION:
#1.) REQUIRES FILE PATH AND PASSWORD STRINGS
#2.) ACCEPTS AN OPTIONAL BLOCK SIZE INTEGER
#3.) AES-128 DECRYPTS THE FILE, IN THE SUPPLIED FILE PATH, SECURELY (IF THE SUPPLIED PASSWORD, IS CORRECT)
def aes_128_decrypt_file(FILE_PATH, PASSWORD, BLOCK_SIZE=None):
    if not isinstance(FILE_PATH, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_decrypt_file()"\nThe supplied file path parameter, was not a string type.')
    elif not isfile(FILE_PATH):
        raise FileNotFoundError('[FileNotFoundError]\nFunction: "aes_128_decrypt_file()"\nThe supplied file path parameter, was not a path to an existing file.')
    elif not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_decrypt_file()"\nThe supplied password parameter, was not a string type.')
    elif not PASSWORD.strip():
        raise ValueError('[ValueError]\nFunction: "aes_128_decrypt_file()"\nThe supplied password parameter, was empty.')
    try:
        BLOCK_SIZE = 65536 if BLOCK_SIZE is None else BLOCK_SIZE
        with open(FILE_PATH, 'rb') as INFILE:
            #VALIDATE THE FILE, IS AES-128 ENCRYPTED, NOT EMPTY, AND THE SALT HEADER IS NOT CORRUPTED
            CHECK_SALT_HEADER_RESULT = check_aes_128_salt_header(INFILE)
            if CHECK_SALT_HEADER_RESULT[1] == 'NOT_AES_128_ENCRYPTED':
                return [False, f'NOT_AES_128_ENCRYPTED:\n{FILE_PATH}']
            elif CHECK_SALT_HEADER_RESULT[1] == 'FILE_EMPTY':
                return [False, f'FILE_EMPTY:\n{FILE_PATH}']
            elif CHECK_SALT_HEADER_RESULT[1] == 'AES_128_SALT_HEADER_CORRUPTED':
                return [False, f'AES_128_SALT_HEADER_CORRUPTED:\n{FILE_PATH}']
            SALT_BYTES, TOTAL_SALT_HEADER_SIZE = CHECK_SALT_HEADER_RESULT
            #DERIVE A DECRYPTION KEY, THAT MATCHES THE ORIGINAL ENCRYPTION KEY,
            #USING THE USER-ENTERED PASSWORD AND THE SALT BYTES STORED, IN THE AES-128 ENCRYPTED FILE'S SALT HEADER
            KEY_BYTES = generate_key_and_salt(PASSWORD, SALT_BYTES)[0]
            #DELETE THE PASSWORD, ONCE A KEY IS DERIVED, TO PREVENT ANY PASSWORD DATA FROM BEING STORED, IN THE MEMORY
            del PASSWORD
            #USE THE KEY BYTES, TO CREATE A CIPHER FOR DECRYPTION
            CIPHER = Fernet(urlsafe_b64encode(KEY_BYTES))
            #SET THE FILE POINTER, TO THE FIRST ENCRYPTED FILE CHUNK, AFTER THE ENCRYPTED FILE'S SALT HEADER
            INFILE.seek(TOTAL_SALT_HEADER_SIZE)
            with open(FILE_PATH + '.tmp', 'wb') as OUTFILE:
                #DECRYPT THE ENCRYPTED DATA, IN CHUNKS (TO ALLOW DECRYPTION OF ALL FILE TYPES)
                while True:
                    SIZE_DATA = INFILE.read(4)
                    if not SIZE_DATA or len(SIZE_DATA) < 4:
                        break
                    (CHUNK_SIZE,) = unpack('>I', SIZE_DATA)
                    if CHUNK_SIZE <= 0:
                        try:
                            remove(FILE_PATH + '.tmp')
                            return [False, f'AES_128_ENCRYPTED_DATA_CORRUPTED:\n{FILE_PATH}']
                        except:
                            return [False, f'AES_128_ENCRYPTED_DATA_CORRUPTED:\n{FILE_PATH}\nAdditionally, the temp file: {FILE_PATH + ".tmp"},\nwas unable to be deleted.']
                    ENCRYPTED_CHUNK = INFILE.read(CHUNK_SIZE)
                    if len(ENCRYPTED_CHUNK) != CHUNK_SIZE:
                        try:
                            remove(FILE_PATH + '.tmp')
                            return [False, f'AES_128_ENCRYPTED_DATA_CORRUPTED:\n{FILE_PATH}']
                        except:
                            return [False, f'AES_128_ENCRYPTED_DATA_CORRUPTED:\n{FILE_PATH}\nAdditionally, the temp file: {FILE_PATH + ".tmp"},\nwas unable to be deleted.']
                    PLAINTEXT_CHUNK = CIPHER.decrypt(ENCRYPTED_CHUNK)
                    #DELETE EACH ENCRYPTED DATA CHUNK, AFTER DECRYPTION, TO PREVENT ANY ENCRYPTED DATA FROM BEING STORED, IN THE MEMORY
                    del ENCRYPTED_CHUNK
                    OUTFILE.write(PLAINTEXT_CHUNK)
                    #DELETE EACH PLAINTEXT DATA CHUNK, AFTER WRITING THE CHUNK, TO THE ".tmp" FILE, 
                    #TO PREVENT ANY PLAINTEXT DATA FROM BEING STORED, IN THE MEMORY
                    del PLAINTEXT_CHUNK
        #OVERWRITE THE ORIGINAL FILE'S ENCRYPTED CONTENTS WITH RANDOM BYTES,
        #BEFORE DELETION, TO PREVENT THE RECOVERY, OF ANY ENCRYPTED DATA, FROM THE DRIVE
        with open(FILE_PATH, 'r+b') as RANDOM_BYTES_OVERWRITE_FILE:
            while True:
                ENCRYPTED_CHUNK = RANDOM_BYTES_OVERWRITE_FILE.read(BLOCK_SIZE)
                if not ENCRYPTED_CHUNK:
                    break
                RANDOM_BYTES_OVERWRITE_FILE.seek(-len(ENCRYPTED_CHUNK), 1)
                RANDOM_BYTES_OVERWRITE_FILE.write(token_bytes(len(ENCRYPTED_CHUNK)))
                #DELETE EACH AES-128 ENCRYPTED DATA CHUNK, AFTER EACH RANDOM BYTES OVERWRITE, 
                #OF THE FILE CHUNK, TO PREVENT ANY AES-128 ENCRYPTED DATA FROM BEING STORED, IN THE MEMORY
                del ENCRYPTED_CHUNK
            RANDOM_BYTES_OVERWRITE_FILE.flush()
            fsync(RANDOM_BYTES_OVERWRITE_FILE.fileno())
        #DELETE THE ORIGINAL FILE AND RENAME THE ".tmp" FILE, TO THE ORIGINAL FILE NAME
        replace(FILE_PATH + '.tmp', FILE_PATH)
        return [True, f'AES_128_FILE_DECRYPTION_SUCCESSFULL:\n{FILE_PATH}']
    except InvalidToken:
        try:
            remove(FILE_PATH + '.tmp')
            return [False, f'INCORRECT_PASSWORD:\n{FILE_PATH}']
        except:
            return [False, f'INCORRECT_PASSWORD:\n{FILE_PATH}\nAdditionally, the temp file: {FILE_PATH + ".tmp"},\nwas unable to be deleted.']
    except Exception as ERROR:
            try:
                remove(FILE_PATH + '.tmp')
                raise Exception(f'[Exception]\nFunction: "aes_128_decrypt_file()"\n{ERROR}\n{FILE_PATH}')
            except:
                raise Exception(f'[Exception]\nFunction: "aes_128_decrypt_file()"\n{ERROR}\n{FILE_PATH}\nAdditionally, the temp file: {FILE_PATH + ".tmp"},\nwas unable to be deleted.')
        
#THIS FUNCTION:
#1.) REQUIRES A STRING OR BYTES TYPE VARIABLE AND A PASSWORD STRING
#2.) AES-128 ENCRYPTS, THE SUPPLIED STRING OR BYTES TYPE VARIABLE
#3.) RETURNS A LIST, CONTAINING THE ENCRYPTED VARIABLE BYTES AND A 16-BYTE SALT
#NOTE: THE SALT BYTES, SHOULD BE STORED SOMEWHERE (FOR LATER DECRYPTION)
def aes_128_encrypt_variable(PLAINTEXT_VARIABLE, PASSWORD):
    if not isinstance(PLAINTEXT_VARIABLE, str) and not isinstance(PLAINTEXT_VARIABLE, bytes):
        raise TypeError('[TypeError]\nFunction: "aes_128_encrypt_variable()"\nThe supplied plaintext variable parameter, was not a string or bytes type.')
    elif not PLAINTEXT_VARIABLE.strip() or PLAINTEXT_VARIABLE is None:
        raise ValueError('[ValueError]\nFunction: "aes_128_encrypt_variable()"\nThe supplied plaintext variable parameter, was empty.')
    elif not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_encrypt_variable()"\nThe supplied plaintext variable parameter, was not a string type.')
    elif not PASSWORD.strip():
        raise ValueError('[ValueError]\nFunction: "aes_128_encrypt_variable()"\nThe supplied plaintext variable parameter, was empty.')
    try:
        PLAINTEXT_VARIABLE = PLAINTEXT_VARIABLE.encode() if isinstance(PLAINTEXT_VARIABLE, str) else PLAINTEXT_VARIABLE
        KEY_BYTES, SALT_BYTES = generate_key_and_salt(PASSWORD)
        CIPHER = Fernet(urlsafe_b64encode(KEY_BYTES))
        ENCRYPTED_VARIABLE_BYTES = CIPHER.encrypt(PLAINTEXT_VARIABLE)
        return [ENCRYPTED_VARIABLE_BYTES, SALT_BYTES]
    except Exception as ERROR:
        raise Exception(f'[Exception]\nFunction: "aes_128_encrypt_variable()"\n{ERROR}')

#THIS FUNCTION:
#1.) REQUIRES AES-128 ENCRYPTED BYTES, A PASSWORD STRING (USED TO ENCRYPT, THE VARIABLE), AND THE SALT BYTES
#RETURNED BY THE "aes_128_encrypt_variable()" FUNCTION
#2.) AES-128 DECRYPTS, THE SUPPLIED STRING OR BYTES TYPE VARIABLE
#3.) RETURNS THE AES-128 DECRYPTED BYTES OR "None", IF THE SUPPLIED PASSWORD, WAS INCORRECT
def aes_128_decrypt_variable(ENCRYPTED_VARIABLE_BYTES, PASSWORD, SALT_BYTES):
    if not isinstance(ENCRYPTED_VARIABLE_BYTES, bytes):
        raise TypeError('[TypeError]\nFunction: "aes_128_decrypt_variable()"\nThe supplied encrypted variable bytes parameter, was not a bytes type.')
    elif not ENCRYPTED_VARIABLE_BYTES:
        raise ValueError('[ValueError]\nFunction: "aes_128_decrypt_variable()"\nThe supplied encrypted variable bytes parameter, was empty.')
    elif not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_decrypt_variable()"\nThe supplied password parameter, was not a string type.')
    elif not PASSWORD.strip():
        raise ValueError('[ValueError]\nFunction: "aes_128_decrypt_variable()"\nThe supplied password parameter, was empty.')
    elif not isinstance(SALT_BYTES, bytes):
        raise TypeError('[TypeError]\nFunction: "aes_128_decrypt_variable()"\nThe supplied salt bytes parameter, was not a bytes type.')
    elif not SALT_BYTES:
        raise ValueError('[ValueError]\nFunction: "aes_128_decrypt_variable()"\nThe supplied salt bytes parameter, was empty.')
    elif len(SALT_BYTES) != 16:
        raise ValueError('[ValueError]\nFunction: "aes_128_decrypt_variable()"\nThe supplied salt bytes parameter, was not 16 bytes long.')
    try:
        KEY_BYTES, SALT_BYTES = generate_key_and_salt(PASSWORD, SALT_BYTES)
        CIPHER = Fernet(urlsafe_b64encode(KEY_BYTES))
        PLAINTEXT_VARIABLE = CIPHER.decrypt(ENCRYPTED_VARIABLE_BYTES)
        return PLAINTEXT_VARIABLE
    except InvalidToken:
        return None
    except Exception as ERROR:
        raise Exception(f'[Exception]\nFunction: "aes_128_decrypt_variable()"\n{ERROR}')