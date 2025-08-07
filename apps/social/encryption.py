import os
from cryptography.fernet import Fernet
from django.conf import settings

# It's crucial that the encryption key is kept secret and consistent.
# We'll load it from the environment variables, just like the Django SECRET_KEY.
# Make sure to generate a new key for your production environment.
# You can generate a key using: Fernet.generate_key().decode()
try:
    ENCRYPTION_KEY = settings.SOCIAL_ENCRYPTION_KEY
    if not ENCRYPTION_KEY:
        raise ValueError("SOCIAL_ENCRYPTION_KEY is not set in settings.")
    f = Fernet(ENCRYPTION_KEY.encode())
except AttributeError:
    raise AttributeError("Please define SOCIAL_ENCRYPTION_KEY in your project settings.")

def encrypt_token(token: str) -> str:
    """Encrypts a token using Fernet symmetric encryption."""
    if not token:
        return ''
    return f.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    """Decrypts a token."""
    if not encrypted_token:
        return ''
    try:
        return f.decrypt(encrypted_token.encode()).decode()
    except Exception as e:
        # Log the error and handle it gracefully
        print(f"Error decrypting token: {e}")
        return ''