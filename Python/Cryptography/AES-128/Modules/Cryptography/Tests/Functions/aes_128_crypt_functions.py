from io import IOBase
from os import walk, replace, remove, urandom, fsync
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
#3.) IF A SALT, IS NOT SUPPLIED, A 16 BYTE SALT IS GENERATED
#4.) THE 16 BYTE SALT, IS USED TO GENERATE A 32 BYTE HASH, USING THE PBKDF2 HASHING ALGORITHM, WITH 200,000 ITERATIONS OF SHA256
#5.) RETURNS A LIST, CONTAINING THE 32 BYTE HASH BYTES AND THE 16 BYTE SALT BYTES
#NOTE: THIS FUNCTION, MEETS THE CRITERIA FOR "RFC 8018" AND "NIST SP 800‑63B",
#MEANING IT MEETS THE SECURITY STANDARDS FOR HASHING PASSWORDS AND GENERATING SALTS, 
#TO BE STORED IN A DATABASE, FOR LATER PASSWORD VERIFICATION.
def get_hash_and_salt(PASSWORD, SALT_BYTES=None):
    if not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "get_hash_and_salt()"\nThe supplied password parameter, was not a string type.')
    elif PASSWORD is None or PASSWORD.strip() == '':
        raise ValueError('[ValueError]\nFunction: "get_hash_and_salt()"\nThe supplied password parameter, was empty.')
    elif SALT_BYTES is not None and not isinstance(SALT_BYTES, bytes):
        raise TypeError('[TypeError]\nFunction: "get_hash_and_salt()"\nThe supplied salt parameter, was not a bytes type.')
    elif SALT_BYTES is not None and len(SALT_BYTES) != 16:
        raise ValueError('[ValueError]\nFunction: "get_hash_and_salt()"\nThe supplied salt parameter, was not 16 bytes long.')
    SALT_BYTES = token_bytes(16) if SALT_BYTES is None else SALT_BYTES
    ALGORITHM = PBKDF2HMAC(
        algorithm=SHA256(),
        length=32,
        salt=SALT_BYTES,
        iterations=200_000
    )
    PASSWORD_BYTES = PASSWORD.encode()
    HASH_BYTES = ALGORITHM.derive(PASSWORD_BYTES)
    return [HASH_BYTES, SALT_BYTES]

#THIS FUNCTION:
#1.) REQUIRES A FILE OBJECT, IN 'rb' MODE
#2.) CHECKS IF THE FILE IS AES-128 ENCRYPTED AND VALIDATES THE AES-128 ENCRYPTION HEADERS
#3.) RETURNS THE AES-128 ENCRYPTION HEADERS AND THE TOTAL SIZE, OF THEM
def check_aes_128_encryption_headers(FILE):
    if not isinstance(FILE, IOBase) or 'r' not in FILE.mode or 'b' not in FILE.mode:
        raise TypeError('[TypeError]\nFunction: "check_aes_128_encryption_headers()"\nThe supplied file parameter, was not a file object, in read bytes mode.')
    HEADERS = []
    HEADER_NUMBER = 1
    TOTAL_SIZE = 0
    SIZE_DATA = FILE.read(4)
    FILE.seek(0)
    if not SIZE_DATA or len(SIZE_DATA) < 4:
        FILE.seek(0)
        return [None, 'FILE_EMPTY']
    while True:
        SIZE_DATA = FILE.read(4)
        if len(SIZE_DATA) < 4:
            FILE.seek(0)
            return [None, 'HEADERS_CORRUPTED']
        (HEADER_SIZE,) = unpack('>I', SIZE_DATA)
        if HEADER_NUMBER == 1 and HEADER_SIZE > 1024:
            FILE.seek(0)
            return [None, 'NOT_AES_128_ENCRYPTED']
        HEADER_DATA = FILE.read(HEADER_SIZE)
        if len(HEADER_DATA) != HEADER_SIZE:
            FILE.seek(0)
            return [None, 'HEADERS_CORRUPTED']
        elif HEADER_NUMBER == 2:
            HEADER = HEADER_DATA
            if len(HEADER) != 16:
                FILE.seek(0)
                return [None, 'HEADERS_CORRUPTED']
        else:
            try:
                HEADER = HEADER_DATA.decode('utf-8', 'strict')
            except UnicodeDecodeError:
                FILE.seek(0)
                return [None, 'NOT_AES_128_ENCRYPTED']
        if HEADER_NUMBER == 1 and HEADER != 'START_AES_128_ENCRYPTION_HEADERS':
            FILE.seek(0)
            return [None, 'HEADERS_CORRUPTED']
        elif HEADER_NUMBER == 3 and HEADER != 'END_AES_128_ENCRYPTION_HEADERS':
            FILE.seek(0)
            return [None, 'HEADERS_CORRUPTED']
        TOTAL_SIZE += 4 + HEADER_SIZE
        HEADERS.append(HEADER)
        if HEADER_NUMBER == 3:
            FILE.seek(0)
            break
        HEADER_NUMBER += 1
    return [HEADERS, TOTAL_SIZE]

