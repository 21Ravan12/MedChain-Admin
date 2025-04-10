# auth.py (Tam Sürüm)
import base64
from datetime import datetime, time, timedelta
import random
import re
from threading import Thread
import uuid
from flask import Blueprint, app, json, make_response, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token,
    get_jwt, 
    jwt_required, 
    get_jwt_identity,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    decode_token
)
from itsdangerous import URLSafeSerializer
from psycopg2 import IntegrityError
import redis
from rich import _console
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, limiter, redis_client
from app.models import Admin, Doctor, Hospital, HospitalAdmin, Patient, Pharmacist, Pharmacy, PharmacyAdmin, TokenBlacklist, User, AuditLog
from app.utils import (
    check_login_attempts,
    generate_secure_token,
    send_code_email,
    generate_cryptographic_code,
    validate_password_complexity,
    rate_limit_key,
    generate_telephone_hash,
    calculate_risk_score  # Ensure this is imported if it exists
)
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf

# Define valid medical specialties
MEDICAL_SPECIALTIES = {'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Dermatology'}

MEDICAL_DEGREES = {'MD', 'DO', 'MBBS', 'BDS', 'DVM'}

HOSPITAL_DEPARTMENTS = {'emergency', 'cardiology', 'neurology', 'oncology', 'pediatrics', 'radiology'}

HOSPITAL_TYPES = {'general', 'specialty', 'clinic'}

PHARMACY_DEGREES = {'PharmD', 'BPharm', 'MPharm', 'DPharm'}

ADMIN_SECURITY_LEVELS = {'standard', 'elevated', 'super'}

from app.security import (
    encrypt_data,
    decrypt_data,
    generate_email_hash,
    role_required,
    validate_csrf_token,
    validate_url
)
import bleach
import hmac
import hashlib
import os
import pyotp

csrf = CSRFProtect()

auth_bp = Blueprint('auth', __name__)

DEFAULT_LIMITS = "5 per minute; 100 per day"

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("3/minute; 20/hour", key_func=rate_limit_key)
def register():
    current_app.logger.info(f"Registration endpoint called - IP: {request.remote_addr}")
    
    try:
        if not request.is_json:
            current_app.logger.warning("Invalid content type")
            return jsonify({"message": "Content-Type must be application/json"}), 415
            
        csrf_token = request.headers.get('X-CSRF-Token')
        if not csrf_token:
            current_app.logger.warning("Missing CSRF token")
            return jsonify({"message": "CSRF token required"}), 403
            
        if not validate_csrf_token(csrf_token):
            current_app.logger.warning("Invalid CSRF token")
            return jsonify({"message": "Invalid CSRF token"}), 403

        data = request.get_json()
        if not data:
            current_app.logger.warning("Invalid JSON format")
            return jsonify({"message": "Invalid data format"}), 400

        required_fields = {'email', 'password', 'name'}
        missing_fields = required_fields - data.keys()
        if missing_fields:
            current_app.logger.warning(f"Missing fields: {missing_fields}")
            return jsonify({"message": f"Missing information: {', '.join(missing_fields)}"}), 400

        email = data['email'].strip().lower()
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            current_app.logger.warning(f"Invalid email format")
            return jsonify({"message": "Invalid email format"}), 400

        password = data['password'].strip()
        if not (len(password) >= 12 
                and any(c.isupper() for c in password) 
                and any(c.isdigit() for c in password)
                and any(not c.isalnum() for c in password)):
            current_app.logger.warning("Weak password detected")
            return jsonify({"message": "Password must contain 12+ chars, 1 uppercase, 1 number, and 1 special char"}), 400

        telephone = None
        if 'telephone' in data:
            telephone = bleach.clean(data['telephone']).strip()
            if not re.match(r'^\+?[1-9]\d{4,14}$', telephone):
                current_app.logger.warning(f"Invalid phone format: {telephone}")
                return jsonify({"message": "Invalid phone number format"}), 400
                
            if User.query.filter_by(telephone_hash=generate_telephone_hash(telephone)).first():
                current_app.logger.warning(f"Phone conflict: {telephone}")
                return jsonify({"message": "This phone number is already registered"}), 409

        if User.query.filter_by(email_hash=generate_email_hash(email)).first():
            current_app.logger.warning(f"Email conflict")
            return jsonify({"message": "This email is already registered"}), 409

        if redis_client.get(f"reg_attempt:{email}"):
            current_app.logger.warning(f"Too many attempts for email: {email}")
            return jsonify({"message": "Too many registration attempts. Please wait."}), 429
        redis_client.setex(f"reg_attempt:{email}", timedelta(minutes=5), "1")

        encrypted_data = {
            'email': encrypt_data(email),
            'name': encrypt_data(bleach.clean(data['name'])),
            'password': generate_password_hash(password, 'pbkdf2:sha256'),
            'telephone': encrypt_data(telephone) if telephone else None
        }

        try:
            verification_code = generate_cryptographic_code()
            challenge = os.urandom(32)
            challenge_hex = challenge.hex()
            redis_key = challenge_hex  
            
            redis_data = {
                **encrypted_data,
                'code': verification_code,
                'ip': request.remote_addr,
                'user_agent': request.user_agent.string[:200],
                'created_at': datetime.utcnow().isoformat(),
                'attempts': 0,  
                'device_fingerprint': request.headers.get('X-Device-Fingerprint', ''),
                'metadata': {
                    'source': 'web',
                    'security_level': 'high'
                }
            }
            
            if not redis_client.setex(
                name=redis_key,
                time=timedelta(minutes=15),
                value=encrypt_data(json.dumps(redis_data))
            ):
                raise RuntimeError("Redis operation failed")
                
        except redis.exceptions.RedisError as redis_err:  
            current_app.logger.error(f"Redis error: {str(redis_err)}")
            return jsonify({"message": "Temporary system error"}), 503

        try:
            send_code_email(email, code=verification_code)
            current_app.logger.info(f"Verification code sent to {email}")
        except Exception as e:
            current_app.logger.error(f"Email sending failed: {str(e)}")
            redis_client.delete(redis_key)  
            return jsonify({"message": "Verification code could not be sent"}), 500

        AuditLog.log_async(
            event='REGISTER_ATTEMPT',
            user=email,
            ip=request.remote_addr,
            user_agent=request.user_agent.string,
            metadata={
                'risk_score': calculate_risk_score(request) if 'calculate_risk_score' in globals() else 'unknown',
                'risk_score': calculate_risk_score(request),
                'headers': {k: v for k, v in request.headers.items() 
                           if k.lower() in ['user-agent', 'accept-language']}
            }     
        )

        current_app.logger.info(f"Successful registration attempt for {email}")

        response = jsonify({
            "message": "Verification code sent to your email",
            "cooldown": 180,
            "redis_key": challenge_hex,
            "security": {
                "level": "high",
                "features": ["csrf_protection", "rate_limiting", "encrypted_storage"]
            }
        })
        
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response, 200

    except Exception as e:
        current_app.logger.critical(
            f"CRITICAL ERROR | IP: {request.remote_addr} | Error: {str(e)}",
            exc_info=True
        )
        return jsonify({"message": "An error occurred during processing"}), 500

