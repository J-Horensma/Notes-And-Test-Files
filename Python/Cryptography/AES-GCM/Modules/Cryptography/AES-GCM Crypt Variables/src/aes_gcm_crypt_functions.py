from io import IOBase
from os import walk, access, R_OK, W_OK, X_OK, replace, remove, fsync
from os.path import join, exists, isdir, isfile, islink
from struct import pack, unpack
from base64 import urlsafe_b64encode
from secrets import token_bytes
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.exceptions import InvalidTag

#THIS FUNCTION:
#1.) REQUIRES A KEY SIZE INTEGER AND A PASSWORD STRING
#2.) ACCEPTS AN OPTIONAL SALT BYTES
#3.) IF A 16 BYTE SALT, IS NOT SUPPLIED, ONE IS GENERATED
#4.) A VARYING BYTE-LENGTH PASSWORD HASH IS GENERATED, AS A KEY, FOR AES CRYPTOGRAPHY
#5.) RETURNS THE KEY AND SALT BYTES, AS A LIST
def get_aes_key_and_salt(KEY_SIZE, PASSWORD, SALT_BYTES=None):
    if not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "get_aes_key_and_salt()"\nThe password parameter, must be a string type.')
    elif not PASSWORD.strip():
        raise ValueError('[ValueError]\nFunction: "get_aes_key_and_salt()"\nThe password parameter, cannot be empty.')
    elif not isinstance(KEY_SIZE, int):
        raise TypeError('[TypeError]\nFunction: "get_aes_key_and_salt()"\nThe key size parameter, must be an integer type.')
    elif KEY_SIZE not in [128, 192, 256]:
        raise ValueError('[ValueError]\nFunction: "get_aes_key_and_salt()"\nThe key size parameter, must be an integer, of 128, 192, or 256.')
    elif SALT_BYTES is not None and not isinstance(SALT_BYTES, bytes):
        raise TypeError('[TypeError]\nFunction: "get_aes_key_and_salt()"\nThe salt bytes parameter, must be a bytes type.')
    elif SALT_BYTES is not None and len(SALT_BYTES) != 16:
        raise ValueError('[ValueError]\nFunction: "get_aes_key_and_salt()"\nThe salt bytes parameter, must be 16 bytes long.')
    else:
        try:
            SALT_BYTES = token_bytes(16) if SALT_BYTES is None else SALT_BYTES
            #CREATE A KEY (1 BYTE = 8 BITS):
            #16 BYTES = 128 BIT, KEY LENGTH (AES-128)
            #24 BYTES = 192 BIT, KEY LENGTH (AES-192)
            #32 BYTES = 256 BIT, KEY LENGTH (AES-256)
            KEY_BYTES_LENGTH = KEY_SIZE // 8
            KEY_DERIVATION_FUNCTION = PBKDF2HMAC(
                algorithm=SHA256(),
                length=KEY_BYTES_LENGTH,
                salt=SALT_BYTES,
                iterations=200_000
            )
            KEY_BYTES = KEY_DERIVATION_FUNCTION.derive(PASSWORD.encode())
            return [KEY_BYTES, SALT_BYTES]
        except Exception as ERROR:
            raise Exception(f'[Exception]\nFunction: "get_aes_key_and_salt()"\n{ERROR}')

