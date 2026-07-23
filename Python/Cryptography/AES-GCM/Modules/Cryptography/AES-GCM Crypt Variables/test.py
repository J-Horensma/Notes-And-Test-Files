from src.aes_gcm_crypt_functions import aes_gcm_encrypt_variable, aes_gcm_decrypt_variable

try:
    while True:
        KEY_SIZE_LIST = ['128', '192', '256']
        PLAINTEXT = input('Enter something to encrypt: ')
        KEY_SIZE = input('Enter a key size (128, 192, or 256): ')
        if KEY_SIZE in KEY_SIZE_LIST:
            KEY_SIZE = int(KEY_SIZE)
        else:
            print('The key size, must be 128, 192, or 256.\n') 
            continue
        PASSWORD =  input('Enter a password: ')
        if not PASSWORD:
            print('The password, cannot be empty.\n')
            continue
        ENCRYPTED_BYTES, SALT_BYTES, NONCE_BYTES, TAG_BYTES = aes_gcm_encrypt_variable(PLAINTEXT, KEY_SIZE, PASSWORD)
        break
    print(f'Encrypted: {ENCRYPTED_BYTES}\n')
    while True:
        PASSWORD =  input('Enter the password, to decrypt: ')
        PLAINTEXT = aes_gcm_decrypt_variable(ENCRYPTED_BYTES, KEY_SIZE, PASSWORD, SALT_BYTES, NONCE_BYTES, TAG_BYTES)
        if not PLAINTEXT:
            print('The password, was incorrect!\n')
            continue
        break
    print(f'Decrypted: {PLAINTEXT}\n')
    input('Press Enter: ')
except Exception as ERROR:
    print(f'{ERROR}\n')
    input('Press Enter: ')