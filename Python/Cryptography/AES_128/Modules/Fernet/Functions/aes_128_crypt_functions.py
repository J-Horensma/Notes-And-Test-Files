from os import walk
from os.path import join, islink
from base64 import urlsafe_b64encode
from secrets import token_bytes
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet, InvalidToken

#THIS FUNCTION:
#1.) REQUIRES A PASSWORD STRING AND AN OPTIONAL 16 BYTE SALT BYTES
#2.) IF A SALT IS NOT SUPPLIED, A 16 BYTE SALT IS GENERATED
#3.) THE SALT, IS USED TO GENERATE A 32 BYTE PASSWORD HASH, USING THE PBKDF2 HASHING ALGORITHM, WITH 200,000 ITERATIONS OF SHA256
#4.) RETURNS A LIST, CONTAINING THE 32 BYTE PASSWORD HASH BYTES AND THE 16 BYTE SALT BYTES
def get_hash_and_salt(PASSWORD, SALT_BYTES=None):
    SALT_BYTES = token_bytes(16) if SALT_BYTES is None else SALT_BYTES
    HASH_BYTES = PBKDF2HMAC(
        algorithm=SHA256(),
        length=32, #THE NUMBER OF BYTES
        salt=SALT_BYTES,
        iterations=200_000 #THE NUMBER OF TIMES, THE PASSWORD IS HASHED
    )
    PASSWORD_BYTES = PASSWORD.encode()
    HASH_BYTES = HASH_BYTES.derive(PASSWORD_BYTES)
    return [HASH_BYTES, SALT_BYTES]

#THIS FUNCTION:
#1.) REQUIRES A STRING TO ENCRYPT AND A 32 BYTE PASSWORD HASH,
#THAT CAN BE OBTAINED FROM THE "get_hash_and_salt" FUNCTION
#2.) CONVERTS THE STRING TO AES-128 ENCRYPTED BYTES, USING THE PASSWORD HASH BYTES AS A KEY FOR THE ENCRYPTION AND LATER DECRYPTION
#3.) RETURNS THE AES-128 ENCRYPTED BYTES OR RAISES AN ERROR AND RETURNS "False"
def aes_128_encrypt_string(STRING, PASSWORD_HASH_BYTES):
    CIPHER = Fernet(urlsafe_b64encode(PASSWORD_HASH_BYTES))
    STRING_BYTES = STRING.encode()
    ENCRYPTED_STRING_BYTES = CIPHER.encrypt(STRING_BYTES)
    return ENCRYPTED_STRING_BYTES

#THIS FUNCTION:
#1.) REQUIRES THE AES-128 ENCRYPTED STRING BYTES TO DECRYPT AND THE 32 BYTE PASSWORD HASH BYTES,
#USED AS THE KEY TO ENCRYPT/DECRYPT THE STRING
#2.) CONVERTS THE AES-128 ENCRYPTED BYTES TO THE ORIGINAL STRING
#3.) RETURNS THE ORIGINAL STRING OR "False", IF THE DECRYPTION FAILS
def aes_128_decrypt_string(ENCRYPTED_STRING_BYTES, PASSWORD_HASH_BYTES):
    try:
        CIPHER = Fernet(urlsafe_b64encode(PASSWORD_HASH_BYTES))
        STRING = CIPHER.decrypt(ENCRYPTED_STRING_BYTES)
        return STRING
    except InvalidToken:
        return False
    
#THIS FUNCTION:
#1.) REQUIRES A FOLDER PATH STRING AND PASSWORD HASH BYTES
#2.) RECURSIVELY ENCRYPTS ALL FILES, WITHIN THE FOLDER, OR RAISES AN ERROR
def aes_128_encrypt_folder(FOLDER_PATH, PASSWORD_HASH_BYTES):
    for ROOT, DIRECTORIES, FILES in walk(FOLDER_PATH):
        FILES = [FILE for FILE in FILES if not FILE.startswith('.') and not islink(join(ROOT, FILE))]
        for FILE_NAME in FILES:
            FILE_PATH = join(ROOT, FILE_NAME)
            with open(FILE_PATH, 'rb') as PLAINTEXT_FILE:
                PLAINTEXT_DATA = PLAINTEXT_FILE.read()
                if PLAINTEXT_DATA.strip() == b'':
                    continue
                ENCRYPTED_DATA = aes_128_encrypt_string(PLAINTEXT_DATA.decode(), PASSWORD_HASH_BYTES)
            with open(FILE_PATH, 'wb') as ENCRYPTED_FILE:
                ENCRYPTED_FILE.write(ENCRYPTED_DATA)

#THIS FUNCTION:
#1.) REQUIRES THE PASSWORD HASH BYTES, USED TO ENCRYPT THE FOLDER
#2.) RECURSIVELY DECRYPTS ALL FILES, WITHIN THE FOLDER, OR RAISES AN ERROR
def aes_128_decrypt_folder(FOLDER_PATH, PASSWORD_HASH_BYTES):
    for ROOT, DIRECTORIES, FILES in walk(FOLDER_PATH):
        FILES = [FILE for FILE in FILES if not FILE.startswith('.') and not islink(join(ROOT, FILE))]
        for FILE_NAME in FILES:
            FILE_PATH = join(ROOT, FILE_NAME)
            with open(FILE_PATH, 'rb') as ENCRYPTED_FILE:
                ENCRYPTED_DATA = ENCRYPTED_FILE.read()
                if ENCRYPTED_DATA.strip() == b'':
                    continue
                PLAINTEXT_DATA = aes_128_decrypt_string(ENCRYPTED_DATA, PASSWORD_HASH_BYTES)
            with open(FILE_PATH, 'wb') as DECRYPTED_FILE:
                DECRYPTED_FILE.write(PLAINTEXT_DATA)