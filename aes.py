import os
from Crypto.Cipher import AES
import os

def encrypt_file(key, in_filename, out_filename=None, chunksize=64*1024):
    if not out_filename:
        out_filename = in_filename + '.enc'
    iv = os.urandom(16)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)
    with open(in_filename, 'rb') as infile, open(out_filename, 'wb') as outfile:
        outfile.write(filesize.to_bytes(8, byteorder='big'))
        outfile.write(iv)
        while True:
            chunk = infile.read(chunksize)
            if len(chunk) == 0:
                break
            elif len(chunk) % 16 != 0:
                chunk += b' ' * (16 - len(chunk) % 16)
            outfile.write(encryptor.encrypt(chunk))
    return out_filename

def decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024):
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]
    with open(in_filename, 'rb') as infile:
        origsize = int.from_bytes(infile.read(8), byteorder='big')
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)
        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))
            outfile.truncate(origsize)
    return out_filename

def generate_key(key_size=16):
    return os.urandom(key_size)







# import os, base64
# import struct
# from Crypto.Cipher import AES
# from Crypto.Random import get_random_bytes

# def generate_secret_key_for_AES_cipher():
# 	# AES key length must be either 16, 24, or 32 bytes long
# 	AES_key_length = 16 # use larger value in production
# 	# generate a random secret key with the decided key length
# 	# this secret key will be used to create AES cipher for encryption/decryption
# 	secret_key = os.urandom(AES_key_length)
# 	# encode this secret key for storing safely in database
# 	encoded_secret_key = base64.b64encode(secret_key)
# 	return encoded_secret_key

# def encrypt_file(plaintext, symmetric_key):
#     # Pad the plaintext to a multiple of AES block size
#     def pad(s):
#         return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

#     plaintext = pad(plaintext)
#     iv = get_random_bytes(AES.block_size)
#     cipher = AES.new(symmetric_key, AES.MODE_CBC, iv)
#     ciphertext = iv + cipher.encrypt(plaintext)

#     # Write the encrypted file
#     return ciphertext

# def decrypt_file(file_name, symmetric_key):
#     # Decrypt the file using AES in CBC mode
#     with open(file_name, "rb") as f:
#         ciphertext = f.read()
#     iv = ciphertext[:AES.block_size]
#     cipher = AES.new(symmetric_key, AES.MODE_CBC, iv)
#     plaintext = cipher.decrypt(ciphertext[AES.block_size:])

#     # Remove the padding
#     plaintext = plaintext.rstrip(b"\0")

#     # Write the decrypted file
#     with open(file_name, "wb") as f:
#         f.write(plaintext)