#THIS FUNCTION:
#1.) REQUIRES A FILE OBJECT, OPENED IN READ BYTES MODE AND A KEY SIZE INTEGER
#2.) CHECKS FOR AES-GCM HEADERS, IN THE FILE, AND RETURNS THE HEADERS, AS A LIST, OR "None" WITH ERROR INFORMATION
def check_aes_gcm_headers(FILE):
    if not isinstance(FILE, IOBase) or 'r' not in FILE.mode or 'b' not in FILE.mode:
        raise TypeError('[TypeError]\nFunction: "check_aes_gcm_headers()"\nThe file parameter, must be a file object, in read bytes mode.')
    else:
        try:
            TOTAL_HEADERS_SIZE = 0
            #READ THE HEADER SIZE DATA (FIRST 4 BYTES OF EVERY AES-GCM ENCRYPTION HEADER, ENCODED INTO BIG ENDIAN BINARY BYTES)
            ALGORITHM_AND_MODE_HEADER_SIZE_DATA = FILE.read(4)
            #CHECK IF THE FILE, IS EMPTY, BY CHECKING FOR THE FIRST AES-GCM ENCRYPTION HEADER'S SIZE DATA
            if len(ALGORITHM_AND_MODE_HEADER_SIZE_DATA) == 0:
                FILE.seek(0); return [None, 'FILE_EMPTY']
            #THE "aes_gcm_encrypt_file()" FUNCTION, SHOULD WRITE HEADERS TO AES-GCM ENCRYPTED FILES, IN THE FORMAT: 
            #4 BYTES (CONTAINING BIG ENDIAN BINARY ENCODED HEADER SIZE DATA) + HEADER BYTES
            #LESS THAN 4 BYTES, MEANS THE HEADER SIZE DATA, IS TRUNCATED 
            if len(ALGORITHM_AND_MODE_HEADER_SIZE_DATA) != 4:
                FILE.seek(0); return [None, 'ALGORITHM_AND_MODE_HEADER_SIZE_TRUNCATED']
            #CONVERT THE HEADER SIZE DATA, FROM BIG ENDIAN BINARY ENCODED, TO AN INTEGER, REPRESENTING THE BYTES LENGTH OF THE HEADER
            (ALGORITHM_AND_MODE_HEADER_SIZE,) = unpack('>I', ALGORITHM_AND_MODE_HEADER_SIZE_DATA)
            #READ THE LENGTH OF THE HEADER
            ALGORITHM_AND_MODE_HEADER = FILE.read(ALGORITHM_AND_MODE_HEADER_SIZE)
            #CHECK IF THE FILE, IS AES-GCM ENCRYPTED
            if ALGORITHM_AND_MODE_HEADER != b'AES-GCM':
                FILE.seek(0); return [None, 'NOT_AES-GCM_ENCRYPTED']
            #CHECK IF THE HEADER, IS CORRUPTED
            elif ALGORITHM_AND_MODE_HEADER_SIZE != len(ALGORITHM_AND_MODE_HEADER):
                FILE.seek(0); return [None, 'ALGORITHM_AND_MODE_HEADER_CORRUPTED']
            #UPDATE THE TOTAL HEADERS SIZE VARIABLE, REPRESENTING THE TOTAL BYTES LENGTH, OF ALL THE AES-GCM ENCRYPTION HEADERS
            TOTAL_HEADERS_SIZE += 4 + ALGORITHM_AND_MODE_HEADER_SIZE
            KEY_SIZE_HEADER_SIZE_DATA = FILE.read(4)
            if len(KEY_SIZE_HEADER_SIZE_DATA) != 4:
                FILE.seek(0); return [None, 'KEY_SIZE_HEADER_SIZE_TRUNCATED']
            (KEY_SIZE_HEADER_SIZE,) = unpack('>I', KEY_SIZE_HEADER_SIZE_DATA)
            KEY_SIZE_HEADER = FILE.read(KEY_SIZE_HEADER_SIZE)
            TOTAL_HEADERS_SIZE += 4 + KEY_SIZE_HEADER_SIZE
            NONCE_BYTES_HEADER_SIZE_DATA = FILE.read(4)
            if len(NONCE_BYTES_HEADER_SIZE_DATA) != 4:
                FILE.seek(0); return [None, 'NONCE_BYTES_HEADER_SIZE_TRUNCATED']
            (NONCE_BYTES_HEADER_SIZE,) = unpack('>I', NONCE_BYTES_HEADER_SIZE_DATA)
            NONCE_BYTES_HEADER = FILE.read(NONCE_BYTES_HEADER_SIZE)
            if NONCE_BYTES_HEADER_SIZE != len(NONCE_BYTES_HEADER) or len(NONCE_BYTES_HEADER) != 12:
                FILE.seek(0); return [None, 'NONCE_BYTES_HEADER_CORRUPTED']
            TOTAL_HEADERS_SIZE += 4 + NONCE_BYTES_HEADER_SIZE
            TAG_BYTES_HEADER_SIZE_DATA = FILE.read(4)
            if len(TAG_BYTES_HEADER_SIZE_DATA) != 4:
                FILE.seek(0); return [None, 'TAG_BYTES_HEADER_SIZE_TRUNCATED']
            (TAG_BYTES_HEADER_SIZE,) = unpack('>I', TAG_BYTES_HEADER_SIZE_DATA)
            TAG_BYTES_HEADER = FILE.read(TAG_BYTES_HEADER_SIZE)
            if TAG_BYTES_HEADER_SIZE != len(TAG_BYTES_HEADER) or len(TAG_BYTES_HEADER) != 16:
                FILE.seek(0); return [None, 'TAG_BYTES_HEADER_CORRUPTED']
            TOTAL_HEADERS_SIZE += 4 + TAG_BYTES_HEADER_SIZE
            SALT_BYTES_HEADER_SIZE_DATA = FILE.read(4)
            if len(SALT_BYTES_HEADER_SIZE_DATA) != 4:
                FILE.seek(0); return [None, 'SALT_BYTES_HEADER_SIZE_TRUNCATED']
            (SALT_BYTES_HEADER_SIZE,) = unpack('>I', SALT_BYTES_HEADER_SIZE_DATA)
            SALT_BYTES_HEADER = FILE.read(SALT_BYTES_HEADER_SIZE)
            if SALT_BYTES_HEADER_SIZE != len(SALT_BYTES_HEADER) or len(SALT_BYTES_HEADER) != 16:
                FILE.seek(0); return [None, 'SALT_BYTES_HEADER_CORRUPTED']
            TOTAL_HEADERS_SIZE += 4 + SALT_BYTES_HEADER_SIZE
            if TOTAL_HEADERS_SIZE != 74:
                FILE.seek(0); return [None, 'UNEXPECTED_TOTAL_HEADERS_SIZE']
            FILE.seek(0); return [ALGORITHM_AND_MODE_HEADER.decode(), int(KEY_SIZE_HEADER.decode()), NONCE_BYTES_HEADER, TAG_BYTES_HEADER, SALT_BYTES_HEADER, TOTAL_HEADERS_SIZE]
        except Exception as ERROR:
            raise Exception(f'[Exception]\nFunction: "check_aes_gcm_headers()"\n{ERROR}')
        
