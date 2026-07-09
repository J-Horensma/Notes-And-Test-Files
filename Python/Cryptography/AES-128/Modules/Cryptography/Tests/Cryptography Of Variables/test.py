from time import sleep
from platform import system
from colorama import Fore
from src.aes_128_crypt_functions import aes_128_encrypt_variable, aes_128_decrypt_variable

#IF THIS FILE, IS LAUNCHED BY WINDOWS:
if system() == 'Windows':
    from colorama import just_fix_windows_console
    just_fix_windows_console()
    
def clear_console():
    print('\033[H\033[2J', end='', flush=True)

try:
    while True:
        while True:
            clear_console()
            print(f'{Fore.GREEN}AES-128 Encrypt/Decrypt A Variable{Fore.RESET} (Press "ctrl" + "c", to exit)\n')
            PLAINTEXT_VARIABLE = input('Enter a string, to encrypt: ')
            if not PLAINTEXT_VARIABLE.strip():
                print('The string, was empty, try again.')
                sleep(1)
                continue
            PASSWORD = input('Enter a password, to encrypt the string: ')
            if not PASSWORD.strip():
                print('The password, was empty, try again.')
                sleep(1)
                continue
            else:
                ENCRYPTED_VARIABLE_BYTES, SALT_BYTES = aes_128_encrypt_variable(PLAINTEXT_VARIABLE, PASSWORD)
                print(f'{Fore.GREEN}Encrypted:{Fore.RESET} {ENCRYPTED_VARIABLE_BYTES}\n')
                break
        while True:
            PASSWORD = input('Enter a password, to decrypt the string: ')
            if not PASSWORD.strip():
                print('The password, was empty, try again.')
                sleep(1)
                continue
            DECRYPTED_VARIABLE_BYTES = aes_128_decrypt_variable(ENCRYPTED_VARIABLE_BYTES, PASSWORD, SALT_BYTES)
            if not DECRYPTED_VARIABLE_BYTES:
                print('The password, was incorrect, try again.')
                sleep(1)
                continue
            else:
                print(f'{Fore.GREEN}Decrypted:{Fore.RESET} {DECRYPTED_VARIABLE_BYTES.decode()}\n')
                break
        input('Press Enter: ')
except KeyboardInterrupt:
    clear_console()
    print('Exiting...')
    sleep(1)
    exit(0)
except Exception as ERROR:
    raise Exception(f'[Exception]\nFunction: "aes_128_decrypt_variable()"\n{ERROR}')