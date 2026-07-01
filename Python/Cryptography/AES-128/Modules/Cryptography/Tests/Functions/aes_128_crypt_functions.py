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
            return [None, 'AES_128_ENCRYPTION_HEADERS_CORRUPTED']
        (HEADER_SIZE,) = unpack('>I', SIZE_DATA)
        if HEADER_NUMBER == 1 and HEADER_SIZE > 1024:
            FILE.seek(0)
            return [None, 'NOT_AES_128_ENCRYPTED']
        HEADER_DATA = FILE.read(HEADER_SIZE)
        if len(HEADER_DATA) != HEADER_SIZE:
            FILE.seek(0)
            return [None, 'AES_128_ENCRYPTION_HEADERS_CORRUPTED']
        elif HEADER_NUMBER == 2:
            HEADER = HEADER_DATA
            if len(HEADER) != 16:
                FILE.seek(0)
                return [None, 'AES_128_ENCRYPTION_HEADERS_CORRUPTED']
        else:
            try:
                HEADER = HEADER_DATA.decode('utf-8', 'strict')
            except UnicodeDecodeError:
                FILE.seek(0)
                return [None, 'NOT_AES_128_ENCRYPTED']
        if HEADER_NUMBER == 1 and HEADER != 'START_AES_128_ENCRYPTION_HEADERS':
            FILE.seek(0)
            return [None, 'AES_128_ENCRYPTION_HEADERS_CORRUPTED']
        elif HEADER_NUMBER == 3 and HEADER != 'END_AES_128_ENCRYPTION_HEADERS':
            FILE.seek(0)
            return [None, 'AES_128_ENCRYPTION_HEADERS_CORRUPTED']
        TOTAL_SIZE += 4 + HEADER_SIZE
        HEADERS.append(HEADER)
        if HEADER_NUMBER == 3:
            FILE.seek(0)
            break
        HEADER_NUMBER += 1
    return [HEADERS, TOTAL_SIZE]

