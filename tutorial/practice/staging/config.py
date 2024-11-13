import os
import secrets

session_secret = secrets.token_hex(16)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', session_secret)  # Get from environment variable or use default
    # Other configurations...