#THIS FUNCTION:
#1.) REQUIRES A FOLDER PATH STRING, KEY SIZE INTEGER, AND PASSWORD STRING
#2.) RECURSIVELY AES-GCM ENCRYPTS ALL FILES, WITHIN THE SUPPLIED FOLDER PATH (SECURELY, FOR ANY FILE TYPE)
def aes_gcm_encrypt_folder(FOLDER_PATH, KEY_SIZE, PASSWORD):
    KEY_SIZE_LIST = [128, 192, 256]
    if not isinstance(FOLDER_PATH, str):
        raise TypeError('[TypeError]\nFunction: "aes_gcm_encrypt_folder()"\nThe folder path parameter, must be a string type.')
    elif not isdir(FOLDER_PATH):
        raise NotADirectoryError('[NotADirectoryError]\nFunction: "aes_gcm_encrypt_folder()"\nThe folder path parameter, must be a path to an existing folder.')
    elif KEY_SIZE not in KEY_SIZE_LIST:
        raise ValueError('[ValueError]\nFunction: "aes_gcm_encrypt_folder()"\nThe key size parameter, must be an integer, of 128, 192, or 256.')
    elif not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "aes_gcm_encrypt_folder()"\nThe password parameter, must be a string type.')
    elif not PASSWORD.strip():
        raise ValueError('[ValueError]\nFunction: "aes_gcm_encrypt_folder()"\nThe password parameter, cannot be empty.')
    try:
        for ROOT, DIRECTORIES, FILES in walk(FOLDER_PATH):
            FILES = [FILE for FILE in FILES if not FILE.startswith('.') and not FILE.endswith('ini') and not islink(join(ROOT, FILE))]
            ERRORS = []
            for FILE_NAME in FILES:
                FILE_PATH = join(ROOT, FILE_NAME)
                RESULT = aes_gcm_encrypt_file(FILE_PATH, KEY_SIZE, PASSWORD)
                if not RESULT[0]:
                    ERRORS += RESULT[1].splitlines()
        if ERRORS:
            ERRORS = '\n'.join(ERRORS)
            return [False, ERRORS]
        return [True, f'AES-GCM_FOLDER_ENCRYPTION_SUCCESSFULL:\n{FOLDER_PATH}']
    except Exception as ERROR:
        raise Exception(f'[Exception]\nFunction: "aes_gcm_encrypt_folder()"\n{ERROR}\n{FOLDER_PATH}')

#THIS FUNCTION:
#1.) REQUIRES A FOLDER PATH STRING, KEY SIZE INTEGER, AND PASSWORD STRING
#2.) RECURSIVELY AES-GCM DECRYPTS ALL FILES, WITHIN THE SUPPLIED FOLDER PATH (IF THE SUPPLIED PASSWORD, IS CORRECT)
def aes_gcm_decrypt_folder(FOLDER_PATH, PASSWORD):
    if not isinstance(FOLDER_PATH, str):
        raise TypeError('[TypeError]\nFunction: "aes_gcm_decrypt_folder()"\nThe folder path parameter, must be a string type.')
    elif not isdir(FOLDER_PATH):
        raise NotADirectoryError('[NotADirectoryError]\nFunction: "aes_gcm_decrypt_folder()"\nThe folder path parameter, must be a path to an existing folder.')
    elif not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "aes_gcm_decrypt_folder()"\nThe password parameter, must be a string type.')
    elif not PASSWORD.strip():
        raise ValueError('[ValueError]\nFunction: "aes_gcm_decrypt_folder()"\nThe password parameter, cannot be empty.')
    try:
        for ROOT, DIRECTORIES, FILES in walk(FOLDER_PATH):
            FILES = [FILE for FILE in FILES if not FILE.startswith('.') and not FILE.endswith('ini') and not islink(join(ROOT, FILE))]
            ERRORS = []
            for FILE_NAME in FILES:
                FILE_PATH = join(ROOT, FILE_NAME)
                RESULT = aes_gcm_decrypt_file(FILE_PATH, PASSWORD)
                if not RESULT[0]:
                    ERRORS += RESULT[1].splitlines()
        if ERRORS:
            ERRORS = '\n'.join(ERRORS)
            return [False, ERRORS]
        return [True, f'AES-GCM_FOLDER_DECRYPTION_SUCCESSFULL:\n{FOLDER_PATH}']
    except Exception as ERROR:
        raise Exception(f'[Exception]\nFunction: "aes_gcm_decrypt_folder()"\n{ERROR}\n{FOLDER_PATH}')

