from cryptography.fernet import Fernet
from app.core.config import settings

# Get encryption key from environment variables
cipher = Fernet(settings.ENCRYPTION_KEY)

def encrypt_value(value: str) -> str:
    """Encrypt a string value"""
    if not value:
        return None
    return cipher.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value: str) -> str:
    """Decrypt a string value"""
    if not encrypted_value:
        return None
    return cipher.decrypt(encrypted_value.encode()).decode()

def hash_value(value: str) -> str:
    """Create a one-way hash for duplicate checking"""
    import hashlib
    if not value:
        return None
    return hashlib.sha256(value.encode()).hexdigest()