@auth_bp.route('/resend-verification-code', methods=['POST'])
@limiter.limit("3/minute; 20/hour", key_func=rate_limit_key)
def resend_verification_code():
    current_app.logger.info(f"Verification code resend endpoint called - IP: {request.remote_addr}")
    
    try:
        csrf_token = request.headers.get('X-CSRF-TOKEN')
        if not csrf_token:
            current_app.logger.warning("Missing CSRF token")
            return jsonify({"message": "CSRF token required"}), 403
            
        if not validate_csrf_token(csrf_token):
            current_app.logger.warning("Invalid CSRF token")
            return jsonify({"message": "Invalid CSRF token"}), 403

        if not request.is_json:
            current_app.logger.warning("Invalid content type")
            return jsonify({"message": "Content-Type must be application/json"}), 415

        data = request.get_json()
        if not data:
            current_app.logger.warning("Invalid JSON format")
            return jsonify({"message": "Invalid data format"}), 400

        redis_key = data.get('redis_key', '').strip()
        if not redis_key:
            current_app.logger.error("Missing redis_key parameter")
            return jsonify({"message": "Missing registration ID"}), 400

        request_type = data.get('type', '').strip().lower()
        if request_type not in ('register', 'changecode'):
            current_app.logger.error("Invalid type parameter")
            return jsonify({"message": "Invalid request type"}), 400

        encrypted_data = redis_client.get(redis_key)
        if not encrypted_data:
            current_app.logger.error(f"Invalid Redis key: {redis_key}")
            return jsonify({"message": "Invalid or expired session"}), 400

        try:
            user_data = json.loads(decrypt_data(encrypted_data))
        except (ValueError, json.JSONDecodeError) as e:
            current_app.logger.error(f"JSON parse error: {str(e)}")
            return jsonify({"message": "Invalid session data"}), 400
        except Exception as e:
            current_app.logger.error(f"Decryption failed: {str(e)}")
            return jsonify({"message": "Security validation failed"}), 400

        if user_data.get('ip') != request.remote_addr:
            current_app.logger.warning(f"IP mismatch: {request.remote_addr} vs {user_data.get('ip')}")
            return jsonify({"message": "Session validation failed"}), 403

        verification_code = generate_cryptographic_code()
        new_redis_key = os.urandom(32).hex()

        redis_data = {
            'code': verification_code,
            'ip': request.remote_addr,
            'user_agent': request.user_agent.string[:200],
            'created_at': datetime.utcnow().isoformat(),
            'attempts': 0,
            'previous_key': redis_key  
        }

        if request_type == 'register':
            redis_data.update({
                'email': user_data['email'],
                'name': user_data['name'],
                'password': user_data['password'],
                'telephone': user_data.get('telephone')
            })
            email = decrypt_data(user_data['email'])
        elif request_type == 'changecode':
            redis_data['user_id'] = user_data['user_id']
            user = User.query.get(user_data['user_id'])
            if not user:
                current_app.logger.error(f"User not found: {user_data['user_id']}")
                return jsonify({"message": "User not found"}), 404
            email = decrypt_data(user.email_encrypted)

        try:
            if not redis_client.setex(
                name=new_redis_key,
                time=timedelta(minutes=15),
                value=encrypt_data(json.dumps(redis_data))
            ):
                raise RuntimeError("Redis operation failed")
            
            redis_client.delete(redis_key)
        except redis.exceptions.RedisError as e:
            current_app.logger.error(f"Redis error: {str(e)}")
            return jsonify({"message": "Temporary system error"}), 503

        try:
            send_code_email(email, code=verification_code)
            current_app.logger.info(f"Verification code sent to {email}")
        except Exception as e:
            current_app.logger.error(f"Email sending failed: {str(e)}")
            redis_client.delete(new_redis_key)  # Clean up on failure
            return jsonify({"message": "Failed to send verification code"}), 500

        AuditLog.log_async(
            event='VERIFICATION_CODE_RESENT',
            user=email,
            ip=request.remote_addr,
            user_agent=request.user_agent.string,
            metadata={
                'type': request_type,
                'new_redis_key': new_redis_key,
                'previous_key': redis_key,
                'security': {
                    'ip_match': user_data.get('ip') == request.remote_addr,
                    'user_agent_match': user_data.get('user_agent') == request.user_agent.string
                }
            }     
        )

        response = jsonify({
            "message": "Verification code sent to your email",
            "cooldown": 180,
            "redis_key": new_redis_key,
            "security": {
                "session_expiry": 900,  
                "remaining_attempts": 3  
            }
        })
        
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        
        return response, 200

    except Exception as e:
        current_app.logger.critical(
            f"CRITICAL ERROR | IP: {request.remote_addr} | Error: {str(e)}",
            exc_info=True
        )
        return jsonify({"message": "An error occurred during processing"}), 500
     
