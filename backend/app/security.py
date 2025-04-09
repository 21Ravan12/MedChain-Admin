from datetime import time
import hmac
import hashlib
from cryptography.fernet import Fernet
from flask import current_app, jsonify, request
import redis
from itsdangerous import BadSignature, URLSafeSerializer
from werkzeug.security import check_password_hash
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt, JWTManager
from urllib.parse import urlparse
import os
import socket

from app.models import TokenBlacklist

jwt = JWTManager()

class SSRFError(Exception):
    """Custom exception for Server-Side Request Forgery (SSRF) errors."""
    pass

fernet_key = os.environ.get('FERNET_KEY')
hmac_key = os.environ.get('HMAC_KEY')

if not fernet_key or not hmac_key:
    raise RuntimeError("Critical environment variables are missing. Please check the configuration.")

fernet = Fernet(fernet_key)
hmac_key = hmac_key.encode()

redis_client = redis.StrictRedis(
    host=os.environ.get('REDIS_HOST', 'localhost'),
    port=int(os.environ.get('REDIS_PORT', 6379)),
    db=int(os.environ.get('REDIS_DB', 0)),
    decode_responses=True
)

def encrypt_data(data):
    if not isinstance(data, str):
        raise ValueError("Data to encrypt must be a string.")
    try:
        encrypted = fernet.encrypt(data.encode()).decode()
        current_app.logger.info("Data encrypted successfully.")
        return encrypted
    except Exception as e:
        current_app.logger.error("Encryption failed.")
        raise RuntimeError("Encryption failed.")

def decrypt_data(encrypted_data):
    if not encrypted_data:
        return None
    try:
        decrypted = fernet.decrypt(encrypted_data).decode()
        current_app.logger.info("Data decrypted successfully.")
        return decrypted
    except Exception as e:
        current_app.logger.error("Decryption failed.")
        raise RuntimeError("Decryption failed.")

def generate_email_hash(email):
    return hmac.new(hmac_key, email.encode(), hashlib.sha256).hexdigest()

def hash_data(data):
    return hashlib.pbkdf2_hmac('sha256', data.encode(), current_app.config['SECRET_KEY'].encode(), 100000).hex()

def validate_password_complexity(password):
    if len(password) < 12:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for c in password):
        return False
    return True

def validate_csrf_token(signed_token, max_age=1800):
    try:
        s = URLSafeSerializer(current_app.secret_key)
        token_data = s.loads(signed_token)
        
        current_time = int(time.time())
        if current_time - token_data['timestamp'] > max_age:
            return False, "CSRF token expired"
        
        redis_key = f"csrf:{token_data['token']}"
        if not redis_client.delete(redis_key):
            return False, "CSRF token already used or invalid"
        
        return True, token_data['token']
    except BadSignature:
        return False, "Invalid CSRF token"
    except Exception as e:
        current_app.logger.error("CSRF token validation failed.")
        return False, "Error verifying CSRF token."

def role_required(required_role):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('role') != required_role:
                return jsonify({"message": "You do not have the required permissions!"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def validate_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ["http", "https"]:
        raise SSRFError("Invalid URL scheme.")
    
    try:
        ip = socket.gethostbyname(parsed.hostname)
        if ip.startswith("127.") or ip.startswith("10.") or ip.startswith("192.168.") or ip.startswith("172."):
            raise SSRFError("Blocked private IP address.")
    except Exception as e:
        raise SSRFError("Failed to resolve URL.")
    
    return True

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    try:
        return bool(redis_client.get(f"revoked_token:{jti}"))
    except Exception as e:
        current_app.logger.error("Failed to check token revocation.")
        return True

def generate_data_signature(data):
    secret = current_app.config.get('DATA_INTEGRITY_SECRET')
    if not secret:
        raise RuntimeError("DATA_INTEGRITY_SECRET is not defined!")
    return hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()