from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///default.db')
    
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or os.urandom(32).hex()  
    if not JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY must be set in environment or .env file")
    
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_EXPIRATION_HOURS', 24)))


    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1'] if MAIL_PORT == 587 else False
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() in ['true', '1'] if MAIL_PORT == 465 else False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', f"MedChain Pro <{MAIL_USERNAME}>")

    # Rate Limiting
    REDIS_URL = os.getenv('REDIS_URL', "redis://localhost:6379/0")
    RATELIMIT_STORAGE_URI = REDIS_URL
    RATELIMIT_STRATEGY = os.getenv('RATELIMIT_STRATEGY', "fixed-window")
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
    TELEPHONE_PEPPER = os.getenv('TELEPHONE_PEPPER', os.urandom(16).hex())