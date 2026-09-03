from time import sleep
from platform import system
from colorama import Fore
from src.aes_gcm_crypt_functions import aes_gcm_encrypt_variable, aes_gcm_decrypt_variable

#IF THIS FILE, IS LAUNCHED BY WINDOWS:
if system() == 'Windows':
    from colorama import just_fix_windows_console
    just_fix_windows_console()
    
def clear_console():
    print('\033[H\033[2J', end='', flush=True)

try:
    while True:
        KEY_SIZE_LIST = ['128', '192', '256']
        print(f'{Fore.GREEN}AES-GCM Encrypt/Decrypt A Variable Example{Fore.RESET} (Press "ctrl" + "c", to exit)\n')
        PLAINTEXT = input('Enter something to encrypt: ')
        KEY_SIZE = input('Enter a key size (128, 192, or 256): ')
        if KEY_SIZE in KEY_SIZE_LIST:
            KEY_SIZE = int(KEY_SIZE)
        else:
            print('The key size, must be 128, 192, or 256.\n') 
            continue
        PASSWORD =  input('Enter a password: ')
        if not PASSWORD:
            print('The password, cannot be empty!\n')
            continue
        #NORMALLY, THE RETURNED VARIABLE VALUES, WOULD BE STORED SOMEWHERE, LIKE A DATABASE.
        #IN THIS EXAMPLE, THE RETURNED VALUES, ARE SIMPLY CARRIED OVER TO THE DECRYPT FUNCTION.
        ENCRYPTED_BYTES, SALT_BYTES, NONCE_BYTES, TAG_BYTES = aes_gcm_encrypt_variable(PLAINTEXT, KEY_SIZE, PASSWORD)
        break
    print(f'{Fore.GREEN}Encrypted:{Fore.RESET} {ENCRYPTED_BYTES}\n')
    while True:
        PASSWORD =  input('Enter the password, to decrypt: ')
        PLAINTEXT = aes_gcm_decrypt_variable(ENCRYPTED_BYTES, KEY_SIZE, PASSWORD, SALT_BYTES, NONCE_BYTES, TAG_BYTES)
        if not PLAINTEXT:
            print('The password, was incorrect!\n')
            continue
        break
    print(f'{Fore.GREEN}Decrypted:{Fore.RESET} {PLAINTEXT}\n')
    input('Press Enter: ')
except KeyboardInterrupt:
    clear_console()
    print('Exiting...')
    sleep(1)
    exit(0)
except Exception as ERROR:
    print(f'{ERROR}\n')
    input('Press Enter: ')
