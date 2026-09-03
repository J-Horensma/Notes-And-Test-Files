![Preview](assets/icon/ico/256x256.ico)  
<br></br>

# AES-GCM File-Crypter (Graphical User Interface)  

## What Does This Application Do?
This application, makes AES-GCM cryptography of files and/or entire folders, quick and easy for Windows and Linux.  

## What Is AES-GCM?
AES-GCM, is the most secure and modern approach for encryption/decryption and has 3 options (128, 192, and 256 bit).  
<br></br>

## Windows Version ("dist/windows" folder):  
</br>

![Preview](assets/previews/preview_1.png)
### 1.) Pick encryption/decryption options
![Preview](assets/previews/preview_2.png)
### 2.) Enter the password
![Preview](assets/previews/preview_3.png)
### 3.) Encrypt/decrypt a file or an entire folder
![Preview](assets/previews/preview_4.png)  
<br></br>

## Linux Version ("dist/linux" folder):  
</br>

![Preview](assets/previews/linux_preview_1.png)
### 1.) Pick encryption/decryption options
![Preview](assets/previews/linux_preview_2.png)
### 2.) Enter the password
![Preview](assets/previews/linux_preview_3.png)
### 3.) Encrypt/decrypt a file or an entire folder
![Preview](assets/previews/linux_preview_4.png)    
<br></br>

## Compile, Yourself (Optional):  

### Windows
1.) Make sure the latest python, PyInstaller, and any missing requirements are installed, \
then open a terminal and change directory to this file's directory, before entering the following shellcode \
2.) ```python -m PyInstaller --clean --noconfirm --onefile --windowed --icon=assets/icon/ico/icon.ico --add-data "assets;assets" "AES-GCM File-Crypter.pyw"```  

### Linux:
1.) Make sure the latest python, PyInstaller, and any missing requirements are installed, \
then open a terminal and change directory to this file's directory, before entering the following shellcode \
2.) ```python -m PyInstaller --clean --noconfirm --onefile --windowed --icon="assets/icon/ico/icon.ico" --add-data "assets:assets" --hidden-import=_cffi_backend --collect-binaries cffi --collect-data cffi "AES-GCM File-Crypter.pyw"```
