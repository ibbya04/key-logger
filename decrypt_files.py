import os
import sys
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

dir = "out"

if __name__ == "__main__":

    password = "password".encode()
    salt = b'\x89\x07\x06\xc6i\x99\xd2\x950\xb5Sje\xe4\xd9\xff'

    kdf = PBKDF2HMAC(
            algorithm = hashes.SHA256(),
            length = 32,
            salt = salt,
            iterations = 10000,
            backend = default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))

    # Loops through all files in /out and decrypts each file
    for filename in os.listdir(dir):
        if filename.endswith('.txt'):
            with open(os.path.join(dir, filename), "rb") as file:
                data = file.read()
            fernet = Fernet(key)
            decrypted = fernet.decrypt(data)
            with open(os.path.join(dir, filename), "wb") as file:
                file.write(decrypted)