#1.) REQUIRES A FILE PATH STRING, KEY SIZE INTEGER, AND PASSWORD STRING
#2.) ACCEPTS AN OPTIONAL BLOCK SIZE INTEGER
#3.) AES-GCM ENCRYPTS THE SUPPLIED FILE PATH, WITH THE SUPPLIED KEY SIZE (SECURELY, FOR ANY FILE TYPE)
def aes_gcm_encrypt_file(FILE_PATH, KEY_SIZE, PASSWORD, BLOCK_SIZE=None):
    KEY_SIZE_LIST = [128, 192, 256]
    if not isinstance(FILE_PATH, str):
        raise TypeError('[TypeError]\nFunction: "aes_gcm_encrypt_file()"\nThe file path parameter, must be a string type.')
    elif not isfile(FILE_PATH):
        raise FileNotFoundError('[FileNotFoundError]\nFunction: "aes_gcm_encrypt_file()"\nThe file path parameter, must be a path to an existing file.')
    elif KEY_SIZE not in KEY_SIZE_LIST:
        raise ValueError('[ValueError]\nFunction: "aes_gcm_encrypt_file()"\nThe key size parameter, must be an integer, of 128, 192, or 256.')
    elif not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "aes_gcm_encrypt_file()"\nThe password parameter, must be a string type.')
    elif not PASSWORD.strip():
        raise ValueError('[ValueError]\nFunction: "aes_gcm_encrypt_file()"\nThe password parameter, cannot be empty.')
    elif BLOCK_SIZE is not None and not isinstance(BLOCK_SIZE, int):
        raise TypeError('[TypeError]\nFunction: "aes_gcm_encrypt_file()"\nThe block size parameter, must be an integer type.')
    try:
        BLOCK_SIZE = 65536 if BLOCK_SIZE is None else BLOCK_SIZE
        #CREATE A 16-32 BYTE KEY (DEPENDENT ON THE KEY SIZE) AND A 16-BYTE SALT, 
        #USING THE "get_aes_key_and_salt()" FUNCTION, IN COMBINATION,
        #WITH THE KEY SIZE, AS AN INTEGER (128, 192, OR 256), AND THE USER-ENTERED PASSWORD STRING
        KEY_BYTES, SALT_BYTES = get_aes_key_and_salt(KEY_SIZE, PASSWORD)
        #CREATE A 12-BYTE NONCE
        NONCE_BYTES = token_bytes(12)
        #USE THE KEY AND NONCE BYTES, TO CREATE A CIPHER FOR THE AES-GCM ENCRYPTION
        CIPHER = Cipher(algorithms.AES(KEY_BYTES), modes.GCM(NONCE_BYTES))
        #START THE ENCRYPTION STREAMER
        ENCRYPTOR = CIPHER.encryptor()
        #CHECK IF FILE PERMISSION, IS AVAILABLE
        if exists(FILE_PATH) and not all([access(FILE_PATH, R_OK), access(FILE_PATH, W_OK), access(FILE_PATH, X_OK)]):
            return [False, f'FILE_PERMISSION_DENIED:\n{FILE_PATH}']
        with open(FILE_PATH, 'rb') as INFILE:
            #CHECK IF THE FILE, IS EMPTY OR ALREADY AES-GCM ENCRYPTED
            AES_GCM_HEADERS_CHECK = check_aes_gcm_headers(INFILE)
            if AES_GCM_HEADERS_CHECK[1] == 'FILE_EMPTY':
                return [False, f'FILE_EMPTY:\n{FILE_PATH}']
            elif AES_GCM_HEADERS_CHECK[0]:
                return [False, f'ALREADY_AES-GCM_ENCRYPTED:\n{FILE_PATH}']
            #CREATE AND OPEN A TEMPORARY FILE, TO WRITE TO
            with open(FILE_PATH + '.tmp', 'wb') as OUTFILE:
                RESERVED_HEADERS_LENGTH_LIST = [7, 3, 12, 16, 16]
                for RESERVED_HEADER_LENGTH in RESERVED_HEADERS_LENGTH_LIST:
                    #WRITE THE RESERVED SPACE FOR THE HEADER SIZE INTEGER (MAX INTEGER OF 4294967295, BINARY ENCODED INTO 4 BYTES) 
                    #AND THE HEADER BYTES, USING NULL-BYTES
                    OUTFILE.write(pack('>I', RESERVED_HEADER_LENGTH) + (b'\x00' * RESERVED_HEADER_LENGTH))
                #STREAM-ENCRYPT THE PLAINTEXT DATA, IN CHUNKS (TO ALLOW ENCRYPTION OF ALL FILE TYPES)
                while True:
                    PLAINTEXT_CHUNK = INFILE.read(BLOCK_SIZE)
                    if not PLAINTEXT_CHUNK:
                        break
                    ENCRYPTED_CHUNK = ENCRYPTOR.update(PLAINTEXT_CHUNK)
                    #DELETE EACH PLAINTEXT DATA CHUNK VARIABLE, AFTER ENCRYPTION, 
                    #TO PREVENT ANY PLAINTEXT DATA FROM BEING STORED, IN THE MEMORY
                    del PLAINTEXT_CHUNK
                    OUTFILE.write(pack('>I', len(ENCRYPTED_CHUNK)) + ENCRYPTED_CHUNK)
                    #DELETE EACH ENCRYPTED DATA CHUNK VARIABLE, AFTER WRITING TO THE TEMPORARY FILE, 
                    #TO PREVENT ANY ENCRYPTED DATA FROM BEING STORED, IN THE MEMORY
                    del ENCRYPTED_CHUNK
                #CLOSE THE ENCRYPTION STREAM
                ENCRYPTOR.finalize()
                TAG_BYTES = ENCRYPTOR.tag
                #RESET THE FILE POINTER AND OVERWRITE THE RESERVED HEADER SPACE,
                #WITH THE AES-GCM ENCRYPTION HEADERS
                OUTFILE.seek(0)
                HEADERS_LIST = ['AES-GCM', KEY_SIZE, NONCE_BYTES, TAG_BYTES, SALT_BYTES]
                for HEADER in HEADERS_LIST:
                    HEADER_BYTES = HEADER if isinstance(HEADER, bytes) else str(HEADER).encode()
                    OUTFILE.write(pack('>I', len(HEADER_BYTES)) + HEADER_BYTES)
                #DELETE THE HEADERS LIST VARIABLE AND THE HEADER VARIABLE, AFTER WRITING TO THE TEMPORARY FILE, 
                #TO PREVENT ANY HEADER DATA FROM BEING STORED, IN THE MEMORY
                del HEADERS_LIST
                del HEADER
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
        #DELETE THE ORIGINAL FILE AND RENAME THE ".tmp" FILE, TO THE ORIGINAL FILE NAME AND EXTENTION
        replace(FILE_PATH + '.tmp', FILE_PATH)
        return [True, f'AES-GCM_FILE_ENCRYPTION_SUCCESSFULL:\n{FILE_PATH}']
    except Exception as ERROR:
        if exists(FILE_PATH + '.tmp'):
            if all([access(FILE_PATH + '.tmp', W_OK), access(FILE_PATH + '.tmp', X_OK)]):
                remove(FILE_PATH + '.tmp')
            else:
                raise Exception(f'[Exception]\nFunction: "aes_gcm_encrypt_file()"\n{ERROR}\nAdditionally, the temporary file: {FILE_PATH + '.tmp'},\nwas unable to be deleted.')
        raise Exception(f'[Exception]\nFunction: "aes_gcm_encrypt_file()"\n{ERROR}\n{FILE_PATH}')