#THIS FUNCTION:
#1.) REQUIRES FOLDER PATH AND PASSWORD STRINGS
#2.) RECURSIVELY AES-128 ENCRYPTS ALL FILES, WITHIN THE SUPPLIED FOLDER PATH
def aes_128_encrypt_folder(FOLDER_PATH, PASSWORD):
    if not isinstance(FOLDER_PATH, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_encrypt_folder()"\nThe supplied folder path parameter, was not a string type.')
    elif not isdir(FOLDER_PATH):
        raise NotADirectoryError('[NotADirectoryError]\nFunction: "aes_128_encrypt_folder()"\nThe supplied folder path parameter, was not a path to an existing folder.')
    elif not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_encrypt_folder()"\nThe supplied password parameter, was not a string type.')
    elif PASSWORD.strip() == '':
        raise ValueError('[ValueError]\nFunction: "aes_128_encrypt_folder()"\nThe supplied password parameter, was empty.')
    ALREADY_ENCRYPTED_DETECTED = False
    for ROOT, DIRECTORIES, FILES in walk(FOLDER_PATH):
        FILES = [FILE for FILE in FILES if not FILE.startswith('.') and not FILE.endswith('ini') and not islink(join(ROOT, FILE))]
        ERRORS = []
        for FILE_NAME in FILES:
            FILE_PATH = join(ROOT, FILE_NAME)
            RESULT = aes_128_encrypt_file(FILE_PATH, PASSWORD)
            if RESULT[1] == 'FILE_EMPTY':
                ERRORS.append('FILE_EMPTY')
                continue
            elif RESULT[1] == 'ALREADY_AES_128_ENCRYPTED':
                ERRORS.append('ALREADY_AES_128_ENCRYPTED')
                continue
    if ERRORS:
        return [False, ERRORS]
    return [True, 'AES_128_FOLDER_ENCRYPTION_SUCCESS']

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
    INCORRECT_PASSWORD_DETECTED = False
    for ROOT, DIRECTORIES, FILES in walk(FOLDER_PATH):
        FILES = [FILE for FILE in FILES if not FILE.startswith('.') and not FILE.endswith('ini') and not islink(join(ROOT, FILE))]
        ERRORS = []
        for FILE_NAME in FILES:
            FILE_PATH = join(ROOT, FILE_NAME)
            RESULT = aes_128_decrypt_file(FILE_PATH, PASSWORD)
            if RESULT[1] == 'FILE_EMPTY':
                ERRORS.append('FILE_EMPTY')
                continue
            elif RESULT[1] == 'NOT_AES_128_ENCRYPTED':
                ERRORS.append('NOT_AES_128_ENCRYPTED')
                continue
            elif RESULT[1] == 'AES_128_ENCRYPTION_HEADERS_CORRUPTED':
                ERRORS.append('AES_128_ENCRYPTION_HEADERS_CORRUPTED')
                continue
            elif RESULT[1] == 'AES_128_ENCRYPTED_DATA_CORRUPTED':
                ERRORS.append('AES_128_ENCRYPTED_DATA_CORRUPTED')
                continue
            elif RESULT[1] == 'INCORRECT_AES_128_FILE_DECRYPTION_PASSWORD':
                ERRORS.append('INCORRECT_AES_128_FILE_DECRYPTION_PASSWORD')
                continue
    if ERRORS:
        return [False, ERRORS]
    return [True, 'AES_128_FOLDER_DECRYPTION_SUCCESS']

#THIS FUNCTION:
#1.) REQUIRES FILE PATH AND PASSWORD STRINGS
#2.) ACCEPTS AN OPTIONAL BLOCK SIZE INTEGER
#3.) AES-128 ENCRYPTS THE FILE, IN THE SUPPLIED FILE PATH
def aes_128_encrypt_file(FILE_PATH, PASSWORD, BLOCK_SIZE=None):
    if not isinstance(FILE_PATH, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_encrypt_file()"\nThe supplied file path parameter, was not a string type.')
    elif not isfile(FILE_PATH):
        raise FileNotFoundError('[FileNotFoundError]\nFunction: "aes_128_encrypt_file()"\nThe supplied file path parameter, was not a path to an existing file.')
    elif not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_encrypt_file()"\nThe supplied password parameter, was not a string type.')
    elif PASSWORD.strip() == '':
        raise ValueError('[ValueError]\nFunction: "aes_128_encrypt_file()"\nThe supplied password parameter, was empty.')
    #CREATE A SALT, USING THE "get_hash_and_salt()" FUNCTION
    #AND THE USER-ENTERED PASSWORD, THEN WRITE IT TO THE AES-128 ENCRYPTED
    #FILE HEADERS, FOR LATER CREATION OF A MATCHING HASH, WHEN IN COMBINATION,
    #WITH THE USER-ENTERED PASSWORD
    HASH_BYTES, SALT_BYTES = get_hash_and_salt(PASSWORD)
    BLOCK_SIZE = 65536 if BLOCK_SIZE is None else BLOCK_SIZE
    #USE THE HASH, TO CREATE A CIPHER FOR ENCRYPTION
    CIPHER = Fernet(urlsafe_b64encode(HASH_BYTES))
    #STREAM THE PLAINTEXT DATA, TO A ".tmp" FILE, WHILE ENCRYPTING
    #THE DATA BETWEEN, TO PREVENT LOADING ANY OF THE PLAINTEXT FILE DATA, TO THE MEMORY
    INFILE = open(FILE_PATH, 'rb')
    OUTFILE = open(FILE_PATH + '.tmp', 'wb')
    try:
        #VALIDATE THE FILE, IS NOT EMPTY OR ALREADY AES-128 ENCRYPTED
        CHECK_HEADERS_RESULT = check_aes_128_encryption_headers(INFILE)
        if CHECK_HEADERS_RESULT[1] == 'FILE_EMPTY':
            OUTFILE.close()
            INFILE.close()
            remove(FILE_PATH + '.tmp')
            return [False, 'FILE_EMPTY']
        elif CHECK_HEADERS_RESULT[0]:
            OUTFILE.close()
            INFILE.close()
            remove(FILE_PATH + '.tmp')
            return [False, 'ALREADY_AES_128_ENCRYPTED']
        elif CHECK_HEADERS_RESULT[1] == 'AES_128_ENCRYPTION_HEADERS_CORRUPTED':
            OUTFILE.close()
            INFILE.close()
            remove(FILE_PATH + '.tmp')
            return [False, 'AES_128_ENCRYPTION_HEADERS_CORRUPTED']
        #WRITE 4 BYTES OF DATA, CONTAINING THE SIZE, IN BYTES, BEFORE EACH AES-128 ENCRYPTION HEADER, 
        #PLUS THE AES-128 ENCRYPTION HEADER
        START = b'START_AES_128_ENCRYPTION_HEADERS'
        END = b'END_AES_128_ENCRYPTION_HEADERS'
        OUTFILE.write(pack('>I', len(START)) + START)
        OUTFILE.write(pack('>I', len(SALT_BYTES)) + SALT_BYTES)
        OUTFILE.write(pack('>I', len(END)) + END)
        #STREAM AND ENCRYPT THE PLAINTEXT DATA, IN CHUNKS, 
        #TO ALLOW ENCRYPTION OF ALL FILE TYPES
        while True:
            DATA_CHUNK = INFILE.read(BLOCK_SIZE)
            if not DATA_CHUNK:
                break
            ENCRYPTED_CHUNK = CIPHER.encrypt(DATA_CHUNK)
            OUTFILE.write(pack('>I', len(ENCRYPTED_CHUNK)) + ENCRYPTED_CHUNK)
        OUTFILE.close()
        INFILE.close()
        #OVERWRITE THE ORIGINAL FILE'S PLAINTEXT CONTENTS WITH RANDOM BYTES,
        #BEFORE DELETION, TO PREVENT RECOVERY, FROM THE DRIVE
        with open(FILE_PATH, 'r+b') as WIPEFILE:
            while True:
                CHUNK = WIPEFILE.read(BLOCK_SIZE)
                if not CHUNK:
                    break
                WIPEFILE.seek(-len(CHUNK), 1)
                WIPEFILE.write(urandom(len(CHUNK)))
            WIPEFILE.flush()
            fsync(WIPEFILE.fileno())
        #DELETE THE ORIGINAL FILE AND RENAME THE ".tmp" FILE, TO THE ORIGINAL FILE NAME
        replace(FILE_PATH + '.tmp', FILE_PATH)
        return [True, 'AES_128_FILE_ENCRYPTION_SUCCESS']
    except Exception as ERROR:
        OUTFILE.close()
        INFILE.close()
        remove(FILE_PATH + '.tmp')
        return [False, f'AES_128_ENCRYPTION_FAILED: {str(ERROR)}']

#THIS FUNCTION:
#1.) REQUIRES FILE PATH AND PASSWORD STRINGS
#2.) ACCEPTS AN OPTIONAL BLOCK SIZE INTEGER
#3.) AES-128 DECRYPTS THE FILE, IN THE SUPPLIED FILE PATH, IF THE SUPPLIED PASSWORD, IS CORRECT
def aes_128_decrypt_file(FILE_PATH, PASSWORD, BLOCK_SIZE=None):
    if not isinstance(FILE_PATH, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_decrypt_file()"\nThe supplied file path parameter, was not a string type.')
    elif not isfile(FILE_PATH):
        raise FileNotFoundError('[FileNotFoundError]\nFunction: "aes_128_decrypt_file()"\nThe supplied file path parameter, was not a path to an existing file.')
    elif not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "aes_128_decrypt_file()"\nThe supplied password parameter, was not a string type.')
    elif PASSWORD.strip() == '':
        raise ValueError('[ValueError]\nFunction: "aes_128_decrypt_file()"\nThe supplied password parameter, was empty.')
    BLOCK_SIZE = 65536 if BLOCK_SIZE is None else BLOCK_SIZE
    #STREAM THE ENCRYPTED DATA, TO A ".tmp" FILE, WHILE DECRYPTING
    #THE DATA BETWEEN, TO PREVENT LOADING ANY OF THE ENCRYPTED FILE DATA, TO THE MEMORY
    INFILE = open(FILE_PATH, 'rb')
    OUTFILE = open(FILE_PATH + '.tmp', 'wb')
    try:
        #VALIDATE THE FILE, IS NOT EMPTY AND IS AES-128 ENCRYPTED
        CHECK_HEADERS_RESULT = check_aes_128_encryption_headers(INFILE)
        if CHECK_HEADERS_RESULT[1] == 'FILE_EMPTY':
            OUTFILE.close()
            INFILE.close()
            remove(FILE_PATH + '.tmp')
            return [False, 'FILE_EMPTY']
        elif not CHECK_HEADERS_RESULT[0]:
            OUTFILE.close()
            INFILE.close()
            remove(FILE_PATH + '.tmp')
            return [False, CHECK_HEADERS_RESULT[1]]
        HEADERS, HEADER_TOTAL_SIZE = CHECK_HEADERS_RESULT
        #START AT THE FIRST ENCRYPTED FILE CHUNK,
        #AFTER THE AES-128 ENCRYPTION HEADERS
        INFILE.seek(HEADER_TOTAL_SIZE)
        SIZE_TEST = INFILE.read(4)
        if not SIZE_TEST:
            OUTFILE.close()
            INFILE.close()
            remove(FILE_PATH + '.tmp')
            return [False, 'FILE_EMPTY']
        INFILE.seek(HEADER_TOTAL_SIZE)
        while True:
            SIZE_DATA = INFILE.read(4)
            if not SIZE_DATA or len(SIZE_DATA) < 4:
                break
            (CHUNK_SIZE,) = unpack('>I', SIZE_DATA)
            ENCRYPTED_CHUNK = INFILE.read(CHUNK_SIZE)
            if len(ENCRYPTED_CHUNK) != CHUNK_SIZE:
                OUTFILE.close()
                INFILE.close()
                remove(FILE_PATH + '.tmp')
                return [False, 'AES_128_ENCRYPTED_DATA_CORRUPTED']
            #EXTRACT THE SALT BYTES, FROM THE SECOND AES-128 ENCRYPTION HEADER
            SALT_BYTES = HEADERS[1]
            #DERIVE A MATCHING HASH, TO THE ORIGINAL HASH, FROM THE USER-ENTERED PASSWORD AND THE SALT BYTES, 
            #THAT ARE STORED, IN THE SECOND AES-128 ENCRYPTED FILE HEADER
            HASH_BYTES = get_hash_and_salt(PASSWORD, SALT_BYTES)[0]
            try:
                 #USE THE HASH, TO CREATE A CIPHER FOR DECRYPTION
                 CIPHER = Fernet(urlsafe_b64encode(HASH_BYTES))
                 PLAINTEXT_CHUNK = CIPHER.decrypt(ENCRYPTED_CHUNK)
            except InvalidToken:
                OUTFILE.close()
                INFILE.close()
                remove(FILE_PATH + '.tmp')
                return [False, 'INCORRECT_AES_128_FILE_DECRYPTION_PASSWORD']
            OUTFILE.write(PLAINTEXT_CHUNK)
        OUTFILE.close()
        INFILE.close()
        #OVERWRITE THE ORIGINAL FILE'S ENCRYPTED CONTENTS WITH RANDOM BYTES,
        #BEFORE DELETION, PREVENTING RECOVERY, FROM THE DRIVE
        try:
            with open(FILE_PATH, 'r+b') as WIPEFILE:
                while True:
                    CHUNK = WIPEFILE.read(BLOCK_SIZE)
                    if not CHUNK:
                        break
                    WIPEFILE.seek(-len(CHUNK), 1)
                    WIPEFILE.write(urandom(len(CHUNK)))
                WIPEFILE.flush()
                fsync(WIPEFILE.fileno())
        except Exception:
            remove(FILE_PATH + '.tmp')
            return [False, 'AES_128_ENCRYPTED_FILE_WIPE_FAILED']
        #DELETE THE ORIGINAL FILE AND RENAME THE ".tmp" FILE, TO THE ORIGINAL FILE NAME
        replace(FILE_PATH + '.tmp', FILE_PATH)
        return [True, 'AES_128_FILE_DECRYPTION_SUCCESS']
    except Exception as ERROR:
        OUTFILE.close()
        INFILE.close()
        remove(FILE_PATH + '.tmp')
        return [False, f'AES_128_DECRYPTION_FAILED: {str(ERROR)}']