#THIS FUNCTION:
#1.) REQUIRES FOLDER PATH AND PASSWORD STRINGS
#2.) RECURSIVELY AND SECURELY AES-128 ENCRYPTS ALL FILES, WITHIN THE SUPPLIED FOLDER PATH
def aes_128_encrypt_folder(FOLDER_PATH, PASSWORD):
    if not isinstance(FOLDER_PATH, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_encrypt_folder()"\nThe supplied folder path parameter, was not a string type.')
    elif not isdir(FOLDER_PATH):
        raise NotADirectoryError('[NotADirectoryError]\nFunction: "aes_128_encrypt_folder()"\nThe supplied folder path parameter, was not a path to an existing folder.')
    elif not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_encrypt_folder()"\nThe supplied password parameter, was not a string type.')
    elif PASSWORD.strip() == '':
        raise ValueError('[ValueError]\nFunction: "aes_128_encrypt_folder()"\nThe supplied password parameter, was empty.')
    try:
        for ROOT, DIRECTORIES, FILES in walk(FOLDER_PATH):
            FILES = [FILE for FILE in FILES if not FILE.startswith('.') and not FILE.endswith('ini') and not islink(join(ROOT, FILE))]
            ERRORS = []
            FILE_COUNT = len(FILES)
            for FILE_NAME in FILES:
                FILE_PATH = join(ROOT, FILE_NAME)
                RESULT = aes_128_encrypt_file(FILE_PATH, PASSWORD)
                if 'FILE_EMPTY' in RESULT[1]:
                    ERRORS.append(RESULT[1])
                elif 'ALREADY_AES_128_ENCRYPTED' in RESULT[1]:
                    ERRORS.append(RESULT[1])
                elif 'AES_128_FILE_ENCRYPTION_FAILED' in RESULT[1]:
                    ERRORS.append(RESULT[1])
        if ERRORS:
            return [False, ERRORS]
        else:
            return [True, f'AES_128_FOLDER_ENCRYPTION_SUCCESSULL:\n{FOLDER_PATH}']
    except:
        return [False, f'AES_128_FOLDER_ENCRYPTION_FAILED:\n{FOLDER_PATH}']

#THIS FUNCTION:
#1.) REQUIRES FOLDER PATH AND PASSWORD STRINGS
#2.) RECURSIVELY DECRYPTS ALL FILES, WITHIN THE SUPPLIED FOLDER PATH
def aes_128_decrypt_folder(FOLDER_PATH, PASSWORD):
    if not isinstance(FOLDER_PATH, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_decrypt_folder()"\nThe supplied folder path parameter, was not a string type.')
    elif not isdir(FOLDER_PATH):
        raise NotADirectoryError('[NotADirectoryError]\nFunction: "aes_128_decrypt_folder()"\nThe supplied folder path parameter, was not a path to an existing folder.')
    elif not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_decrypt_folder()"\nThe supplied password parameter, was not a string type.')
    elif PASSWORD.strip() == '':
        raise ValueError('[ValueError]\nFunction: "aes_128_decrypt_folder()"\nThe supplied password parameter, was empty.')
    try:
        for ROOT, DIRECTORIES, FILES in walk(FOLDER_PATH):
            FILES = [FILE for FILE in FILES if not FILE.startswith('.') and not FILE.endswith('ini') and not islink(join(ROOT, FILE))]
            ERRORS = []
            for FILE_NAME in FILES:
                FILE_PATH = join(ROOT, FILE_NAME)
                RESULT = aes_128_decrypt_file(FILE_PATH, PASSWORD)
                print(RESULT)
                if 'NOT_AES_128_ENCRYPTED' in RESULT[1]:
                    ERRORS.append(RESULT[1])
                elif 'FILE_EMPTY' in RESULT[1]:
                    ERRORS.append(RESULT[1])
                elif 'HEADERS_CORRUPTED' in RESULT[1]:
                    ERRORS.append(RESULT[1])
                elif 'AES_128_ENCRYPTED_DATA_CORRUPTED' in RESULT[1]:
                    ERRORS.append(RESULT[1])
                elif 'INCORRECT_PASSWORD' in RESULT[1]:
                    ERRORS.append(RESULT[1])
        if ERRORS:
            return [False, ERRORS]
        else:
            return [True, f'AES_128_FOLDER_DECRYPTION_SUCCESS:\n{FOLDER_PATH}']
    except:
        return [False, f'AES_128_FOLDER_DECRYPTION_FAILED:\n{FOLDER_PATH}']

#1.) REQUIRES FILE PATH AND PASSWORD STRINGS
#2.) ACCEPTS AN OPTIONAL BLOCK SIZE INTEGER
#3.) AES-128 ENCRYPTS THE FILE, SECURELY, IN THE SUPPLIED FILE PATH (ANY FILE TYPE)
def aes_128_encrypt_file(FILE_PATH, PASSWORD, BLOCK_SIZE=None):
    if not isinstance(FILE_PATH, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_encrypt_file()"\nThe supplied file path parameter, was not a string type.')
    elif not isfile(FILE_PATH):
        raise FileNotFoundError('[FileNotFoundError]\nFunction: "aes_128_encrypt_file()"\nThe supplied file path parameter, was not a path to an existing file.')
    elif not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_encrypt_file()"\nThe supplied password parameter, was not a string type.')
    elif PASSWORD.strip() == '' or PASSWORD is None:
        raise ValueError('[ValueError]\nFunction: "aes_128_encrypt_file()"\nThe supplied password parameter, was empty.')
    try:
        BLOCK_SIZE = 65536 if BLOCK_SIZE is None else BLOCK_SIZE
        #CREATE A SALT AND HASH, USING THE "get_hash_and_salt()" FUNCTION
        #AND THE USER-ENTERED PASSWORD, THEN WRITE THE SALT TO THE AES-128 ENCRYPTED
        #FILE HEADERS, FOR LATER CREATION OF A MATCHING HASH, WHEN THE USER-ENTERED PASSWORD
        #IS SUPPLIED TO DECRYPT THE AES-128 ENCRYPTED FILE
        HASH_BYTES, SALT_BYTES = get_hash_and_salt(PASSWORD)
        #USE THE HASH, AS A KEY, TO CREATE A CIPHER FOR ENCRYPTION
        CIPHER = Fernet(urlsafe_b64encode(HASH_BYTES))
        #STREAM THE PLAINTEXT DATA, TO A ".tmp" FILE, WHILE ENCRYPTING THE DATA BETWEEN THE 2 FILES, 
        #TO PREVENT LOADING ANY OF THE PLAINTEXT FILE DATA, TO THE MEMORY
        with open(FILE_PATH, 'rb') as INFILE:
            #VALIDATE THE FILE IS NOT ALREADY AES-128 ENCRYPTED OR EMPTY
            CHECK_HEADERS_RESULT = check_aes_128_encryption_headers(INFILE)
            if CHECK_HEADERS_RESULT[0]:
                return [False, f'ALREADY_AES_128_ENCRYPTED:\n{FILE_PATH}']
            elif CHECK_HEADERS_RESULT[1] == 'FILE_EMPTY':
                return [False, f'FILE_EMPTY:\n{FILE_PATH}']
            #RESET THE FILE POINTER, AFTER THE AES-128 HEADER CHECK
            INFILE.seek(0)
            #OPEN THE ".tmp" OUTPUT FILE
            with open(FILE_PATH + '.tmp', 'wb') as OUTFILE:
                #WRITE 4 BYTES OF DATA, CONTAINING THE SIZE, IN BYTES, 
                #BEFORE EACH AES-128 ENCRYPTION HEADER, PLUS THE AES-128 ENCRYPTION HEADER
                START_HEADERS = b'START_AES_128_ENCRYPTION_HEADERS'
                END_HEADERS = b'END_AES_128_ENCRYPTION_HEADERS'
                OUTFILE.write(pack('>I', len(START_HEADERS)) + START_HEADERS)
                OUTFILE.write(pack('>I', len(SALT_BYTES)) + SALT_BYTES)
                OUTFILE.write(pack('>I', len(END_HEADERS)) + END_HEADERS)
                #STREAM AND ENCRYPT THE PLAINTEXT DATA, IN CHUNKS, TO ALLOW ENCRYPTION OF ALL FILE TYPES
                while True:
                    DATA_CHUNK = INFILE.read(BLOCK_SIZE)
                    if not DATA_CHUNK:
                        break
                    ENCRYPTED_CHUNK = CIPHER.encrypt(DATA_CHUNK)
                    #DELETE THE DATA CHUNK, FROM THE MEMORY, AFTER ENCRYPTION, OF EACH CHUNK
                    del DATA_CHUNK
                    OUTFILE.write(pack('>I', len(ENCRYPTED_CHUNK)) + ENCRYPTED_CHUNK)
        #OVERWRITE THE ORIGINAL FILE'S PLAINTEXT CONTENTS WITH RANDOM BYTES,
        #BEFORE DELETION, TO PREVENT RECOVERY, FROM THE DRIVE
        with open(FILE_PATH, 'r+b') as RANDOM_BYTES_OVERWRITE_FILE:
            while True:
                CHUNK = RANDOM_BYTES_OVERWRITE_FILE.read(BLOCK_SIZE)
                if not CHUNK:
                    break
                RANDOM_BYTES_OVERWRITE_FILE.seek(-len(CHUNK), 1)
                RANDOM_BYTES_OVERWRITE_FILE.write(urandom(len(CHUNK)))
            RANDOM_BYTES_OVERWRITE_FILE.flush()
            fsync(RANDOM_BYTES_OVERWRITE_FILE.fileno())
        #DELETE THE ORIGINAL FILE AND RENAME THE ".tmp" FILE, TO THE ORIGINAL FILE NAME
        replace(FILE_PATH + '.tmp', FILE_PATH)
        return [True, f'AES_128_FILE_ENCRYPTION_SUCCESSFULL:\n{FILE_PATH}']
    except Exception:
        try:
            remove(FILE_PATH + '.tmp')
            return [False, f'AES_128_FILE_ENCRYPTION_FAILED:\n{FILE_PATH}']
        except:
            return [False, f'AES_128_FILE_ENCRYPTION_FAILED:\n{FILE_PATH}']

#THIS FUNCTION:
#1.) REQUIRES FILE PATH AND PASSWORD STRINGS
#2.) ACCEPTS AN OPTIONAL BLOCK SIZE INTEGER
#3.) AES-128 DECRYPTS THE FILE, SECURELY, IN THE SUPPLIED FILE PATH (IF THE SUPPLIED PASSWORD, IS CORRECT)
def aes_128_decrypt_file(FILE_PATH, PASSWORD, BLOCK_SIZE=None):
    if not isinstance(FILE_PATH, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_decrypt_file()"\nThe supplied file path parameter, was not a string type.')
    elif not isfile(FILE_PATH):
        raise FileNotFoundError('[FileNotFoundError]\nFunction: "aes_128_decrypt_file()"\nThe supplied file path parameter, was not a path to an existing file.')
    elif not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_decrypt_file()"\nThe supplied password parameter, was not a string type.')
    elif PASSWORD.strip() == '':
        raise ValueError('[ValueError]\nFunction: "aes_128_decrypt_file()"\nThe supplied password parameter, was empty.')
    try:
        BLOCK_SIZE = 65536 if BLOCK_SIZE is None else BLOCK_SIZE
        #STREAM THE ENCRYPTED DATA, TO A ".tmp" FILE, WHILE DECRYPTING THE DATA BETWEEN THE 2 FILES,
        #TO PREVENT LOADING ANY OF THE ENCRYPTED FILE DATA, TO THE MEMORY
        with open(FILE_PATH, 'rb') as INFILE:
            #VALIDATE THE FILE, IS AES-128 ENCRYPTED, NOT EMPTY, AND THE HEADERS ARE NOT CORRUPTED
            CHECK_HEADERS_RESULT = check_aes_128_encryption_headers(INFILE)
            if CHECK_HEADERS_RESULT[1] == 'NOT_AES_128_ENCRYPTED':
                return [False, f'NOT_AES_128_ENCRYPTED:\n{FILE_PATH}']
            elif CHECK_HEADERS_RESULT[1] == 'FILE_EMPTY':
                return [False, f'FILE_EMPTY:\n{FILE_PATH}']
            elif CHECK_HEADERS_RESULT[1] == 'HEADERS_CORRUPTED':
                return [False, f'HEADERS_CORRUPTED:\n{FILE_PATH}']
            HEADERS, TOTAL_HEADERS_SIZE = CHECK_HEADERS_RESULT
            #EXTRACT THE SALT BYTES, FROM THE SECOND AES-128 ENCRYPTION HEADER
            SALT_BYTES = HEADERS[1]
            #DERIVE A HASH (AS A DECRYPTION KEY), THAT MATCHES THE ORIGINAL HASH (USED AS AN ENCRYPTION KEY), 
            #USING THE SALT BYTES STORED, IN THE AES-128 ENCRYPTION HEADERS,
            #AND THE USER-ENTERED PASSWORD, TO DECRYPT THE ENCRYPTED FILE CHUNKS
            HASH_BYTES = get_hash_and_salt(PASSWORD, SALT_BYTES)[0]
            #START AT THE FIRST ENCRYPTED FILE CHUNK, AFTER THE AES-128 ENCRYPTION HEADERS
            INFILE.seek(TOTAL_HEADERS_SIZE)
            with open(FILE_PATH + '.tmp', 'wb') as OUTFILE:
                while True:
                    SIZE_DATA = INFILE.read(4)
                    if not SIZE_DATA or len(SIZE_DATA) < 4:
                        break
                    (CHUNK_SIZE,) = unpack('>I', SIZE_DATA)
                    if CHUNK_SIZE <= 0:
                        remove(FILE_PATH + '.tmp')
                        return [False, f'AES_128_ENCRYPTED_DATA_CORRUPTED:\n{FILE_PATH}']
                    ENCRYPTED_CHUNK = INFILE.read(CHUNK_SIZE)
                    if len(ENCRYPTED_CHUNK) != CHUNK_SIZE:
                        remove(FILE_PATH + '.tmp')
                        return [False, f'AES_128_ENCRYPTED_DATA_CORRUPTED:\n{FILE_PATH}']
                    #USE THE HASH, AS A KEY, TO CREATE A CIPHER FOR DECRYPTION
                    CIPHER = Fernet(urlsafe_b64encode(HASH_BYTES))
                    PLAINTEXT_CHUNK = CIPHER.decrypt(ENCRYPTED_CHUNK)
                    OUTFILE.write(PLAINTEXT_CHUNK)
        #OVERWRITE THE ORIGINAL FILE'S ENCRYPTED CONTENTS WITH RANDOM BYTES,
        #BEFORE DELETION, TO PREVENT RECOVERY, OF THE ENCRYPTED DATA, FROM THE DRIVE
        with open(FILE_PATH, 'r+b') as RANDOM_BYTES_OVERWRITE_FILE:
            while True:
                CHUNK = RANDOM_BYTES_OVERWRITE_FILE.read(BLOCK_SIZE)
                if not CHUNK:
                    break
                RANDOM_BYTES_OVERWRITE_FILE.seek(-len(CHUNK), 1)
                RANDOM_BYTES_OVERWRITE_FILE.write(urandom(len(CHUNK)))
            RANDOM_BYTES_OVERWRITE_FILE.flush()
            fsync(RANDOM_BYTES_OVERWRITE_FILE.fileno())
        #DELETE THE ORIGINAL FILE AND RENAME THE ".tmp" FILE, TO THE ORIGINAL FILE NAME
        replace(FILE_PATH + '.tmp', FILE_PATH)
        return [True, f'AES_128_FILE_DECRYPTION_SUCCESS:\n{FILE_PATH}']
    except InvalidToken:
        try:
            remove(FILE_PATH + '.tmp')
            return [False, f'INCORRECT_PASSWORD:\n{FILE_PATH}']
        except:
            return [False, f'INCORRECT_PASSWORD:\n{FILE_PATH}']
    except Exception:
        try:
            remove(FILE_PATH + '.tmp')
            return [False, f'AES_128_FILE_DECRYPTION_FAILED:\n{FILE_PATH}']
        except:
            return [False, f'AES_128_FILE_DECRYPTION_FAILED:\n{FILE_PATH}']