#THIS FUNCTION:
#1.) REQUIRES FILE PATH AND PASSWORD STRINGS
#2.) ACCEPTS AN OPTIONAL BLOCK SIZE INTEGER
#3.) AES-GCM DECRYPTS THE SUPPLIED FILE PATH (IF THE SUPPLIED PASSWORD, IS CORRECT)
def aes_gcm_decrypt_file(FILE_PATH, PASSWORD, BLOCK_SIZE=None):
    if not isinstance(FILE_PATH, str):
        raise TypeError('[TypeError]\nFunction: "aes_gcm_decrypt_file()"\nThe file path parameter, must be a string type.')
    elif not isfile(FILE_PATH):
        raise FileNotFoundError('[FileNotFoundError]\nFunction: "aes_gcm_decrypt_file()"\nThe file path parameter, must be a path to an existing file.')
    elif not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "aes_gcm_decrypt_file()"\nThe password parameter, must be a string type.')
    elif not PASSWORD.strip():
        raise ValueError('[ValueError]\nFunction: "aes_gcm_decrypt_file()"\nThe password parameter, cannot be empty.')
    try:
        BLOCK_SIZE = 65536 if BLOCK_SIZE is None else BLOCK_SIZE
        #CHECK IF FILE PERMISSION, IS AVAILABLE
        if exists(FILE_PATH) and not all([access(FILE_PATH, R_OK), access(FILE_PATH, W_OK), access(FILE_PATH, X_OK)]):
            return [False, f'FILE_PERMISSION_DENIED:\n{FILE_PATH}']
        #STREAM THE DATA (TO DECRYPT ALL FILE TYPES)
        with open(FILE_PATH, 'rb') as INFILE:
            #CHECK IF THE FILE, IS EMPTY, NOT AES-GCM ENCRYPTED, OR HAS ANY OTHER ERROR
            AES_GCM_HEADERS_CHECK = check_aes_gcm_headers(INFILE)
            if AES_GCM_HEADERS_CHECK[1] == 'FILE_EMPTY':
                return [False, f'FILE_EMPTY:\n{FILE_PATH}']
            elif AES_GCM_HEADERS_CHECK[1] == 'NOT_AES-GCM_ENCRYPTED':
                return [False, f'NOT_AES-GCM_ENCRYPTED:\n{FILE_PATH}']
            elif not AES_GCM_HEADERS_CHECK[0]:
                return [False, f'{AES_GCM_HEADERS_CHECK[1]}:\n{FILE_PATH}']
            ALGORITHM_AND_MODE, KEY_SIZE, NONCE_BYTES, TAG_BYTES, SALT_BYTES, TOTAL_HEADERS_SIZE = AES_GCM_HEADERS_CHECK
            #DERIVE A KEY, THAT MATCHES THE ORIGINAL KEY,
            #USING THE USER-ENTERED PASSWORD AND THE SALT BYTES STORED, IN THE FILE'S SALT BYTES HEADER
            KEY_BYTES = get_aes_key_and_salt(KEY_SIZE, PASSWORD, SALT_BYTES)[0]
            #DELETE THE PASSWORD VARIABLE, ONCE A KEY IS DERIVED, TO PREVENT ANY PLAINTEXT PASSWORD DATA FROM BEING STORED, IN THE MEMORY
            del PASSWORD
            #USE THE KEY, NONCE, AND TAG BYTES, TO CREATE A CIPHER FOR THE AES-GCM DECRYPTION
            CIPHER = Cipher(algorithms.AES(KEY_BYTES), modes.GCM(NONCE_BYTES, TAG_BYTES))
            #START THE DECRYPTION STREAMER
            DECRYPTOR = CIPHER.decryptor()
            #SET THE FILE POINTER, TO THE FIRST ENCRYPTED FILE CHUNK, AFTER THE FILE'S HEADERS
            INFILE.seek(TOTAL_HEADERS_SIZE)
            with open(FILE_PATH + '.tmp', 'wb') as OUTFILE:
                #STREAM-DECRYPT THE ENCRYPTED DATA, IN CHUNKS (TO ALLOW DECRYPTION OF ALL FILE TYPES)
                while True:
                    #READ THE BIG ENDIAN ENCODED SIZE DATA
                    SIZE_DATA = INFILE.read(4)
                    #CHECK FOR THE END OF THE FILE
                    if not SIZE_DATA or len(SIZE_DATA) < 4:
                        break
                    #READ THE AES-GCM ENCRYPTED CHUNK SIZE INTEGER
                    (CHUNK_SIZE,) = unpack('>I', SIZE_DATA)
                    #CHECK IF THE CHUNK SIZE INTEGER, IS CORRUPTED
                    if CHUNK_SIZE <= 0:
                        if exists(FILE_PATH + '.tmp'):
                            if all([access(FILE_PATH + '.tmp', W_OK), access(FILE_PATH + '.tmp', X_OK)]):
                                remove(FILE_PATH + '.tmp')
                            else:
                                return [False, f'AES-GCM_ENCRYPTED_DATA_SIZE_DATA_CORRUPTED:\n{FILE_PATH}\nAdditionally, the temporary file: {FILE_PATH + ".tmp"},\nwas unable to be deleted.']
                        return [False, f'AES-GCM_ENCRYPTED_DATA_SIZE_DATA_CORRUPTED:\n{FILE_PATH}']
                    #READ THE AES-GCM ENCRYPTED CHUNK
                    ENCRYPTED_CHUNK = INFILE.read(CHUNK_SIZE)
                    #CHECK IF THE ENCRYPTED CHUNK, IS CORRUPTED
                    if len(ENCRYPTED_CHUNK) != CHUNK_SIZE:
                        if exists(FILE_PATH + '.tmp'):
                            if all([access(FILE_PATH + '.tmp', W_OK), access(FILE_PATH + '.tmp', X_OK)]):
                                remove(FILE_PATH + '.tmp')
                            else:
                                return [False, f'AES-GCM_ENCRYPTED_DATA_CORRUPTED:\n{FILE_PATH}\nAdditionally, the temporary file: {FILE_PATH + ".tmp"},\nwas unable to be deleted.']
                        return [False, f'AES-GCM_ENCRYPTED_DATA_CORRUPTED:\n{FILE_PATH}']
                    PLAINTEXT_CHUNK = DECRYPTOR.update(ENCRYPTED_CHUNK)
                    #DELETE EACH ENCRYPTED DATA CHUNK, AFTER DECRYPTION, TO PREVENT ANY ENCRYPTED DATA FROM BEING STORED, IN THE MEMORY
                    del ENCRYPTED_CHUNK
                    OUTFILE.write(PLAINTEXT_CHUNK)
                    #DELETE EACH PLAINTEXT DATA CHUNK, AFTER WRITING THE CHUNK, TO THE ".tmp" FILE,
                    #TO PREVENT ANY PLAINTEXT DATA FROM BEING STORED, IN THE MEMORY
                    del PLAINTEXT_CHUNK
                #FINALIZE, AFTER ALL CHUNKS ARE PROCESSED
                FINAL_BYTES = DECRYPTOR.finalize()
                if FINAL_BYTES:
                    OUTFILE.write(FINAL_BYTES)
                del FINAL_BYTES
        #OVERWRITE THE ORIGINAL FILE'S ENCRYPTED CONTENTS WITH RANDOM BYTES,
        #BEFORE DELETION, TO PREVENT THE RECOVERY OF ANY ENCRYPTED DATA, FROM THE DRIVE
        with open(FILE_PATH, 'r+b') as RANDOM_BYTES_OVERWRITE_FILE:
            while True:
                ENCRYPTED_CHUNK = RANDOM_BYTES_OVERWRITE_FILE.read(BLOCK_SIZE)
                if not ENCRYPTED_CHUNK:
                    break
                RANDOM_BYTES_OVERWRITE_FILE.seek(-len(ENCRYPTED_CHUNK), 1)
                RANDOM_BYTES_OVERWRITE_FILE.write(token_bytes(len(ENCRYPTED_CHUNK)))
                #DELETE EACH AES-GCM ENCRYPTED DATA CHUNK, AFTER EACH RANDOM BYTES OVERWRITE,
                #OF THE FILE CHUNK, TO PREVENT ANY AES-GCM ENCRYPTED DATA FROM BEING STORED, IN THE MEMORY
                del ENCRYPTED_CHUNK
            RANDOM_BYTES_OVERWRITE_FILE.flush()
            fsync(RANDOM_BYTES_OVERWRITE_FILE.fileno())
        #DELETE THE ORIGINAL FILE AND RENAME THE ".tmp" FILE, TO THE ORIGINAL FILE NAME
        replace(FILE_PATH + '.tmp', FILE_PATH)
        return [True, f'AES-GCM_FILE_DECRYPTION_SUCCESSFULL:\n{FILE_PATH}']
    except InvalidTag:
        if exists(FILE_PATH + '.tmp'):
            if all([access(FILE_PATH + '.tmp', W_OK), access(FILE_PATH + '.tmp', X_OK)]):
                remove(FILE_PATH + '.tmp')
            else:
                return [False, f'INCORRECT_PASSWORD:\n{FILE_PATH}\nAdditionally, the temporary file: {FILE_PATH + ".tmp"},\nwas unable to be deleted.']
        return [False, f'INCORRECT_PASSWORD:\n{FILE_PATH}']
    except Exception as ERROR:
        if exists(FILE_PATH + '.tmp'):
            if all([access(FILE_PATH + '.tmp', W_OK), access(FILE_PATH + '.tmp', X_OK)]):
                remove(FILE_PATH + '.tmp')
            else:
                raise Exception(f'[Exception]\nFunction: "aes_gcm_decrypt_file()"\n{ERROR}\n{FILE_PATH}\nAdditionally, the temporary file: {FILE_PATH + ".tmp"},\nwas unable to be deleted.')
        raise Exception(f'[Exception]\nFunction: "aes_gcm_decrypt_file()"\n{ERROR}\n{FILE_PATH}')