@auth_bp.route('/complete-registration', methods=['POST'])
@limiter.limit("5 per minute", key_func=rate_limit_key)
def complete_registration():
    current_app.logger.info(f"Complete registration endpoint called - IP: {request.remote_addr}")
    
    try:
        csrf_token = request.headers.get('X-CSRF-TOKEN')
        if not csrf_token:
            current_app.logger.warning("Missing CSRF token")
            return jsonify({"message": "CSRF token required"}), 403
            
        if not validate_csrf_token(csrf_token):
            current_app.logger.warning("Invalid CSRF token")
            return jsonify({"message": "Invalid CSRF token"}), 403

        if not request.is_json:
            current_app.logger.error("Invalid content type")
            return jsonify({"message": "Content-Type must be application/json"}), 415

        data = request.get_json()
        if not data:
            current_app.logger.error("Invalid JSON payload")
            return jsonify({"message": "Invalid request format"}), 400

        redis_key = data.get('redis_key', '').strip()
        if not redis_key:
            current_app.logger.error("Missing redis_key parameter")
            return jsonify({"message": "Missing registration ID"}), 400
            
        verification_code = str(data.get('code', '')).strip()
        if not verification_code:
            current_app.logger.error("Missing verification code")
            return jsonify({"message": "Missing verification code"}), 400

        encrypted_data = redis_client.get(redis_key)
        if not encrypted_data:
            current_app.logger.error(f"Invalid or expired Redis key: {redis_key}")
            return jsonify({"message": "Invalid or expired registration session"}), 400

        try:
            user_data = json.loads(decrypt_data(encrypted_data))
        except (ValueError, json.JSONDecodeError) as e:
            current_app.logger.error(f"JSON parse error: {str(e)}")
            return jsonify({"message": "Invalid registration data"}), 400
        except Exception as e:
            current_app.logger.error(f"Decryption failed: {str(e)}")
            return jsonify({"message": "Security validation failed"}), 400

        if user_data.get('ip') != request.remote_addr:
            current_app.logger.warning(f"IP mismatch: {request.remote_addr} vs {user_data.get('ip')}")
            return jsonify({"message": "Session validation failed"}), 403

        stored_code = str(user_data.get('code', ''))
        if not hmac.compare_digest(stored_code, verification_code):
            current_app.logger.warning(f"Code mismatch for session {redis_key}")
            AuditLog.log_async(
                event='INVALID_VERIFICATION_ATTEMPT',
                user=user_data.get('email'),
                ip=request.remote_addr,
                user_agent=request.user_agent.string,
                metadata={
                    'provided_code': verification_code,
                    'expected_code': stored_code[-4:] + '...' 
                }
            )
            return jsonify({"message": "Invalid verification code"}), 400

        email = decrypt_data(user_data['email'])
        if User.query.filter_by(email_hash=generate_email_hash(email)).first():
            current_app.logger.warning(f"Duplicate registration for {email}")
            return jsonify({"message": "Account already exists"}), 409

        new_user = User(
            email_encrypted=user_data['email'],
            email_hash=generate_email_hash(email),
            password=user_data['password'],
            name_encrypted=user_data['name'],
            telephone_encrypted=user_data.get('telephone'),
            last_password_change=datetime.utcnow(),
            account_verified=True,
        )

        db.session.add(new_user)
        db.session.commit()

        encrypted_data = {
            'user_id': encrypt_data(str(new_user.id)),
            'ip': request.remote_addr,
            'user_agent': request.user_agent.string[:200],
            'created_at': datetime.utcnow().isoformat(),
            'attempts': 0,  
            'device_fingerprint': request.headers.get('X-Device-Fingerprint', ''),
            'metadata': {
                'source': 'web',
                'security_level': 'high'
            }
        }
        new_redis_key = os.urandom(32).hex()

        try:
            if not redis_client.setex(
                name=new_redis_key,
                time=timedelta(minutes=15),
                value=encrypt_data(json.dumps(encrypted_data))
            ):
                raise RuntimeError("Redis operation failed")
            
            redis_client.delete(redis_key)
        except redis.exceptions.RedisError as e:
            current_app.logger.error(f"Redis error: {str(e)}")
            return jsonify({"message": "Temporary system error"}), 503

        access_token = create_access_token(identity=str(new_user.id))
        refresh_token = create_refresh_token(identity=str(new_user.id))

        AuditLog.log_async(
            event='REGISTRATION_COMPLETED',
            user=new_user.id,
            ip=request.remote_addr,
            user_agent=request.user_agent.string,
            metadata={
                'registration_method': 'email',
                'device_fingerprint': request.headers.get('X-Device-Fingerprint')
            }
        )

        response = jsonify({
            "message": "Registration successful",
            "redis_key": new_redis_key,
            "security": {
                "cookie_domains": current_app.config.get('JWT_COOKIE_DOMAIN'),
                "cookie_secure": True,
                "same_site": "Strict"
            }
        })
        
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        current_app.logger.info(f"New user registered: {email}")
        return response, 200

    except Exception as e:
        current_app.logger.critical(
            f"Registration failed - IP: {request.remote_addr} - Error: {str(e)}",
            exc_info=True
        )
        db.session.rollback()
        return jsonify({"message": "An error occurred during registration"}), 500
    
