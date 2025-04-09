from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis


db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
limiter = Limiter(key_func=get_remote_address)
redis_client = None  

def create_app():
    app = Flask(__name__)
    
    app.config.from_object('app.config.Config')
    
    global redis_client
    redis_client = redis.Redis(
        host=app.config.get('REDIS_HOST', 'localhost'),
        port=app.config.get('REDIS_PORT', 6379),
        db=app.config.get('REDIS_DB', 0)
    )
    
    limiter.storage_backend = "redis://localhost:6379"  
    
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    
    from .models import User
    
    with app.app_context():
        db.create_all()
    
    from .mainRoutes.auth import auth_bp
    from .mainRoutes.admin import auth_ad

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(auth_ad, url_prefix='/api/admin')

    return app