#THIS FUNCTION:
#1.) REQUIRES A PLAINTEXT STRING OR BYTES TYPE VARIABLE, KEY SIZE INTEGER, AND A PASSWORD STRING
#2.) CREATES A 16 BYTE SALT AND 12 BYTE NONCE
#3.) AES-GCM ENCRYPTS THE VARIABLE
#4.) RETURNS THE ENCRYPTED VARIABLE, SALT, NONCE, AND TAG BYTES, AS A LIST 
def aes_gcm_encrypt_variable(PLAINTEXT_VARIABLE, KEY_SIZE, PASSWORD):
    KEY_SIZE_LIST = [128, 192, 256]
    if not isinstance(PLAINTEXT_VARIABLE, (str, bytes)):
        raise TypeError('[TypeError]\nFunction: "aes_gcm_encrypt_variable()"\nThe plaintext variable parameter, must be a string or bytes type.')
    elif not PLAINTEXT_VARIABLE:
        raise ValueError('[ValueError]\nFunction: "aes_gcm_encrypt_variable()"\nThe plaintext variable parameter, cannot be empty.')
    elif KEY_SIZE not in KEY_SIZE_LIST:
        raise ValueError('[ValueError]\nFunction: "aes_gcm_encrypt_variable()"\nThe key size parameter, must be an integer type, of 128, 192, or 256.')
    elif not isinstance(PASSWORD, str):
        raise TypeError('[TypeError]\nFunction: "aes_gcm_encrypt_variable()"\nThe password parameter, must be a string type.')
    elif not PASSWORD:
        raise ValueError('[ValueError]\nFunction: "aes_gcm_encrypt_variable()"\nThe password parameter, cannot be empty.')
    else:
        try:
            PLAINTEXT = PLAINTEXT_VARIABLE.encode() if isinstance(PLAINTEXT_VARIABLE, str) else PLAINTEXT_VARIABLE
            KEY_BYTES, SALT_BYTES = get_aes_key_and_salt(KEY_SIZE, PASSWORD)
            NONCE_BYTES = token_bytes(12)
            CIPHER = Cipher(algorithms.AES(KEY_BYTES), modes.GCM(NONCE_BYTES))
            ENCRYPTOR = CIPHER.encryptor()
            ENCRYPTED_VARIABLE_BYTES = ENCRYPTOR.update(PLAINTEXT) + ENCRYPTOR.finalize()
            TAG_BYTES = ENCRYPTOR.tag
            return [ENCRYPTED_VARIABLE_BYTES, SALT_BYTES, NONCE_BYTES, TAG_BYTES]
        except Exception as ERROR:
            raise Exception(f'[Exception]\nFunction: "aes_gcm_encrypt_variable()"\n{ERROR}')

