import os
from dotenv import load_dotenv
from flask import jsonify
from flask_migrate import Migrate
from app import create_app, db  
from flask_talisman import Talisman
from datetime import timedelta
import logging
from logging.handlers import RotatingFileHandler

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = create_app()

# -------------------------- 1. Gelişmiş SSL Yönetimi --------------------------
def get_ssl_context():
    """Ortama özel SSL yapılandırması"""
    if app.debug:
        return 'adhoc' if os.getenv('SELF_SIGNED_SSL') == 'true' else None
    else:
        cert_path = os.getenv('SSL_CERT_PATH', '/etc/letsencrypt/live/alanadiniz.com/fullchain.pem')
        key_path = os.getenv('SSL_KEY_PATH', '/etc/letsencrypt/live/alanadiniz.com/privkey.pem')

        if not all(os.path.exists(p) for p in [cert_path, key_path]):
            raise FileNotFoundError("SSL sertifikaları bulunamadı! Kontrol edin: " + cert_path)

        return (cert_path, key_path)

# -------------------------- 2. Güncellenmiş Talisman Yapılandırması --------------------------
csp_policy = {
    'default-src': ["'none'"], 
    'script-src': [
        "'self'",
        "'nonce-{nonce}'",  
        "https://cdn.example.com"
    ],
    'style-src': ["'self'", "'unsafe-inline'"],
    'img-src': ["'self'", "data:", "https://*.mapbox.com"],
    'font-src': ["'self'", "https://fonts.gstatic.com"],
    'connect-src': ["'self'", "https://api.example.com"],
    'frame-src': ["'none'"],  
    'form-action': ["'self'"]  
}

talisman = Talisman(
    app,
    content_security_policy=csp_policy,
    force_https=not app.debug,
    strict_transport_security=not app.debug,
    strict_transport_security_max_age=31536000,  
    strict_transport_security_preload=True,
    frame_options='DENY',
    referrer_policy='no-referrer',
    feature_policy={
        'geolocation': "'none'",
        'camera': "'none'",
        'microphone': "'none'"
    }
)

# -------------------------- 3. JWT Token İyileştirmeleri --------------------------
app.config.update(
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=15),
    JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=7),
    JWT_COOKIE_SECURE=True,
    JWT_COOKIE_SAMESITE='Strict',
    JWT_BLACKLIST_ENABLED=True,
    JWT_BLACKLIST_TOKEN_CHECKS=['access', 'refresh']
)

# -------------------------- 4. Gelişmiş Loglama --------------------------
if not app.debug:
    log_handler = RotatingFileHandler(
        'app.log',
        maxBytes=1024 * 1024 * 100,  
        backupCount=5,
        encoding='utf-8'
    )
    log_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    app.logger.addHandler(log_handler)
    app.logger.setLevel(logging.INFO)

    class SensitiveDataFilter(logging.Filter):
        def filter(self, record):
            sensitive_keys = ['password', 'token', 'secret']
            for key in sensitive_keys:
                if key in record.msg.lower():
                    record.msg = record.msg.replace(key, '***REDACTED***')
            return True

    log_handler.addFilter(SensitiveDataFilter())

# -------------------------- 5. Proxy ve Header İyileştirmeleri --------------------------
if os.getenv('FLASK_ENV') == 'production':
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=2, 
        x_proto=1,
        x_host=1,
        x_prefix=1
    )

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Permitted-Cross-Domain-Policies'] = 'none'
        response.headers['Expect-CT'] = 'max-age=86400, enforce'
        response.headers['Permissions-Policy'] = 'interest-cohort=()'  
        return response

# -------------------------- 6. Hata Yönetimi --------------------------
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"message": "Kaynak bulunamadı"}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Sunucu Hatası: {str(error)}")
    return jsonify({"message": "İç sunucu hatası"}), 500

# -------------------------- 7. Başlatma --------------------------
if __name__ == "__main__":
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    
    try:
        ssl_context = get_ssl_context() if not app.debug else None
        app.run(
            host=host,
            port=port,
            ssl_context=ssl_context,
            use_reloader=False, 
            debug=app.debug,
            threaded=True,
        )
    except Exception as e:
        app.logger.critical(f"Uygulama başlatılamadı: {str(e)}")
        raise