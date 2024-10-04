from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
import os

def bytes_to_str(bytes):
  return ''.join([chr(byte) for byte in bytes])

# key = bytearray.fromhex('bff207f86af3cc9a6b9aac9950d86332cf0937f5ae413a2742fa2afa27831b5f')
# iv = bytearray.fromhex('b6d942b5a77f8a0c2769489f5a0053cd')

# Key and IV generation
key = os.urandom(32)  # AES-256 key
iv = os.urandom(16)   # 16-byte IV for CBC mode
# print('>>>', len(key.hex()), key.hex())
# print('>>>', len(iv.hex()), iv.hex())

message = b'Hello, World!'
print('>>>', bytes_to_str(message))

# Cipher and encryptor
cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
encryptor = cipher.encryptor()

# PKCS7 padding
padder = PKCS7(algorithms.AES.block_size).padder()
padded_data = padder.update(message) + padder.finalize()

# Encrypt the data
ciphertext = encryptor.update(padded_data) + encryptor.finalize()
print('>>>', ciphertext.hex())

# Decryptor for the same ciphertext
decryptor = cipher.decryptor()
decrypted_padded_data = decryptor.update(ciphertext) + decryptor.finalize()

# Unpadding
unpadder = PKCS7(algorithms.AES.block_size).unpadder()
plaintext = unpadder.update(decrypted_padded_data) + unpadder.finalize()
print('>>>', bytes_to_str(plaintext))