#THIS FUNCTION:
#1.) REQUIRES AN ENCRYPTED VARIABLE BYTES, KEY SIZE INTEGER, PASSWORD STRING, SALT, NONCE, AND TAG BYTES
#2.) VALIDATES THE PASSWORD, USING THE SALT BYTES, TO CREATE A MATCHING KEY TO THE ORIGINAL ENCRYPTION KEY, 
#IN COMBINATION WITH THE PASSWORD, USING THE "get_aes_key_and_salt()" FUNCTION
#3.) DECRYPTS AND RETURNS THE VARIABLE, AS A BYTES TYPE, 
#IF THE PASSWORD IS CORRECT, RETURNS "None", IF THE PASSWORD IS INCORRECT
def aes_gcm_decrypt_variable(ENCRYPTED_BYTES, KEY_SIZE, PASSWORD, SALT_BYTES, NONCE_BYTES, TAG_BYTES):
    KEY_SIZE_LIST = [128, 192, 256]
    if not isinstance(ENCRYPTED_BYTES, bytes):
        raise TypeError('[TypeError]\nFunction: "aes_gcm_decrypt_variable()"\nThe encrypted bytes parameter, must be a bytes type.')
    elif not ENCRYPTED_BYTES:
        raise ValueError('[ValueError]\nFunction: "aes_gcm_decrypt_variable()"\nThe encrypted bytes parameter, cannot be empty.')
    elif KEY_SIZE not in KEY_SIZE_LIST:
        raise ValueError('[ValueError]\nFunction: "aes_gcm_encrypt_variable()"\nThe key size parameter, must be an integer type, of 128, 192, or 256.')
    elif not isinstance(SALT_BYTES, bytes):
        raise TypeError('[TypeError]\nFunction: "aes_gcm_decrypt_variable()"\nThe salt bytes parameter, must be a bytes type.')
    elif not SALT_BYTES:
        raise ValueError('[ValueError]\nFunction: "aes_gcm_decrypt_variable()"\nThe salt bytes parameter, cannot be empty.')
    elif len(SALT_BYTES) != 16:
        raise ValueError('[ValueError]\nFunction: "aes_gcm_decrypt_variable()"\nThe tag bytes parameter, must be 16 bytes long.')
    elif not isinstance(NONCE_BYTES, bytes):
        raise TypeError('[TypeError]\nFunction: "aes_gcm_decrypt_variable()"\nThe nonce bytes parameter, must be a bytes type.')
    elif not NONCE_BYTES:
        raise ValueError('[ValueError]\nFunction: "aes_gcm_decrypt_variable()"\nThe nonce bytes parameter, cannot be empty.')
    elif len(NONCE_BYTES) != 12:
        raise ValueError('[ValueError]\nFunction: "aes_gcm_decrypt_variable()"\nThe nonce bytes parameter, must be 12 bytes long.')
    elif not isinstance(TAG_BYTES, bytes):
        raise TypeError('[TypeError]\nFunction: "aes_gcm_decrypt_variable()"\nThe tag bytes parameter, must be a bytes type.')
    elif not TAG_BYTES:
        raise ValueError('[ValueError]\nFunction: "aes_gcm_decrypt_variable()"\nThe tag bytes parameter, cannot be empty.')
    elif len(TAG_BYTES) != 16:
        raise ValueError('[ValueError]\nFunction: "aes_gcm_decrypt_variable()"\nThe tag bytes parameter, must be 16 bytes long.')
    else:
        try:
            KEY_BYTES = get_aes_key_and_salt(KEY_SIZE, PASSWORD, SALT_BYTES)[0]
            CIPHER = Cipher(algorithms.AES(KEY_BYTES), modes.GCM(NONCE_BYTES, TAG_BYTES))
            DECRYPTOR = CIPHER.decryptor()
            PLAINTEXT = DECRYPTOR.update(ENCRYPTED_BYTES) + DECRYPTOR.finalize()
            return PLAINTEXT
        except InvalidTag:
            return None
        except Exception as ERROR:
            raise Exception(f'[Exception]\nFunction: "aes_gcm_decrypt_variable()"\n{ERROR}')
