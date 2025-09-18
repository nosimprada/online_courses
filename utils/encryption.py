from cryptography.fernet import Fernet
from config import ENCRYPTION_KEY

cipher = Fernet(ENCRYPTION_KEY)


def encrypt(s: str) -> bytes:
    return cipher.encrypt(s.encode("utf-8"))

def decrypt(b: bytes) -> str:
    return cipher.decrypt(b).decode("utf-8")