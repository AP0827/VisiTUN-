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

def encrypt(text: str, key=None)  -> tuple[bytes,bytes]:
    nonce = os.urandom(NONCE_SIZE)
    textBytes = text.encode("utf-8")
    if key is None:
        key = read_key()
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(nonce),
        backend=default_backend()
    ).encryptor()

    # Apply the Encryption on the payload
    ciphertext = encryptor.update(textBytes) + encryptor.finalize()

    return (nonce + encryptor.tag + ciphertext, nonce, encryptor.tag)


def decrypt(tag, ciphertext: str, nonce: bytes, key=None) -> str:
    try: 
        if key is None:
            key = read_key()
        cypherBytes = ciphertext.encode("utf-8")
        payload = cypherBytes[NONCE_SIZE+16:]

        decryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce, tag),
            backend=default_backend()
        ).decryptor()

        textBytes = decryptor.update(payload) + decryptor.finalize()
        return textBytes.decode("utf-8")
    
    
    except InvalidTag:
        print("❌ Decryption failed: authentication tag mismatch.")
        return None
