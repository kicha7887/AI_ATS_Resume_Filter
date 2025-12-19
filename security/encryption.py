from cryptography.fernet import Fernet

KEY = b'nlbuh451loMPXPuXbFYpO7LMguVy1yinbUWp9f1WKxM='
fernet = Fernet(KEY)

def encrypt_file(data: bytes) -> bytes:
    return fernet.encrypt(data)

def decrypt_file(data: bytes) -> bytes:
    # 🔐 Only decrypt if data is actually encrypted
    if data.startswith(b"gAAAA"):
        return fernet.decrypt(data)
    else:
        # Data is already plain
        return data
