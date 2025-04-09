# app/utils.py
import logging
import os
import secrets
import string
import hashlib
from datetime import datetime, timedelta
from threading import Thread
from flask import render_template, request, current_app
from flask_limiter.util import get_remote_address
from app import create_app, redis_client
import hmac
from flask_mail import Message, Mail

def generate_cryptographic_code(length=8):
    """Güvenli rastgele kod üretimi"""
    alphabet = string.digits + string.ascii_uppercase
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_telephone_hash(telephone):
    pepper_hex = current_app.config['TELEPHONE_PEPPER']
    pepper_bytes = bytes.fromhex(pepper_hex)  # Hex string'i bytes'a çevir
    return hmac.new(
        key=pepper_bytes,
        msg=telephone.encode(),
        digestmod='sha256'
    ).hexdigest()

def validate_password_complexity(password):
    """Şifre karmaşıklık kurallarını kontrol et"""
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

def rate_limit_key():
    """Özelleştirilmiş rate limit anahtar üretici"""
    client_ip = get_remote_address()
    endpoint = request.endpoint or 'unknown'
    user_agent = request.headers.get('User-Agent', 'none')[:20]
    return f"{client_ip}:{endpoint}:{user_agent}"

mail = Mail()

def send_code_email(email, code):
    """Senkron ve context-safe e-posta gönderim fonksiyonu"""
    try:
        # 1. Uygulama context'ini kontrol et
        if not current_app:
            raise RuntimeError("Application context bulunamadı!")
        
        # 2. Config ve mail extension'larını al
        app = current_app._get_current_object()
        
        # Mail extension'ını doğru şekilde al
        mail = app.extensions.get('mail')  # Düzeltildi: .get() metodu parantez ile kullanıldı
        
        if not mail:
            raise RuntimeError("Mail extension yüklenmemiş!")

        # 3. HTML içeriğini oluştur
        html_content = f"""
        <html>
            <body style="font-family: Arial; padding: 20px;">
                <h2 style="color: #2c3e50;">MEDCHAIN PRO</h2>
                <p>Doğrulama kodunuz: <strong style="color: #e74c3c;">{code}</strong></p>
                <p><small>Bu kod 15 dakika geçerlidir</small></p>
            </body>
        </html>
        """

        # 4. Mesajı oluştur ve gönder
        msg = Message(
            subject="Hesap Doğrulama Kodu",
            recipients=[email],
            html=html_content,
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        
        mail.send(msg)
        app.logger.info(f"E-posta gönderildi: {email}")
        
        return True

    except Exception as e:
        logging.critical(f"E-posta gönderilemedi: {str(e)}", exc_info=True)
        raise


def generate_secure_token():
    random_bytes = os.urandom(32)
    return hashlib.sha256(random_bytes).hexdigest()

def validate_code(email, code):
    """Kod doğrulama fonksiyonu"""
    try:
        redis_key = f"email_code:{hashlib.sha256(email.encode()).hexdigest()}"
        stored_hash = redis_client.get(redis_key)
        
        if not stored_hash:
            return False

        calculated_hash = hmac.new(
            current_app.config['SECRET_KEY'].encode(),
            code.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(stored_hash.decode(), calculated_hash)
    
    except Exception as e:
        current_app.logger.error(f"Code validation error: {str(e)}")
        return False

def calculate_risk_score(request):
    """
    Example implementation of a risk score calculation.
    Adjust this logic based on your application's requirements.
    """
    risk_score = 0

    # Example: Increase risk score for certain IP ranges
    if request.remote_addr.startswith("192.168"):
        risk_score += 10

    # Example: Increase risk score for missing headers
    if not request.headers.get("User-Agent"):
        risk_score += 20

    # Example: Add more risk factors as needed
    return risk_score

class AccountLockedException(Exception):
    """Custom exception for account lockout."""
    pass

def check_login_attempts(email):
    key = f"login_attempts:{email}"
    attempts = redis_client.get(key) or 0
    if int(attempts) >= 5:
        raise AccountLockedException("Hesap geçici olarak kilitlendi")
    return True