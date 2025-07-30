# read_key(filename='face_key.bin')
# decrypt(ciphertext: bytes, nonce: bytes, key=None) -> bytes
# encrypt(payload: bytes, key=None)  -> tuple[bytes,bytes]

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag
import os

NONCE_SIZE = 12


def read_key(filename='face_key.bin'):
    with open(filename, 'rb') as f:
        return f.read()

def encrypt(payload: bytes, key=None)  -> tuple[bytes,bytes]:
    nonce = os.urandom(NONCE_SIZE)
    if key is None:
        key = read_key()
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(nonce),
        backend=default_backend()
    ).encryptor()

    # Apply the Encryption on the payload
    ciphertext = encryptor.update(payload) + encryptor.finalize()

    return (nonce + encryptor.tag + ciphertext, nonce)


def decrypt(ciphertext: bytes, nonce: bytes, key=None) -> bytes:
    try: 
        if key is None:
            key = read_key()
        tag = ciphertext[NONCE_SIZE:NONCE_SIZE+16]
        payload = ciphertext[NONCE_SIZE+16:]

        decryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce, tag),
            backend=default_backend()
        ).decryptor()

        return decryptor.update(payload) + decryptor.finalize()
    
    
    except InvalidTag:
        print("❌ Decryption failed: authentication tag mismatch.")
        return None