@auth_bp.route('/select-role', methods=['POST'])
@limiter.limit("3/minute; 20/hour", key_func=rate_limit_key)
def select_role():
    """Handle role selection and complete user registration process."""
    current_app.logger.info(f"Role selection endpoint called - IP: {request.remote_addr}")
    
    try:
        csrf_token = request.headers.get('X-CSRF-Token') or request.json.get('csrf_token')
        if not csrf_token:
            current_app.logger.warning("Missing CSRF token")
            return jsonify({"message": "CSRF token required"}), 403
            
        if not validate_csrf_token(csrf_token):
            current_app.logger.warning(f"Invalid CSRF token received: {csrf_token[:8]}...")
            return jsonify({"message": "Invalid CSRF token"}), 403

        try:
            data = request.get_json(force=True, silent=False)
            if not data or not isinstance(data, dict):
                raise ValueError("Invalid JSON data")
        except ValueError as e:
            current_app.logger.warning(f"Invalid JSON format: {str(e)}")
            return jsonify({"message": "Invalid data format"}), 400

        required_fields = {'role', 'redis_key'}
        missing_fields = required_fields - set(data.keys())
        if missing_fields:
            current_app.logger.warning(f"Missing fields: {missing_fields}")
            return jsonify({"message": f"Missing information: {', '.join(missing_fields)}"}), 400

        valid_roles = {'patient', 'doctor', 'hospital', 'hospitalAdmin', 'pharmacy', 'pharmacyAdmin', 'pharmacist', 'admin'}
        role = data.get('role', '').strip()

        current_app.logger.warning(f"Current fields: {role}")

        if role not in valid_roles:
            current_app.logger.warning(f"Invalid role selected: {role}")
            return jsonify({"message": "Invalid role selection"}), 400
                
        role_required_fields = {
            'patient': {
                'required': {'birthyear', 'id_proof', 'insurance'},
                'optional': {'profile_image', 'medical_history', 'blood_type'},
                'validation': {
                    'birthyear': lambda x: isinstance(x, int) and 1900 <= x <= datetime.now().year,
                    'id_proof': lambda x: isinstance(x, str) and len(x) > 10,  
                    'insurance': lambda x: isinstance(x, str) and len(x) > 5
                }
            },
            'doctor': {
                'required': {'license_number', 'specialty', 'hospital_id', 'degree'},
                'optional': {'profile_image', 'available_hours', 'languages'},
                'validation': {
                    'license_number': lambda x: isinstance(x, str) and len(x) in (8, 12),
                    'specialty': lambda x: x in MEDICAL_SPECIALTIES,  
                    'degree': lambda x: x in MEDICAL_DEGREES  
                }
            },
            'hospitalAdmin': {
                'required': {'hospital_id', 'admin_id', 'department', 'qualifications'},
                'optional': {'profile_image', 'access_level', 'employment_verification'},
                'validation': {
                    'hospital_name': lambda x: isinstance(x, str) and 2 <= len(x) <= 100,
                    'admin_id': lambda x: isinstance(x, str) and len(x) == 8,
                    'qualifications': lambda x: isinstance(x, list) and all(isinstance(q, str) for q in x)
                }
            },
            'hospital': {
                'required': {'license_number', 'address', 'established', 'type','logo', 'beds', 'operating_hours', 'emergency_services',
                    'accreditation', },
                'optional': {
                    'medical_staff', 'website'
                },
                'validation': {
                    #'license_number': lambda x: isinstance(x, str) and x.startswith('HOSP-'),
                    'address': lambda x: isinstance(x, str) and len(x) > 10,
                    'established': lambda x: isinstance(x, str) and re.match(r'^\d{4}-\d{2}-\d{2}$', x),  # Format: YYYY-MM-DD
                    'type': lambda x: x in HOSPITAL_TYPES  # e.g., ['general', 'specialty', 'clinic']
                }
            },
            'pharmacy': {
                'required': {'license_number', 'address', 'established'},
                'optional': {
                    'logo', 'operating_hours', 'inventory_size',
                    'accreditation', 'prescriptions_filled', 'pharmacists_count'
                },
                'validation': {
                    'license_number': lambda x: isinstance(x, str) and x.startswith('PHARM-'),
                    'address': lambda x: isinstance(x, str) and len(x) > 10,
                    'established':  lambda x: isinstance(x, str) and re.match(r'^\d{4}-\d{2}-\d{2}$', x),
                }
            },
            'pharmacyAdmin': {
                'required': {'pharmacy_id', 'admin_id'},
                'optional': {'profile_image', 'access_level', 'pharmacist_cert'},
                'validation': {
                    'pharmacy_name': lambda x: isinstance(x, str) and 2 <= len(x) <= 100,
                    'admin_id': lambda x: isinstance(x, str) and len(x) == 8,
                    'pharmacy_branch': lambda x: isinstance(x, str) and len(x) <= 50,
                    'pharmacy_license': lambda x: isinstance(x, str) and x.startswith('PHARM-')
                }
            },
            'pharmacist': {
                'required': {'license_number', 'pharmacy_id'},
                'optional': {'specialization', 'years_experience'},
                'validation': {
                    'license_number': lambda x: isinstance(x, str) and len(x) in (10, 12),
                    'degree': lambda x: x in PHARMACY_DEGREES  
                }
            },
            'admin': {
                'required': {'security_level'},
                'optional': {'profile_image', 'audit_access'},
                'validation': {
                    'security_level': lambda x: x in ADMIN_SECURITY_LEVELS  
                }
            }
        }
        
        if role not in role_required_fields:
           current_app.logger.warning(f"Invalid role specified: {role}")
           return jsonify({"message": "Invalid role specified"}), 400

        required_fields = role_required_fields[role]['required']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
           current_app.logger.warning(f"Missing required fields for {role}: {missing_fields}")
           return jsonify({"message": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        validation_rules = role_required_fields[role].get('validation', {})
        for field, validator in validation_rules.items():
           if field in data:  
              try:
                 if not validator(data[field]):
                    current_app.logger.warning(f"Validation failed for {role}.{field}: {data[field]}")
                    return jsonify({"message": f"Invalid value for {field}"}), 400
              except Exception as e:
                 current_app.logger.error(f"Validation error for {role}.{field}: {str(e)}")
                 return jsonify({"message": f"Validation error for {field}"}), 400


        redis_key = data.get('redis_key', '').strip()
        if not redis_key or len(redis_key) > 128:
            current_app.logger.warning("Invalid redis_key format")
            return jsonify({"message": "Invalid session key"}), 400

        try:
            with redis_client.pipeline() as pipe:
                pipe.watch(redis_key)
                encrypted_data = pipe.get(redis_key)
                
                if not encrypted_data:
                    current_app.logger.warning("Invalid or expired verification key")
                    return jsonify({"message": "Session expired or invalid. Please restart registration."}), 400
                   
                try:
                    decrypted_data = json.loads(decrypt_data(encrypted_data))
                    required_decrypted_fields = {'ip', 'user_id'}
                    if not all(field in decrypted_data for field in required_decrypted_fields):
                        raise ValueError("Missing required fields in decrypted data")
                        
                    client_ip = request.remote_addr
                    if decrypted_data.get('ip') != client_ip:
                        current_app.logger.warning(f"IP mismatch: {client_ip} vs {decrypted_data.get('ip')}")
                        return jsonify({"message": "Session validation failed"}), 403
                        
                except (json.JSONDecodeError, ValueError, Exception) as e:
                    current_app.logger.error(f"Decryption/data error: {str(e)}")
                    pipe.unwatch()
                    return jsonify({"message": "Session validation error"}), 400
                    
                pipe.multi()
                pipe.delete(redis_key)
                pipe.execute()
                
        except redis.exceptions.RedisError as e:
            current_app.logger.error(f"Redis error: {str(e)}")
            return jsonify({"message": "Session validation error"}), 500

        try:
            user_id = decrypt_data(decrypted_data['user_id'])
            if not user_id or not isinstance(user_id, str):
                raise ValueError("Invalid user ID")
        except Exception as e:
            current_app.logger.error(f"User ID decryption failed: {str(e)}")
            return jsonify({"message": "Session validation error"}), 400

        existing_user = User.query.filter_by(id=user_id).first()
        if not existing_user:
            current_app.logger.warning(f"User not found: {user_id}")
            return jsonify({"message": "User not found"}), 404

        try:
            with db.session.begin_nested():
                existing_user.role = role
                db.session.add(existing_user)

                submission_date = encrypt_data(str(datetime.utcnow()))
                
                role_models = {
                    'patient': Patient(
        user_id=user_id,
        birthyear_encrypted=encrypt_data(str(data.get('birthyear', ''))),
        profile_image_encrypted=encrypt_data(str(data.get('profile_image', ''))),
        submission_date_encrypted=submission_date,
        patient_id_encrypted=encrypt_data(str(data.get('patient_id', ''))),
        id_proof_encrypted=encrypt_data(str(data.get('id_proof', ''))),
        insurance_encrypted=encrypt_data(str(data.get('insurance', ''))),
        status_encrypted=encrypt_data(str(data.get('status', ''))),
        description_encrypted=encrypt_data(str(data.get('description', ''))),
    ),
                    'doctor': Doctor(
        user_id=user_id,
        specialty_encrypted=encrypt_data(str(data.get('specialty', ''))),
        profile_image_encrypted=encrypt_data(str(data.get('profile_image', ''))),
        submission_date_encrypted=submission_date,
        license_number_encrypted=encrypt_data(str(data.get('license_number', ''))),
        license_document_encrypted=encrypt_data(str(data.get('license_document', ''))),
        degree_encrypted=encrypt_data(str(data.get('degree', ''))),
        status_encrypted=encrypt_data(str(data.get('status', ''))),
        description_encrypted=encrypt_data(str(data.get('description', ''))),
        hospital_id=data.get('hospital_id'),
    ),
                    'hospitalAdmin': HospitalAdmin(
        user_id=user_id,
        profile_image_encrypted=encrypt_data(str(data.get('profile_image', ''))),
        hospital_id_encrypted=encrypt_data(str(data.get('hospital_id', ''))),
        admin_id_encrypted=encrypt_data(str(data.get('admin_id', ''))),
        submission_date_encrypted=submission_date,
        qualifications_encrypted=encrypt_data(str(data.get('qualifications', ''))),
        department_encrypted=encrypt_data(str(data.get('department', ''))),
        access_level_encrypted=encrypt_data(str(data.get('access_level', 'basic'))),
        last_active_encrypted=submission_date,
        license_document_encrypted=encrypt_data(str(data.get('license_document', ''))),
        employment_verification_encrypted=encrypt_data(str(data.get('employment_verification', ''))),
        status_encrypted=encrypt_data(str(data.get('status', ''))),
        description_encrypted=encrypt_data(str(data.get('description', ''))),
        hospital_id=data.get('hospital_id'),
    ),
                    'hospital': Hospital(
        user_id=user_id,
        logo_encrypted=encrypt_data(str(data.get('logo', ''))),
        type_encrypted=encrypt_data(str(data.get('type', ''))),
        beds_encrypted=encrypt_data(str(data.get('beds', ''))),
        established_year_encrypted=encrypt_data(str(data.get('established', ''))),
        address_encrypted=encrypt_data(str(data.get('address', ''))),
        license_number_encrypted=encrypt_data(str(data.get('license_number', ''))),
        submission_date_encrypted=submission_date,
        license_document_encrypted=encrypt_data(str(data.get('license', ''))),
        accreditation_document_encrypted=encrypt_data(str(data.get('accreditation', ''))),
        operating_hours_encrypted=encrypt_data(str(data.get('operating_hours', ''))),
        emergency_services_encrypted=encrypt_data(str(data.get('emergency_services', ''))),
        medical_staff_encrypted=encrypt_data(str(data.get('medical_staff', ''))),
        status_encrypted=encrypt_data(str(data.get('status', ''))),
        description_encrypted=encrypt_data(str(data.get('description', ''))),
    ),
                    'pharmacy': Pharmacy(
        user_id=user_id,
        logo_encrypted=encrypt_data(str(data.get('logo', ''))),
        address_encrypted=encrypt_data(str(data.get('address', ''))),
        type_encrypted=encrypt_data(str(data.get('type', ''))),
        submission_date_encrypted=submission_date,
        license_number_encrypted=encrypt_data(str(data.get('license_number', ''))),
        established_year_encrypted=encrypt_data(str(data.get('established', ''))),
        prescriptions_filled_encrypted=encrypt_data(str(data.get('prescriptions_filled', '0'))),
        operating_hours_encrypted=encrypt_data(str(data.get('operating_hours', ''))),
        inventory_size_encrypted=encrypt_data(str(data.get('inventory_size', ''))),
        license_document_encrypted=encrypt_data(str(data.get('license', ''))),
        accreditation_document_encrypted=encrypt_data(str(data.get('accreditation', ''))),
        status_encrypted=encrypt_data(str(data.get('status', ''))),
        description_encrypted=encrypt_data(str(data.get('description', ''))),
    ),
                    'pharmacyAdmin': PharmacyAdmin(
        user_id=user_id,
        profile_image_encrypted=encrypt_data(str(data.get('profile_image', ''))),
        admin_id_encrypted=encrypt_data(str(data.get('admin_id', ''))),
        submission_date_encrypted=submission_date,
        access_level_encrypted=encrypt_data(str(data.get('access_level', 'basic'))),
        last_active_encrypted=submission_date,
        pharmacist_cert_encrypted=encrypt_data(str(data.get('pharmacist_cert', ''))),
        status_encrypted=encrypt_data(str(data.get('status', ''))),
        description_encrypted=encrypt_data(str(data.get('description', ''))),
        pharmacy_id=data.get('pharmacy_id'),
    ),
                    'pharmacist': Pharmacist(
        user_id=user_id,
        license_number_encrypted=encrypt_data(str(data.get('license_number', ''))),
        submission_date_encrypted=submission_date,
        profile_image_encrypted=encrypt_data(str(data.get('profile_image', ''))),
        pharmacist_cert_encrypted=encrypt_data(str(data.get('pharmacist_cert', ''))),
        status_encrypted=encrypt_data(str(data.get('status', ''))),
        description_encrypted=encrypt_data(str(data.get('description', ''))),
        pharmacy_id=data.get('pharmacy_id'),
    ),
                    'admin': Admin(
        user_id=user_id,
        profile_image_encrypted=encrypt_data(str(data.get('profile_image', ''))),
        security_level_encrypted=encrypt_data(str(data.get('security_level', 'standard'))),
        audit_access_encrypted=encrypt_data(str(data.get('audit_access', 'False'))),
        submission_date_encrypted=submission_date,
        status_encrypted=encrypt_data(str(data.get('status', ''))),
        description_encrypted=encrypt_data(str(data.get('description', ''))),
    )
                }
                
                current_app.logger.warning(f"Role models: {role_models[role]}")

                db.session.add(role_models[role])

            db.session.commit()

            try:
                AuditLog.log_async(
                    event='REGISTRATION_COMPLETE',
                    user=user_id,
                    ip=request.remote_addr,
                    user_agent=request.user_agent.string,
                    metadata={'role': role, 'source': 'web'}
                )
            except Exception as audit_error:
                current_app.logger.error(f"Audit log failed: {str(audit_error)}")

            current_app.logger.info(f"Successful registration for {user_id} as {role}")
                        
            return jsonify({
                "message": "Registration successful",
                "verified": False
            }), 201

        except IntegrityError as ie:
            db.session.rollback()
            current_app.logger.error(f"Integrity error: {str(ie)}", exc_info=True)
            return jsonify({"message": "Registration failed due to data conflict"}), 409
        except Exception as db_error:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(db_error)}", exc_info=True)
            return jsonify({"message": "Registration failed due to database error"}), 500

    except Exception as e:
        current_app.logger.critical(
            f"CRITICAL ERROR | IP: {request.remote_addr} | Error: {str(e)}",
            exc_info=True
        )
        return jsonify({"message": "An unexpected error occurred during registration"}), 500
    
@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute", key_func=rate_limit_key)
def login():
    current_app.logger.info(f"Login attempt from IP: {request.remote_addr}")
    
    try:
        csrf_token = request.headers.get('X-CSRF-TOKEN')
        if not csrf_token:
            current_app.logger.warning("Missing CSRF token")
            return jsonify({"message": "CSRF token required"}), 403
            
        if not validate_csrf_token(csrf_token):
            current_app.logger.warning("Invalid CSRF token")
            return jsonify({"message": "Invalid CSRF token"}), 403

        if not request.is_json:
            current_app.logger.error("Invalid content type")
            return jsonify({"message": "Content-Type must be application/json"}), 415

        data = request.get_json()
        if not data:
            current_app.logger.error("Invalid JSON payload")
            return jsonify({"message": "Invalid request format"}), 400

        email = bleach.clean(data.get('email', '')).strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            current_app.logger.warning("Missing credentials")
            return jsonify({"message": "Email and password required"}), 400

        email_hash = generate_email_hash(email)
        user = User.query.filter_by(email_hash=email_hash).first()

        model_mapping = {
            'hospital': Hospital,
            'pharmacy': Pharmacy,    
            'doctor': Doctor,
            'pharmacist': Pharmacist,
            'hospital_admin': HospitalAdmin,
            'pharmacy_admin': PharmacyAdmin,
            'patient': Patient,
            'admin': Admin
        }

        model = model_mapping.get(user.role)
        if not model:
            current_app.logger.warning(f"Invalid entity type: {user.role}")
            return jsonify({"message": "Invalid entity type"}), 400
        
        entity = model.query.filter_by(user_id=user.id).first()
        if not entity:
            current_app.logger.warning(f"Entity not found: {user.role} with ID {user.id}")
            return jsonify({"message": "Entity not found"}), 404
        
        if decrypt_data(entity.status_encrypted) != 'approved' or entity.verified != True:
            current_app.logger.warning(f"Inactive account: {user.role} with ID {user.id}")
            if decrypt_data(entity.status_encrypted) != 'approved':
                return jsonify({"message": "Account rejected description:"+decrypt_data(entity.description_encrypted)}), 403
            else:
                return jsonify({"message": "Account pending approval"}), 403

        if not user or not check_password_hash(user.password, password):
            current_app.logger.warning(f"Failed login attempt for {email}")
            time.sleep(random.uniform(0.5, 1.5))  
            
            AuditLog.log_async(
                event='FAILED_LOGIN',
                user=email,
                ip=request.remote_addr,
                user_agent=request.user_agent.string,
                metadata={
                    'reason': 'invalid_credentials',
                    'device_fingerprint': request.headers.get('X-Device-Fingerprint')
                }
            )
            return jsonify({"message": "Invalid credentials"}), 401

        if not user.account_verified:
            current_app.logger.warning(f"Unverified account login attempt: {email}")
            return jsonify({"message": "Account not verified"}), 403

        #if user.role == 'admin' or user.mfa_enabled:
            mfa_code = generate_cryptographic_code()
            mfa_key = f"mfa:{user.id}:{os.urandom(16).hex()}"  
            
            redis_client.setex(
                name=mfa_key,
                time=timedelta(minutes=5),
                value=json.dumps({
                    'code': mfa_code,
                    'ip': request.remote_addr,
                    'user_agent_hash': hashlib.sha256(request.user_agent.string.encode()).hexdigest(),
                    'timestamp': datetime.utcnow().isoformat(),
                    'auth_level': 'admin' if user.role == 'admin' else 'standard',
                    'device_id': request.headers.get('X-Device-ID', 'unknown')
                })
            )
            
            try:
                if user.role == 'admin':
                    send_admin_mfa_notification(
                        user=user,
                        code=mfa_code,
                        ip=request.remote_addr
                    )
                else:
                    send_mfa_code(
                        recipient=decrypt_data(user.email_encrypted),
                        code=mfa_code,
                        method=user.mfa_method  # email/sms/authenticator
                    )
                
                current_app.logger.info(f"MFA code sent to {email}")
                
                return jsonify({
                    "message": "MFA verification required",
                    "mfa_key": mfa_key.split(':')[-1],
                    "expires_in": 300,
                    "auth_level": "admin" if user.role == 'admin' else "standard"
                }), 202
                
            except Exception as e:
                current_app.logger.error(f"MFA delivery failed: {str(e)}")
                redis_client.delete(mfa_key)
                return jsonify({"message": "Failed to send verification code"}), 500

        expires_in = timedelta(hours=1)

        access_token = create_access_token(
           identity=user.id,  
           additional_claims={  
               "role": user.role,
               "auth_level": "full" if user.role == 'admin' else "standard"
           },
           expires_delta=expires_in  
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        user.last_login_at = datetime.utcnow()
        user.last_login_ip = request.remote_addr
        user.failed_login_attempts = 0  
        db.session.commit()

        response = jsonify({
            "message": "Login successful",
            'token': access_token,
            "user": {
                "id": user.id,
                "name": decrypt_data(user.name_encrypted),
                "email": email,
                "role": user.role,
                "mfa_enabled": user.mfa_enabled
            },
            "security": {
                "cookie_domains": current_app.config.get('JWT_COOKIE_DOMAIN'),
                "cookie_secure": True,
                "same_site": "Strict",
                "token_expiration": current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()
            }
        })
        
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        AuditLog.log_async(
            event='LOGIN_SUCCESS',
            user=user.id,
            ip=request.remote_addr,
            user_agent=request.user_agent.string,
            metadata={
                'login_method': 'password',
                'auth_level': 'admin' if user.role == 'admin' else 'standard',
                'device_fingerprint': request.headers.get('X-Device-Fingerprint')
            }
        )

        current_app.logger.info(f"Successful login for user {user.id}")
        return response, 200

    except Exception as e:
        current_app.logger.critical(
            f"Login Error - IP: {request.remote_addr} - Error: {str(e)}",
            exc_info=True
        )
        db.session.rollback()
        return jsonify({"message": "Internal server error"}), 500
       
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        response = jsonify({"message": "Logout successful"})
        unset_jwt_cookies(response)
        jti = get_jwt()['jti']
        db.session.add(TokenBlacklist(jti=jti))
        db.session.commit()
        
        AuditLog.log_event(
            event_type='LOGOUT',
            user_id=get_jwt_identity(),
            ip_address=request.remote_addr
        )
        
        return response, 200
    except Exception as e:
        current_app.logger.error(f"Logout Error: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500

@auth_bp.route('/request-password-reset', methods=['POST'])
@limiter.limit("3 per minute", key_func=rate_limit_key)
def request_password_reset():
    current_app.logger.info(f"Password reset request from IP: {request.remote_addr}")
    
    try:
        csrf_token = request.headers.get('X-CSRF-TOKEN')
        if not csrf_token:
            current_app.logger.warning("Missing CSRF token")
            return jsonify({"message": "CSRF token required"}), 403
            
        if not validate_csrf_token(csrf_token):
            current_app.logger.warning("Invalid CSRF token")
            return jsonify({"message": "Invalid CSRF token"}), 403

        if not request.is_json:
            current_app.logger.error("Invalid content type")
            return jsonify({"message": "Content-Type must be application/json"}), 415

        data = request.get_json()
        if not data:
            current_app.logger.error("Invalid JSON payload")
            return jsonify({"message": "Invalid request format"}), 400

        email = bleach.clean(data.get('email', '')).strip().lower()
        if not email:
            current_app.logger.warning("Missing email parameter")
            return jsonify({"message": "Email address required"}), 400

        rate_limit_key = f"pwd_reset:{email}"
        if redis_client.get(rate_limit_key):
            current_app.logger.warning(f"Too many reset requests for email: {email}")
            return jsonify({"message": "Too many reset attempts. Please wait."}), 429
        redis_client.setex(rate_limit_key, timedelta(minutes=5), "1")

        email_hash = generate_email_hash(email)
        user = User.query.filter_by(email_hash=email_hash).first()
        
        if not user:
            current_app.logger.info(f"Password reset request for unregistered email: {email}")
            return jsonify({
                "message": "If this email exists, a reset link has been sent",
                "cooldown": 300
            }), 200

        if not user.account_verified:
            current_app.logger.warning(f"Password reset for unverified account: {email}")
            return jsonify({"message": "Account not verified"}), 403

        verification_code = generate_cryptographic_code()
        challenge_hex = os.urandom(32).hex()
        redis_data = {
            'user_id': str(user.id),
            'code': verification_code,
            'ip': request.remote_addr,
            'user_agent': request.user_agent.string[:200],
            'created_at': datetime.utcnow().isoformat(),
            'attempts': 0,
            'device_fingerprint': request.headers.get('X-Device-Fingerprint', '')
        }

        try:
            if not redis_client.setex(
                name=challenge_hex,
                time=timedelta(minutes=15),
                value=encrypt_data(json.dumps(redis_data))
            ):
                raise RuntimeError("Failed to store reset token")
        except redis.exceptions.RedisError as e:
            current_app.logger.error(f"Redis error: {str(e)}")
            return jsonify({"message": "Temporary system error"}), 503

        try:
            send_code_email(email, code=verification_code)
            current_app.logger.info(f"Password reset code sent to {email}")
        except Exception as e:
            current_app.logger.error(f"Email sending failed: {str(e)}")
            redis_client.delete(f"pwd_reset:{challenge_hex}")
            return jsonify({"message": "Failed to send reset email"}), 500

        AuditLog.log_async(
            event='PASSWORD_RESET_REQUESTED',
            user=user.id,
            ip=request.remote_addr,
            user_agent=request.user_agent.string,
            metadata={
                'source': 'web',
                'device_fingerprint': redis_data['device_fingerprint'],
                'security': {
                    'ip_match': True,
                    'user_agent_match': True
                }
            }
        )

        response = jsonify({
            "message": "If this email exists, a reset link has been sent",
            "cooldown": 300,
            "redis_key": challenge_hex,
            "security": {
                "token_expiry": 900,  
                "max_attempts": 3
            }
        })
        
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        
        return response, 200

    except Exception as e:
        current_app.logger.critical(
            f"Password Reset Error - IP: {request.remote_addr} - Error: {str(e)}",
            exc_info=True
        )
        return jsonify({"message": "An error occurred during processing"}), 500
    
@auth_bp.route('/verify-reset-code', methods=['POST'])
@limiter.limit("3 per minute", key_func=rate_limit_key)
def verify_reset_code():
    current_app.logger.info(f"Password reset verification attempt from IP: {request.remote_addr}")
    
    try:
        csrf_token = request.headers.get('X-CSRF-TOKEN')
        if not csrf_token:
            current_app.logger.warning("Missing CSRF token")
            return jsonify({"message": "CSRF token required"}), 403
            
        if not validate_csrf_token(csrf_token):
            current_app.logger.warning("Invalid CSRF token")
            return jsonify({"message": "Invalid CSRF token"}), 403

        if not request.is_json:
            current_app.logger.error("Invalid content type")
            return jsonify({"message": "Content-Type must be application/json"}), 415

        data = request.get_json()
        if not data:
            current_app.logger.error("Invalid JSON payload")
            return jsonify({"message": "Invalid request format"}), 400

        redis_key = data.get('redis_key', '').strip()
        if not redis_key:
            current_app.logger.error("Missing redis_key parameter")
            return jsonify({"message": "Missing session identifier"}), 400
            
        verification_code = str(data.get('code', '')).strip()
        if not verification_code:
            current_app.logger.error("Missing verification code")
            return jsonify({"message": "Verification code required"}), 400

        encrypted_data = redis_client.get(redis_key)
        if not encrypted_data:
            current_app.logger.error(f"Invalid or expired reset token: {redis_key}")
            return jsonify({"message": "Invalid or expired session"}), 400

        try:
            redis_client.delete(redis_key)

            reset_data = json.loads(decrypt_data(encrypted_data))

            if reset_data.get('ip') != request.remote_addr:
                current_app.logger.warning(f"IP mismatch: {request.remote_addr} vs {reset_data.get('ip')}")
                return jsonify({"message": "Session validation failed"}), 403

            if reset_data.get('user_agent') != request.user_agent.string:
                current_app.logger.warning("User-Agent mismatch")
                return jsonify({"message": "Session validation failed"}), 403

            reset_data['attempts'] = reset_data.get('attempts', 0) + 1
            redis_client.setex(
                name=redis_key,
                time=timedelta(minutes=15),
                value=encrypt_data(json.dumps(reset_data))
            )

            if reset_data['attempts'] > 3:
                current_app.logger.warning(f"Too many attempts for reset token: {redis_key}")
                redis_client.delete(redis_key)
                return jsonify({"message": "Too many attempts. Please request a new code."}), 429

        except (ValueError, json.JSONDecodeError) as e:
            current_app.logger.error(f"JSON parse error: {str(e)}")
            return jsonify({"message": "Invalid session data"}), 400
        except Exception as e:
            current_app.logger.error(f"Decryption failed: {str(e)}")
            return jsonify({"message": "Security validation failed"}), 400

        if not hmac.compare_digest(str(reset_data['code']), verification_code):
            AuditLog.log_async(
                event='INVALID_PASSWORD_RESET_ATTEMPT',
                user=reset_data.get('user_id'),
                ip=request.remote_addr,
                user_agent=request.user_agent.string,
                metadata={
                    'provided_code': verification_code[-4:] + '...',
                    'attempt': reset_data['attempts'],
                    'device_fingerprint': reset_data.get('device_fingerprint')
                }
            )
            current_app.logger.warning(f"Code mismatch for reset token: {redis_key}")
            return jsonify({"message": "Invalid verification code"}), 400

        user = User.query.get(reset_data['user_id'])
        if not user:
            current_app.logger.error(f"User not found: {reset_data['user_id']}")
            return jsonify({"message": "User account not found"}), 404

        AuditLog.log_async(
            event='PASSWORD_RESET_CODE_VERIFIED',
            user=user.id,
            ip=request.remote_addr,
            user_agent=request.user_agent.string,
            metadata={
                'device_fingerprint': reset_data.get('device_fingerprint'),
                'security': {
                    'ip_match': True,
                    'user_agent_match': True
                }
            }
        )

        response = jsonify({
            "message": "Code verified successfully",
            "redis_key": redis_key,
            "expires_in": 600  
        })
        
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        
        return response, 200

    except Exception as e:
        current_app.logger.critical(
            f"Critical Error - IP: {request.remote_addr} - Error: {str(e)}",
            exc_info=True
        )
        return jsonify({"message": "An error occurred during processing"}), 500

@auth_bp.route('/reset-password', methods=['POST'])
@limiter.limit("3 per minute", key_func=rate_limit_key)
def reset_password():
    try:
        csrf_token = request.headers.get('X-CSRF-TOKEN')
        if not csrf_token or not validate_csrf_token(csrf_token):
            current_app.logger.warning("CSRF token validation failed")
            return jsonify({"message": "Invalid request"}), 403

        if not request.is_json:
            current_app.logger.error("Invalid content type")
            return jsonify({"message": "Invalid request format"}), 400

        data = request.get_json()
        
        required_fields = ['new_password', 'redis_key']
        if not all(field in data for field in required_fields):
            return jsonify({"message": "Missing required fields"}), 400

        new_password = bleach.clean(data['new_password']).strip()
        redis_key = bleach.clean(data['redis_key']).strip()

        if not redis_key:
            current_app.logger.error("Missing redis_key parameter")
            return jsonify({"message": "Missing registration ID"}), 400

        encrypted_data = redis_client.get(redis_key)
        if not encrypted_data:
            current_app.logger.error(f"Expired or invalid redis key: {redis_key}")
            return jsonify({"message": "Invalid or expired session"}), 400

        try:
            user_data = json.loads(decrypt_data(encrypted_data))
            current_app.logger.info(f"Decrypted user data: {user_data}")
        
            # Validate session consistency
            if user_data.get('ip') != request.remote_addr:
                current_app.logger.warning(f"IP mismatch: {request.remote_addr} vs {user_data.get('ip')}")
                return jsonify({"message": "Session validation failed"}), 403
        
            if user_data.get('user_agent') != request.user_agent.string:
                current_app.logger.warning("User-Agent mismatch")
                return jsonify({"message": "Session validation failed"}), 403
        
            if 'user_id' not in user_data:
                raise ValueError("Invalid user data structure")
        except Exception as e:
            current_app.logger.error(f"Decryption failure: {str(e)}")
            return jsonify({"message": "Security verification failed"}), 400

        user = User.query.get(user_data['user_id'])
        if not user:
            AuditLog.log_async(
                event='PASSWORD_RESET_FAILED',
                user=user_data['user_id'],
                ip=request.remote_addr,
                user_agent=request.user_agent.string
            )
            return jsonify({"message": "Account not found"}), 404

        if not validate_password_complexity(new_password):
            AuditLog.log_async(
                event='PASSWORD_VALIDATION_FAILED',
                user=user_data['user_id'],
                ip=request.remote_addr,
                user_agent=request.user_agent.string
            )
            return jsonify({"message": "Password does not meet security requirements"}), 400

        user.password = generate_password_hash(new_password)
        user.last_password_change = datetime.utcnow()
        db.session.commit()

        redis_client.delete(redis_key)
        redis_client.delete(f"login_block:{user.id}")  

        AuditLog.log_async(
            event='PASSWORD_RESET_SUCCESS',
            user=user_data['user_id'],
            ip=request.remote_addr,
            user_agent=request.user_agent.string
        )

        return jsonify({"message": "Password successfully updated"}), 200

    except Exception as e:
        current_app.logger.critical(f"Critical error in password reset: {str(e)}")
        db.session.rollback()
        return jsonify({"message": "Internal server error"}), 500

@auth_bp.route('/enable-mfa', methods=['POST'])
@jwt_required()
def enable_mfa():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.mfa_enabled:
            return jsonify({"message": "MFA zaten etkin"}), 400

        # Yeni MFA secret oluştur
        mfa_secret = generate_cryptographic_code(32)
        encrypted_secret = encrypt_data(mfa_secret)
        
        user.mfa_secret = encrypted_secret
        user.mfa_enabled = True
        db.session.commit()

        # QR kodu oluşturma URL'si
        qr_url = f"otpauth://totp/Medicare:{user.email}?secret={mfa_secret}&issuer=Medicare"
        
        return jsonify({
            "message": "MFA etkinleştirildi",
            "secret": mfa_secret,
            "qr_url": qr_url
        }), 200

    except Exception as e:
        current_app.logger.error(f"MFA Enable Error: {str(e)}")
        db.session.rollback()
        return jsonify({"message": "Internal server error"}), 500

@auth_bp.route('/disable-mfa', methods=['POST'])
@jwt_required()
def disable_mfa():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user.mfa_enabled:
            return jsonify({"message": "MFA zaten devre dışı"}), 400

        user.mfa_secret = None
        user.mfa_enabled = False
        db.session.commit()

        return jsonify({"message": "MFA devre dışı bırakıldı"}), 200

    except Exception as e:
        current_app.logger.error(f"MFA Disable Error: {str(e)}")
        db.session.rollback()
        return jsonify({"message": "Internal server error"}), 500

@auth_bp.route('/verify-mfa', methods=['POST'])
@jwt_required()
def verify_mfa():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        code = bleach.clean(data.get('code', ''))
        
        user = User.query.get(user_id)
        if not user.mfa_enabled:
            return jsonify({"message": "MFA etkin değil"}), 400

        current_time = int(time.time())
        valid_codes = pyotp.TOTP(user.mfa_secret).generate_otps(current_time-30, current_time+30)
        
        if not any(hmac.compare_digest(code, valid_code) for valid_code in valid_codes):
            AuditLog.log_event(
                event_type='INVALID_MFA_CODE',
                user_id=user.id,
                ip_address=request.remote_addr
            )
            return jsonify({"message": "Geçersiz MFA kodu"}), 400

        # Full erişim token'ı oluştur
        access_token = create_access_token(identity=user.id)
        response = jsonify({"message": "MFA doğrulaması başarılı"})
        set_access_cookies(response, access_token)
        
        return response, 200

    except Exception as e:
        current_app.logger.error(f"MFA Verification Error: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500

@auth_bp.route('/get-csrf-token', methods=['GET'])
def get_csrf_token():
    try:
        csrf_token = generate_secure_token()
        timestamp = int(datetime.now().timestamp())  
        
        token_data = {'token': csrf_token, 'timestamp': timestamp}
        
        s = URLSafeSerializer(current_app.secret_key)
        signed_token = s.dumps(token_data) 
        
        response = make_response(jsonify({'token': csrf_token}), 200)
        response.set_cookie(
            'XSRF-TOKEN',
            value=signed_token,
            secure=True,
            httponly=False,
            samesite='Strict'
        )
        return response
    except Exception as e:
        current_app.logger.error(f'CSRF token generation failed: {e}')
        return jsonify({'message': 'Failed to generate CSRF token'}), 500
