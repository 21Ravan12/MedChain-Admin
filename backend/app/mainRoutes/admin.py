# auth.py (Tam Sürüm)
from datetime import datetime
import traceback
from flask import Blueprint, make_response, request, jsonify, current_app
from flask_jwt_extended import (
    jwt_required, 
    get_jwt_identity
)
from itsdangerous import URLSafeSerializer
from app import db, limiter
from app.models import Admin, Doctor, Hospital, HospitalAdmin, Patient, Pharmacist, Pharmacy, PharmacyAdmin, User
from app.utils import (
    generate_secure_token,
    rate_limit_key  # Ensure this is imported if it exists
)
from flask_wtf import CSRFProtect
from sqlalchemy.exc import SQLAlchemyError

from app.security import (
    encrypt_data,
    decrypt_data,
    hash_data,
    role_required,
    validate_csrf_token
)

csrf = CSRFProtect()

auth_ad = Blueprint('admin', __name__)

DEFAULT_LIMITS = "20 per minute; 500 per day"

@auth_ad.route('/profile', methods=['GET'])
@limiter.limit(DEFAULT_LIMITS, key_func=rate_limit_key)
@role_required('admin')
@jwt_required() 
def get_admin_profile():
    try:
        if request.content_type and request.content_type != 'application/json':
            current_app.logger.warning("Invalid content type")
            return jsonify({"message": "Content-Type must be application/json"}), 415

        admin_id = get_jwt_identity()
        adminUser = User.query.filter_by(id=admin_id).first()
        adminAdmin = Admin.query.filter_by(user_id=admin_id).first()

        if adminUser and adminAdmin:
            admin_profile = {
                "id": adminUser.id,
                "name": decrypt_data(adminUser.name_encrypted),
                "profile_image": decrypt_data(adminAdmin.profile_image_encrypted),
                "security_level": decrypt_data(adminAdmin.security_level_encrypted),
                "audit_access": decrypt_data(adminAdmin.audit_access_encrypted),
                "email": decrypt_data(adminUser.email_encrypted),
                "phone": decrypt_data(adminUser.telephone_encrypted),
            }
        else:
            current_app.logger.warning(f"Admin profile not found for ID: {admin_id}")
            return jsonify({"message": "Admin profile not found"}), 404

        response_data = {
            'admin_profile': admin_profile,
        }

        response = make_response(jsonify(response_data), 200)
        response.set_cookie(
            'XSRF-TOKEN',
            secure=True,
            httponly=False,
            samesite='Strict',
            max_age=3600  # 1 hour expiration
        )

        current_app.logger.info(f"Admin profile retrieved successfully for ID: {admin_id}")
        return response

    except Exception as e:
        current_app.logger.error(f"Admin profile retrieval failed: {e}")
        return jsonify({'message': 'Failed to retrieve admin profile'}), 500

@auth_ad.route('/dashboard-stats', methods=['GET'])
@limiter.limit(DEFAULT_LIMITS, key_func=rate_limit_key)
@role_required('admin')
@jwt_required() 
def dashboard_stats():
    try:
        if request.content_type and request.content_type != 'application/json':
            current_app.logger.warning("Invalid content type")
            return jsonify({"message": "Content-Type must be application/json"}), 415

        try:
            stats = {
                'approved_total': 0,
                'unverified_total': 0,
                'admins': {
                    'approved': 0,
                    'unverified': 0
                },
                'patients': {
                    'approved': 0,
                    'unverified': 0
                },
                'hospitals': {
                    'approved': 0,
                    'unverified': 0
                },
                'pharmacies': {
                    'approved': 0,
                    'unverified': 0
                },
                'doctors': {
                    'approved': 0,
                    'unverified': 0
                },
                'pharmacists': {
                    'approved': 0,
                    'unverified': 0
                },
                'hospital_admins': {
                    'approved': 0,
                    'unverified': 0
                },
                'pharmacy_admins': {
                    'approved': 0,
                    'unverified': 0
                },
            }
            
            # Admins
            unverified_admins = Admin.query.filter(
                (Admin.verified == False) | 
                (Admin.verified == None) 
            ).count()
            verified_admins = Admin.query.filter(Admin.verified == True).count()
            stats['admins']['unverified'] = unverified_admins
            stats['admins']['approved'] = verified_admins
            stats['unverified_total'] += unverified_admins
            stats['approved_total'] += verified_admins

            # Patients
            unverified_patients = Patient.query.filter(
                (Patient.verified == False) | 
                (Patient.verified == None) 
            ).count()
            verified_patients = Patient.query.filter(Patient.verified == True).count()
            stats['patients']['unverified'] = unverified_patients
            stats['patients']['approved'] = verified_patients
            stats['unverified_total'] += unverified_patients
            stats['approved_total'] += verified_patients

            # Hospitals
            unverified_hospitals = Hospital.query.filter(
                (Hospital.verified == False) | 
                (Hospital.verified == None) 
            ).count()
            verified_hospitals = Hospital.query.filter(Hospital.verified == True).count()
            stats['hospitals']['unverified'] = unverified_hospitals
            stats['hospitals']['approved'] = verified_hospitals
            stats['unverified_total'] += unverified_hospitals
            stats['approved_total'] += verified_hospitals
            
            # Pharmacies
            unverified_pharmacies = Pharmacy.query.filter(
                (Pharmacy.verified == False) | 
                (Pharmacy.verified == None) 
            ).count()
            verified_pharmacies = Pharmacy.query.filter(Pharmacy.verified == True).count()
            stats['pharmacies']['unverified'] = unverified_pharmacies
            stats['pharmacies']['approved'] = verified_pharmacies
            stats['unverified_total'] += unverified_pharmacies
            stats['approved_total'] += verified_pharmacies
            
            # Doctors
            unverified_doctors = Doctor.query.filter(
                (Doctor.verified == False) | 
                (Doctor.verified == None) 
            ).count()
            verified_doctors = Doctor.query.filter(Doctor.verified == True).count()
            stats['doctors']['unverified'] = unverified_doctors
            stats['doctors']['approved'] = verified_doctors
            stats['unverified_total'] += unverified_doctors
            stats['approved_total'] += verified_doctors
            
            # Pharmacists
            unverified_pharmacists = Pharmacist.query.filter(
                (Pharmacist.verified == False) | 
                (Pharmacist.verified == None) 
            ).count()
            verified_pharmacists = Pharmacist.query.filter(Pharmacist.verified == True).count()
            stats['pharmacists']['unverified'] = unverified_pharmacists
            stats['pharmacists']['approved'] = verified_pharmacists
            stats['unverified_total'] += unverified_pharmacists
            stats['approved_total'] += verified_pharmacists
            
            # Hospital Admins
            unverified_hospital_admins = HospitalAdmin.query.filter(
                (HospitalAdmin.verified == False) | 
                (HospitalAdmin.verified == None) 
            ).count()
            verified_hospital_admins = HospitalAdmin.query.filter(HospitalAdmin.verified == True).count()
            stats['hospital_admins']['unverified'] = unverified_hospital_admins
            stats['hospital_admins']['approved'] = verified_hospital_admins
            stats['unverified_total'] += unverified_hospital_admins
            stats['approved_total'] += verified_hospital_admins
            
            # Pharmacy Admins
            unverified_pharmacy_admins = PharmacyAdmin.query.filter(
                (PharmacyAdmin.verified == False) | 
                (PharmacyAdmin.verified == None) 
            ).count()
            verified_pharmacy_admins = PharmacyAdmin.query.filter(PharmacyAdmin.verified == True).count()
            stats['pharmacy_admins']['unverified'] = unverified_pharmacy_admins
            stats['pharmacy_admins']['approved'] = verified_pharmacy_admins
            stats['unverified_total'] += unverified_pharmacy_admins
            stats['approved_total'] += verified_pharmacy_admins
            
        except Exception as e:
            current_app.logger.error(f"Error counting entities: {e}")
            stats = {
                'error': 'Could not retrieve verification counts'
            }
         
        response_data = {
            'verification_stats': stats
        }
        
        response = make_response(jsonify(response_data), 200)
        response.set_cookie(
            'XSRF-TOKEN',
            secure=True,
            httponly=False,
            samesite='Strict',
            max_age=3600  # 1 hour expiration
        )
        
        return response
        
    except Exception as e:
        current_app.logger.error(f'Admin dashboard stats retrieval failed: {e}')
        return jsonify({'message': 'Failed to retrieve admin dashboard stats'}), 500

@auth_ad.route('/users', methods=['GET'])
@limiter.limit(DEFAULT_LIMITS, key_func=rate_limit_key)
@role_required('admin')
@jwt_required()
def get_all_users():
    current_app.logger.info(f"Get all users endpoint called by admin - IP: {request.remote_addr}")
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Define all user models with their role names
        USER_MODELS = {
            'hospital_admin': HospitalAdmin,
            'hospital': Hospital,
            'admin': Admin,
            'patient': Patient,
            'pharmacist': Pharmacist,
            'pharmacy': Pharmacy,
            'pharmacy_admin': PharmacyAdmin,
            'doctor': Doctor
        }

        approved_users = []
        
        # Get approved users from all tables in a single loop
        for role, model in USER_MODELS.items():
            users = model.query.filter(
                decrypt_data(model.status_encrypted) == "approved"
            ).all()
            approved_users.extend([{'id': user.user_id, 'role': role, 'model_instance': user} for user in users])
        
        # Get unique user IDs
        user_ids = list({user['id'] for user in approved_users})
        
        # Query base user information
        user_query = User.query.filter(User.id.in_(user_ids)).distinct()
        user_pagination = user_query.paginate(page=page, per_page=per_page, error_out=False)
        
        users_data = []
        for user in user_pagination.items:
            # Get all roles for this user
            user_roles = [u['role'] for u in approved_users if u['id'] == user.id]
            
            # Collect additional info for each role
            additional_info = {}
            for role in user_roles:
                # Find the model instance for this user and role
                model_instance = next(
                    (u['model_instance'] for u in approved_users 
                     if u['id'] == user.id and u['role'] == role),
                    None
                )
                
                if model_instance:
                    role_info = {}
                    # Dynamically get all encrypted fields
                    for field in model_instance.__table__.columns:
                        if field.name.endswith('_encrypted'):
                            plain_field = field.name.replace('_encrypted', '')
                            role_info[plain_field] = decrypt_data(getattr(model_instance, field.name))
                    
                    additional_info[role] = role_info
            
            user_data = {
                'id': user.id,
                "name": decrypt_data(user.name_encrypted),
                "phone": decrypt_data(user.telephone_encrypted),
                "email": decrypt_data(user.email_encrypted),
                'logo': decrypt_data(user.profile_image_encrypted) if decrypt_data(user.logo_encrypted) else None,
                'roles': user_roles,  # Now shows all roles user has
                'status': decrypt_data(user.status_encrypted),
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'additional_info': additional_info  # Includes info from all role tables
            }

            users_data.append(user_data)    
        
        csrf_token = generate_secure_token()
        timestamp = int(datetime.now().timestamp())  
        token_data = {'token': csrf_token, 'timestamp': timestamp}
        s = URLSafeSerializer(current_app.secret_key)
        signed_token = s.dumps(token_data)
        
        response_data = {
            'data': users_data,
            'pagination': {
                'total': user_pagination.total,
                'pages': user_pagination.pages,
                'current_page': page,
                'per_page': per_page
            },
            'token': csrf_token
        }
        
        response = make_response(jsonify(response_data), 200)
        response.set_cookie(
            'XSRF-TOKEN',
            value=signed_token,
            secure=True,
            httponly=False,
            samesite='Strict',
            max_age=3600  # 1 hour expiration
        )
        
        return response
        
    except Exception as e:
        current_app.logger.error(f'Failed to fetch users: {e}')
        return jsonify({'message': 'Failed to retrieve users', 'error': str(e)}), 500
      
@auth_ad.route('/approve', methods=['POST'])
@limiter.limit(DEFAULT_LIMITS, key_func=rate_limit_key)
@role_required('admin')
@jwt_required() 
def approve():
    try:
        if request.content_type and request.content_type != 'application/json':
            current_app.logger.warning("Invalid content type")
            return jsonify({"message": "Content-Type must be application/json"}), 415

        data = request.get_json()
        if not data:
            current_app.logger.warning("No JSON data provided")
            return jsonify({"message": "No data provided"}), 400

        entity_type = data.get('entity_type')
        entity_id = data.get('entity_id')
        status = data.get('status', 'approved')  # Default to 'approved' if not provided
        description = data.get('description', '')

        if not entity_type or not entity_id:
            current_app.logger.warning("Missing required fields")
            return jsonify({"message": "entity_type and entity_id are required"}), 400

        # Get admin info for logging
        admin_id = get_jwt_identity()
        admin = Admin.query.filter_by(user_id=admin_id).first()
        if not admin:
            current_app.logger.warning(f"Admin not found for ID: {admin_id}")
            return jsonify({"message": "Admin not found"}), 404

        # Define model mapping
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

        model = model_mapping.get(entity_type)
        if not model:
            current_app.logger.warning(f"Invalid entity type: {entity_type}")
            return jsonify({"message": "Invalid entity type"}), 400

        # Find the entity to approve
        entity = model.query.filter_by(user_id=entity_id).first()
        if not entity:
            current_app.logger.warning(f"Entity not found: {entity_type} with ID {entity_id}")
            return jsonify({"message": "Entity not found"}), 404

        # Update verification status and other fields
        try:
            entity.verified = True
            entity.status_encrypted = encrypt_data(status)
            if description:
                entity.description_encrypted = encrypt_data(description)
            
            db.session.commit()

            current_app.logger.info(
                f"Admin {admin_id} approved {entity_type} with ID {entity_id}. "
                f"New status: {status}"
            )

            return jsonify({
                "message": f"{entity_type.capitalize()} approved successfully",
                "verified": True,
                "status": status,
                "description": description if description else ""
            }), 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error approving entity: {str(e)}")
            return jsonify({"message": "Failed to approve entity"}), 500

    except Exception as e:
        current_app.logger.error(f'Approval failed: {e}')
        return jsonify({'message': 'Failed to process approval'}), 500

@auth_ad.route('/reject', methods=['POST'])
@limiter.limit(DEFAULT_LIMITS, key_func=rate_limit_key)
@role_required('admin')
@jwt_required() 
def reject():
    try:
        if request.content_type and request.content_type != 'application/json':
            current_app.logger.warning("Invalid content type")
            return jsonify({"message": "Content-Type must be application/json"}), 415

        data = request.get_json()
        if not data:
            current_app.logger.warning("No JSON data provided")
            return jsonify({"message": "No data provided"}), 400

        required_fields = ['entity_type', 'entity_id', 'status', 'description']
        for field in required_fields:
            if field not in data:
                current_app.logger.warning(f"Missing required field: {field}")
                return jsonify({"message": f"Missing required field: {field}"}), 400

        entity_type = data['entity_type']
        entity_id = data['entity_id']
        status = data['status']
        description = data['description']

        valid_entities = {
            'hospital': Hospital,
            'doctor': Doctor,
            'pharmacy': Pharmacy,
            'pharmacist': Pharmacist,
            'hospital_admin': HospitalAdmin,
            'pharmacy_admin': PharmacyAdmin,
            'patient': Patient,
            'admin': Admin
        }

        if entity_type not in valid_entities:
            current_app.logger.warning(f"Invalid entity type: {entity_type}")
            return jsonify({"message": "Invalid entity type"}), 400

        model_class = valid_entities[entity_type]

        entity = model_class.query.get(entity_id)
        if not entity:
            current_app.logger.warning(f"{entity_type} not found with ID: {entity_id}")
            return jsonify({"message": f"{entity_type} not found"}), 404

        try:
            entity.verified = True
            entity.status_encrypted = encrypt_data(status)
            entity.description_encrypted = encrypt_data(description)
            
            db.session.commit()
            
            current_app.logger.info(f"Successfully rejected {entity_type} with ID: {entity_id}")
            return jsonify({
                "message": f"{entity_type} rejected successfully",
                "entity_id": entity_id,
                "status": status,
                "description": description
            }), 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating {entity_type}: {str(e)}")
            return jsonify({"message": f"Failed to reject {entity_type}"}), 500

    except Exception as e:
        current_app.logger.error(f'Rejection failed: {str(e)}')
        return jsonify({'message': 'Failed to process rejection'}), 500

@auth_ad.route('/unverified-hospital', methods=['GET'])
@limiter.limit(DEFAULT_LIMITS, key_func=rate_limit_key)
@role_required('admin')
@jwt_required()
def unverified_hospital_users():
    current_app.logger.info(f"Unverified users endpoint called by admin - IP: {request.remote_addr}")
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # First get all unverified hospitals
        unverified_hospitals = Hospital.query.filter_by(verified=False).all()
        hospital_user_ids = [hospital.user_id for hospital in unverified_hospitals]

        user_query = User.query.filter(
            User.id.in_(hospital_user_ids),  # The hospital's user account
        ).distinct()

        user_pagination = user_query.paginate(page=page, per_page=per_page, error_out=False)
        
        users_data = []
        for user in user_pagination.items:
            # Find if the user is directly the hospital account
            is_hospital_account = user.id in hospital_user_ids
            hospital = next((h for h in unverified_hospitals if h.user_id == user.id), None)
            
            # Find hospital admin associations
            admin_hospitals = []
            if user.hospital_admin:
                admin_hospitals = [h for h in unverified_hospitals if h.user_id in [a.hospital_id for a in user.hospital_admin]]
            
            user_data = {
                'id': user.id,
                "name": decrypt_data(user.name_encrypted),
                "phone": decrypt_data(user.telephone_encrypted),
                "email": decrypt_data(user.email_encrypted),
                'role': user.role,
                'established': decrypt_data(hospital.established_year_encrypted) if hospital.established_year_encrypted else None,
                'address': decrypt_data(hospital.address_encrypted) if hospital.address_encrypted else None,
                'type': decrypt_data(hospital.type_encrypted) if hospital.type_encrypted else None,
                'beds': decrypt_data(hospital.beds_encrypted) if hospital.beds_encrypted else None,
                'license_number': decrypt_data(hospital.license_number_encrypted) if hospital.license_number_encrypted else None,
                'submission_date': decrypt_data(hospital.submission_date_encrypted) if hospital.submission_date_encrypted else None,
                'operating_hours': decrypt_data(hospital.operating_hours_encrypted) if hospital.operating_hours_encrypted else None,
                'logo': decrypt_data(hospital.logo_encrypted) if hospital.logo_encrypted else None,
                'medical_staff': decrypt_data(hospital.medical_staff_encrypted) if hospital.medical_staff_encrypted else None,
                'emergency_services': decrypt_data(hospital.emergency_services_encrypted) if hospital.emergency_services_encrypted else None,
                'documents': [
                    {
                        'license': decrypt_data(hospital.license_document_encrypted) if hospital.license_document_encrypted else None,
                        'accreditation': decrypt_data(hospital.accreditation_document_encrypted) if hospital.accreditation_document_encrypted else None,
                    }
                ],
            }

            users_data.append(user_data)    
        
        # Generate CSRF token for admin actions
        csrf_token = generate_secure_token()
        timestamp = int(datetime.now().timestamp())  
        token_data = {'token': csrf_token, 'timestamp': timestamp}
        s = URLSafeSerializer(current_app.secret_key)
        signed_token = s.dumps(token_data)
        
        response_data = {
            'data': users_data,
            'pagination': {
                'total': user_pagination.total,
                'pages': user_pagination.pages,
                'current_page': page,
                'per_page': per_page
            },
            'token': csrf_token
        }
        
        response = make_response(jsonify(response_data), 200)
        response.set_cookie(
            'XSRF-TOKEN',
            value=signed_token,
            secure=True,
            httponly=False,
            samesite='Strict',
            max_age=3600  # 1 hour expiration
        )
        
        return response
        
    except Exception as e:
        current_app.logger.error(f'Failed to fetch unverified users: {e}')
        return jsonify({'message': 'Failed to retrieve unverified users', 'error': str(e)}), 500

@auth_ad.route('/verified-hospital', methods=['GET'])
@limiter.limit(DEFAULT_LIMITS, key_func=rate_limit_key)
def verified_hospital():
    current_app.logger.info(f"Verified hospitals endpoint called by admin - IP: {request.remote_addr}")
    
    try:
        csrf_token = request.headers.get('X-CSRF-Token') or request.json.get('csrf_token')
        if not csrf_token:
            current_app.logger.warning("Missing CSRF token")
            return jsonify({"message": "CSRF token required"}), 403
            
        if not validate_csrf_token(csrf_token):
            current_app.logger.warning(f"Invalid CSRF token received: {csrf_token[:8]}...")
            return jsonify({"message": "Invalid CSRF token"}), 403

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Get all verified hospitals then filter by status
        all_verified = Hospital.query.filter(Hospital.verified == True).all()
        verified_hospitals = [
            h for h in all_verified 
            if h.status_encrypted and 
               decrypt_data(h.status_encrypted).lower().strip() == "approved"
        ]
        
        hospital_user_ids = [hospital.user_id for hospital in verified_hospitals]

        if not hospital_user_ids:
            return jsonify({
                'data': [],
                'pagination': {
                    'total': 0,
                    'pages': 0,
                    'current_page': page,
                    'per_page': per_page
                }
            }), 200

        user_query = User.query.filter(User.id.in_(hospital_user_ids))
        user_pagination = user_query.paginate(page=page, per_page=per_page, error_out=False)
        
        hospitals_data = []
        for user in user_pagination.items:
            hospital = next((h for h in verified_hospitals if h.user_id == user.id), None)
            
            if hospital:
                hospital_data = {
                    'id': user.id,
                    'status': decrypt_data(hospital.status_encrypted) if hospital.status_encrypted else None,
                    'name': decrypt_data(user.name_encrypted) if user.name_encrypted else None,
                }
                hospitals_data.append(hospital_data)
        
        response_data = {
            'data': hospitals_data,
            'pagination': {
                'total': user_pagination.total,
                'pages': user_pagination.pages,
                'current_page': page,
                'per_page': per_page
            }
        }
        
        return jsonify(response_data), 200  
         
    except Exception as e:
        current_app.logger.error(f'Failed to fetch verified hospitals: {e}')
        return jsonify({'message': 'Failed to retrieve verified hospitals', 'error': str(e)}), 500

@auth_ad.route('/unverified-admins', methods=['GET'])
@limiter.limit(DEFAULT_LIMITS, key_func=rate_limit_key)
@role_required('admin')
@jwt_required()
def unverified_admin():
    current_app.logger.info(f"Unverified admin endpoint called by admin - IP: {request.remote_addr}")
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        unverified_admins = Admin.query.filter_by(verified=False).all()
        admin_user_ids = [admin.user_id for admin in unverified_admins]

        user_query = User.query.filter(
            User.id.in_(admin_user_ids),  
        ).distinct()

        user_pagination = user_query.paginate(page=page, per_page=per_page, error_out=False)
        
        users_data = []
        for user in user_pagination.items:
            admin = next((p for p in unverified_admins if p.user_id == user.id), None)
            
            if not admin:
                continue
                
            user_data = {
                'id': user.id,
                "name": decrypt_data(user.name_encrypted),
                "phone": decrypt_data(user.telephone_encrypted),
                "email": decrypt_data(user.email_encrypted),
                'role': user.role,
                'submission_date': decrypt_data(admin.submission_date_encrypted) if admin.submission_date_encrypted else None,
                'profile_image': decrypt_data(admin.profile_image_encrypted) if admin.profile_image_encrypted else None,
                'security_level': decrypt_data(admin.security_level_encrypted) if admin.security_level_encrypted else None,
            }

            users_data.append(user_data)    
        
        csrf_token = generate_secure_token()
        timestamp = int(datetime.now().timestamp())  
        token_data = {'token': csrf_token, 'timestamp': timestamp}
        s = URLSafeSerializer(current_app.secret_key)
        signed_token = s.dumps(token_data)
        
        response_data = {
            'data': users_data,
            'pagination': {
                'total': user_pagination.total,
                'pages': user_pagination.pages,
                'current_page': page,
                'per_page': per_page
            },
            'token': csrf_token
        }
        
        response = make_response(jsonify(response_data), 200)
        response.set_cookie(
            'XSRF-TOKEN',
            value=signed_token,
            secure=True,
            httponly=False,
            samesite='Strict',
            max_age=3600  # 1 hour expiration
        )
        
        return response
        
    except Exception as e:
        current_app.logger.error(f'Failed to fetch unverified pharmacies: {e}')
        return jsonify({'message': 'Failed to retrieve unverified pharmacies', 'error': str(e)}), 500

@auth_ad.route('/unverified-hospital-admin', methods=['GET'])
@limiter.limit(DEFAULT_LIMITS, key_func=rate_limit_key)
@role_required('admin')
@jwt_required()
def verified_hospital_admin():
    current_app.logger.info(f"Unverified hospital admin endpoint called by admin - IP: {request.remote_addr}")
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        unverified_hospital_admin = HospitalAdmin.query.filter_by(verified=False).all()
        hospital_admin_user_ids = [hospital_admin.user_id for hospital_admin in unverified_hospital_admin]

        user_query = User.query.filter(
            User.id.in_(hospital_admin_user_ids),  
        ).distinct()

        user_pagination = user_query.paginate(page=page, per_page=per_page, error_out=False)
        
        users_data = []
        for user in user_pagination.items:
            hospital_admin = next((p for p in unverified_hospital_admin if p.user_id == user.id), None)
            
            if not hospital_admin:
                continue
                
            user_data = {
                'id': user.id,
                "name": decrypt_data(user.name_encrypted),
                "phone": decrypt_data(user.telephone_encrypted),
                "email": decrypt_data(user.email_encrypted),
                'role': user.role,
                'submission_date': decrypt_data(hospital_admin.submission_date_encrypted) if hospital_admin.submission_date_encrypted else None,
                'profile_image': decrypt_data(hospital_admin.profile_image_encrypted) if hospital_admin.profile_image_encrypted else None,
                'employment_verification': decrypt_data(hospital_admin.employment_verification_encrypted) if hospital_admin.employment_verification_encrypted else None,
                'hospital_id': hospital_admin.hospital_id_encrypted,
                'admin_id': decrypt_data(hospital_admin.admin_id_encrypted) if hospital_admin.admin_id_encrypted else None,
                'documents': [
                    {
                        'license': decrypt_data(hospital_admin.license_document_encrypted) if hospital_admin.license_document_encrypted else None,
                    }
                ],
            }

            users_data.append(user_data)    
        
        csrf_token = generate_secure_token()
        timestamp = int(datetime.now().timestamp())  
        token_data = {'token': csrf_token, 'timestamp': timestamp}
        s = URLSafeSerializer(current_app.secret_key)
        signed_token = s.dumps(token_data)
        
        response_data = {
            'data': users_data,
            'pagination': {
                'total': user_pagination.total,
                'pages': user_pagination.pages,
                'current_page': page,
                'per_page': per_page
            },
            'token': csrf_token
        }
        
        response = make_response(jsonify(response_data), 200)
        response.set_cookie(
            'XSRF-TOKEN',
            value=signed_token,
            secure=True,
            httponly=False,
            samesite='Strict',
            max_age=3600  # 1 hour expiration
        )
        
        return response
        
    except Exception as e:
        current_app.logger.error(f'Failed to fetch unverified pharmacies: {e}')
        return jsonify({'message': 'Failed to retrieve unverified pharmacies', 'error': str(e)}), 500

@auth_ad.route('/unverified-pharmacy', methods=['GET'])
@limiter.limit(DEFAULT_LIMITS, key_func=rate_limit_key)
@role_required('admin')
@jwt_required()
def unverified_pharmacy():
    current_app.logger.info(f"Unverified pharmacy endpoint called by admin - IP: {request.remote_addr}")
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        unverified_pharmacies = Pharmacy.query.filter_by(verified=False).all()
        pharmacy_user_ids = [pharmacy.user_id for pharmacy in unverified_pharmacies]

        user_query = User.query.filter(
            User.id.in_(pharmacy_user_ids),  # The pharmacy's user account
        ).distinct()

        user_pagination = user_query.paginate(page=page, per_page=per_page, error_out=False)
        
        users_data = []
        for user in user_pagination.items:
            # Find the pharmacy associated with this user
            pharmacy = next((p for p in unverified_pharmacies if p.user_id == user.id), None)
            
            if not pharmacy:
                continue
                
            user_data = {
                'id': user.id,
                "name": decrypt_data(user.name_encrypted),
                "phone": decrypt_data(user.telephone_encrypted),
                "type": decrypt_data(pharmacy.type_encrypted) if pharmacy.type_encrypted else None,
                "email": decrypt_data(user.email_encrypted),
                'role': user.role,
                'established': decrypt_data(pharmacy.established_year_encrypted) if pharmacy.established_year_encrypted else None,
                'address': decrypt_data(pharmacy.address_encrypted) if pharmacy.address_encrypted else None,
                'license_number': decrypt_data(pharmacy.license_number_encrypted) if pharmacy.license_number_encrypted else None,
                'submission_date': decrypt_data(pharmacy.submission_date_encrypted) if pharmacy.submission_date_encrypted else None,
                'operating_hours': decrypt_data(pharmacy.operating_hours_encrypted) if pharmacy.operating_hours_encrypted else None,
                'logo': decrypt_data(pharmacy.logo_encrypted) if pharmacy.logo_encrypted else None,
                'documents': [
                    {
                        'license': decrypt_data(pharmacy.license_document_encrypted) if pharmacy.license_document_encrypted else None,
                        'accreditation': decrypt_data(pharmacy.accreditation_document_encrypted) if pharmacy.accreditation_document_encrypted else None,
                    }
                ],
            }

            users_data.append(user_data)    
        
        # Generate CSRF token for admin actions
        csrf_token = generate_secure_token()
        timestamp = int(datetime.now().timestamp())  
        token_data = {'token': csrf_token, 'timestamp': timestamp}
        s = URLSafeSerializer(current_app.secret_key)
        signed_token = s.dumps(token_data)
        
        response_data = {
            'data': users_data,
            'pagination': {
                'total': user_pagination.total,
                'pages': user_pagination.pages,
                'current_page': page,
                'per_page': per_page
            },
            'token': csrf_token
        }
        
        response = make_response(jsonify(response_data), 200)
        response.set_cookie(
            'XSRF-TOKEN',
            value=signed_token,
            secure=True,
            httponly=False,
            samesite='Strict',
            max_age=3600  # 1 hour expiration
        )
        
        return response
        
    except Exception as e:
        current_app.logger.error(f'Failed to fetch unverified pharmacies: {e}')
        return jsonify({'message': 'Failed to retrieve unverified pharmacies', 'error': str(e)}), 500
    
@auth_ad.route('/verified-pharmacy', methods=['GET'])
@limiter.limit(DEFAULT_LIMITS, key_func=rate_limit_key)
def verified_pharmacy():
    current_app.logger.info(f"Verified pharmacies endpoint called by admin - IP: {request.remote_addr}")
    
    try:
        csrf_token = request.headers.get('X-CSRF-Token') or request.json.get('csrf_token')
        if not csrf_token:
            current_app.logger.warning("Missing CSRF token")
            return jsonify({"message": "CSRF token required"}), 403
            
        if not validate_csrf_token(csrf_token):
            current_app.logger.warning(f"Invalid CSRF token received: {csrf_token[:8]}...")
            return jsonify({"message": "Invalid CSRF token"}), 403

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Get all verified pharmacies then filter by status
        all_verified = Pharmacy.query.filter(Pharmacy.verified == True).all()
        verified_pharmacies = [
            h for h in all_verified 
            if h.status_encrypted and 
               decrypt_data(h.status_encrypted).lower().strip() == "approved"
        ]
        
        pharmacies_user_ids = [pharmacy.user_id for pharmacy in verified_pharmacies]

        if not pharmacies_user_ids:
            return jsonify({
                'data': [],
                'pagination': {
                    'total': 0,
                    'pages': 0,
                    'current_page': page,
                    'per_page': per_page
                }
            }), 200

        user_query = User.query.filter(User.id.in_(pharmacies_user_ids))
        user_pagination = user_query.paginate(page=page, per_page=per_page, error_out=False)
        
        pharmacies_data = []
        for user in user_pagination.items:
            pharmacy = next((h for h in verified_pharmacies if h.user_id == user.id), None)
            
            if pharmacy:
                pharmacy_data = {
                    'id': user.id,
                    'status': decrypt_data(pharmacy.status_encrypted) if pharmacy.status_encrypted else None,
                    'name': decrypt_data(user.name_encrypted) if user.name_encrypted else None,
                }
                pharmacies_data.append(pharmacy_data)
        
        response_data = {
            'data': pharmacies_data,
            'pagination': {
                'total': user_pagination.total,
                'pages': user_pagination.pages,
                'current_page': page,
                'per_page': per_page
            }
        }
        
        return jsonify(response_data), 200  
         
    except Exception as e:
        current_app.logger.error(f'Failed to fetch verified hospitals: {e}')
        return jsonify({'message': 'Failed to retrieve verified hospitals', 'error': str(e)}), 500
  
@auth_ad.route('/unverified-pharmacy-admins', methods=['GET'])
@limiter.limit(DEFAULT_LIMITS, key_func=rate_limit_key)
@role_required('admin')
@jwt_required()
def unverified_pharmacy_admin():
    current_app.logger.info(f"Unverified pharmacy admins endpoint called by admin - IP: {request.remote_addr}")
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        unverified_pharmacy_admins = PharmacyAdmin.query.filter_by(verified=False).all()
        pharmacy_admin_user_ids = [pharmacy_admin.user_id for pharmacy_admin in unverified_pharmacy_admins]

        user_query = User.query.filter(
            User.id.in_(pharmacy_admin_user_ids),  
        ).distinct()

        user_pagination = user_query.paginate(page=page, per_page=per_page, error_out=False)
        
        users_data = []
        for user in user_pagination.items:
            pharmacy_admin = next((p for p in unverified_pharmacy_admins if p.user_id == user.id), None)
            
            if not pharmacy_admin:
                continue
                
            user_data = {
                'id': user.id,
                "name": decrypt_data(user.name_encrypted),
                "phone": decrypt_data(user.telephone_encrypted),
                "email": decrypt_data(user.email_encrypted),
                'role': user.role,
                'access_level': decrypt_data(pharmacy_admin.access_level_encrypted) if pharmacy_admin.access_level_encrypted else None,
                'submission_date': decrypt_data(pharmacy_admin.submission_date_encrypted) if pharmacy_admin.submission_date_encrypted else None,
                'profile_image': decrypt_data(pharmacy_admin.profile_image_encrypted) if pharmacy_admin.profile_image_encrypted else None,
                'pharmacy_id': pharmacy_admin.pharmacy_id,
                'admin_id': decrypt_data(pharmacy_admin.admin_id_encrypted) if pharmacy_admin.admin_id_encrypted else None,
                'documents': [
                    {
                        'pharmacist_cert': decrypt_data(pharmacy_admin.pharmacist_cert_encrypted) if pharmacy_admin.pharmacist_cert_encrypted else None,
                    }
                ],
            }

            users_data.append(user_data)    
        
        csrf_token = generate_secure_token()
        timestamp = int(datetime.now().timestamp())  
        token_data = {'token': csrf_token, 'timestamp': timestamp}
        s = URLSafeSerializer(current_app.secret_key)
        signed_token = s.dumps(token_data)
        
        response_data = {
            'data': users_data,
            'pagination': {
                'total': user_pagination.total,
                'pages': user_pagination.pages,
                'current_page': page,
                'per_page': per_page
            },
            'token': csrf_token
        }
        
        response = make_response(jsonify(response_data), 200)
        response.set_cookie(
            'XSRF-TOKEN',
            value=signed_token,
            secure=True,
            httponly=False,
            samesite='Strict',
            max_age=3600  # 1 hour expiration
        )
        
        return response
        
    except Exception as e:
        current_app.logger.error(f'Failed to fetch unverified pharmacies: {e}')
        return jsonify({'message': 'Failed to retrieve unverified pharmacies', 'error': str(e)}), 500
    
@auth_ad.route('/unverified-pharmacist', methods=['GET'])
@limiter.limit(DEFAULT_LIMITS, key_func=rate_limit_key)
@role_required('admin')
@jwt_required()
def unverified_pharmacist():
    current_app.logger.info(f"Unverified pharmacist endpoint called by admin - IP: {request.remote_addr}")
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        unverified_pharmacist = Pharmacist.query.filter_by(verified=False).all()
        pharmacist_user_ids = [pharmacist.user_id for pharmacist in unverified_pharmacist]

        user_query = User.query.filter(
            User.id.in_(pharmacist_user_ids),  
        ).distinct()

        user_pagination = user_query.paginate(page=page, per_page=per_page, error_out=False)
        
        users_data = []
        for user in user_pagination.items:
            pharmacist = next((p for p in unverified_pharmacist if p.user_id == user.id), None)
            
            if not pharmacist:
                continue
                
            user_data = {
                'id': user.id,
                "name": decrypt_data(user.name_encrypted),
                "phone": decrypt_data(user.telephone_encrypted),
                "email": decrypt_data(user.email_encrypted),
                'role': user.role,
                'submission_date': decrypt_data(pharmacist.submission_date_encrypted) if pharmacist.submission_date_encrypted else None,
                'profile_image': decrypt_data(pharmacist.profile_image_encrypted) if pharmacist.profile_image_encrypted else None,
                'license_number_encrypted': decrypt_data(pharmacist.license_number_encrypted) if pharmacist.license_number_encrypted else None,
                'pharmacy_id': pharmacist.pharmacy_id,
                'documents': [
                    {
                        'license': decrypt_data(pharmacist.pharmacist_cert_encrypted) if pharmacist.pharmacist_cert_encrypted else None,
                    }
                ],
            }

            users_data.append(user_data)    
        
        csrf_token = generate_secure_token()
        timestamp = int(datetime.now().timestamp())  
        token_data = {'token': csrf_token, 'timestamp': timestamp}
        s = URLSafeSerializer(current_app.secret_key)
        signed_token = s.dumps(token_data)
        
        response_data = {
            'data': users_data,
            'pagination': {
                'total': user_pagination.total,
                'pages': user_pagination.pages,
                'current_page': page,
                'per_page': per_page
            },
            'token': csrf_token
        }
        
        response = make_response(jsonify(response_data), 200)
        response.set_cookie(
            'XSRF-TOKEN',
            value=signed_token,
            secure=True,
            httponly=False,
            samesite='Strict',
            max_age=3600  # 1 hour expiration
        )
        
        return response
        
    except Exception as e:
        current_app.logger.error(f'Failed to fetch unverified pharmacies: {e}')
        return jsonify({'message': 'Failed to retrieve unverified pharmacies', 'error': str(e)}), 500
    
@auth_ad.route('/unverified-patient', methods=['GET'])
@limiter.limit(DEFAULT_LIMITS, key_func=rate_limit_key)
@role_required('admin')
@jwt_required()
def unverified_patient():
    current_app.logger.info(f"Unverified patient endpoint called by admin - IP: {request.remote_addr}")
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        unverified_patient = Patient.query.filter_by(verified=False).all()
        patient_user_ids = [patient.user_id for patient in unverified_patient]

        user_query = User.query.filter(
            User.id.in_(patient_user_ids),  
        ).distinct()

        user_pagination = user_query.paginate(page=page, per_page=per_page, error_out=False)
        
        users_data = []
        for user in user_pagination.items:
            patient = next((p for p in unverified_patient if p.user_id == user.id), None)
            
            if not patient:
                continue
                
            user_data = {
                'id': user.id,
                "name": decrypt_data(user.name_encrypted),
                "phone": decrypt_data(user.telephone_encrypted),
                "email": decrypt_data(user.email_encrypted),
                'role': user.role,
                'birthyear': decrypt_data(patient.birthyear_encrypted) if patient.birthyear_encrypted else None,
                'submission_date': decrypt_data(patient.submission_date_encrypted) if patient.submission_date_encrypted else None,
                'patient_id': decrypt_data(patient.patient_id_encrypted) if patient.patient_id_encrypted else None,
                'id_proof': decrypt_data(patient.id_proof_encrypted) if patient.id_proof_encrypted else None,
                'insurance': decrypt_data(patient.insurance_encrypted) if patient.insurance_encrypted else None,
                'profile_image': decrypt_data(patient.profile_image_encrypted) if patient.profile_image_encrypted else None,
            }

            users_data.append(user_data)    
        
        csrf_token = generate_secure_token()
        timestamp = int(datetime.now().timestamp())  
        token_data = {'token': csrf_token, 'timestamp': timestamp}
        s = URLSafeSerializer(current_app.secret_key)
        signed_token = s.dumps(token_data)
        
        response_data = {
            'data': users_data,
            'pagination': {
                'total': user_pagination.total,
                'pages': user_pagination.pages,
                'current_page': page,
                'per_page': per_page
            },
            'token': csrf_token
        }
        
        response = make_response(jsonify(response_data), 200)
        response.set_cookie(
            'XSRF-TOKEN',
            value=signed_token,
            secure=True,
            httponly=False,
            samesite='Strict',
            max_age=3600  # 1 hour expiration
        )
        
        return response
        
    except Exception as e:
        current_app.logger.error(f'Failed to fetch unverified pharmacies: {e}')
        return jsonify({'message': 'Failed to retrieve unverified pharmacies', 'error': str(e)}), 500

@auth_ad.route('/unverified-doctor', methods=['GET'])
@limiter.limit(DEFAULT_LIMITS, key_func=rate_limit_key)
@role_required('admin')
@jwt_required()
def unverified_doctor():
    # Log request initiation
    current_app.logger.info(
        f"Unverified doctor endpoint called by admin - IP: {request.remote_addr}, "
        f"User-Agent: {request.user_agent}, "
        f"Headers: {dict(request.headers)}"
    )
    
    try:
        # Log pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        current_app.logger.debug(f"Pagination parameters - page: {page}, per_page: {per_page}")

        # Query unverified doctors
        current_app.logger.debug("Querying unverified doctors from database")
        unverified_doctor = Doctor.query.filter_by(verified=False).all()
        current_app.logger.debug(f"Found {len(unverified_doctor)} unverified doctors")
        
        doctor_user_ids = [doctor.user_id for doctor in unverified_doctor]
        current_app.logger.debug(f"Extracted user IDs: {doctor_user_ids}")

        # Query users
        current_app.logger.debug("Querying user data for unverified doctors")
        user_query = User.query.filter(
            User.id.in_(doctor_user_ids),  
        ).distinct()

        user_pagination = user_query.paginate(page=page, per_page=per_page, error_out=False)
        current_app.logger.debug(
            f"User pagination results - total: {user_pagination.total}, "
            f"pages: {user_pagination.pages}, "
            f"current page items: {len(user_pagination.items)}"
        )
        
        # Process user data
        users_data = []
        current_app.logger.debug("Processing user data and doctor details")
        
        for user in user_pagination.items:
            try:
                doctor = next((p for p in unverified_doctor if p.user_id == user.id), None)
                
                if not doctor:
                    current_app.logger.warning(f"No doctor record found for user ID: {user.id}")
                    continue
                    
                user_data = {
                    'id': user.id,
                    "name": decrypt_data(user.name_encrypted),
                    "phone": decrypt_data(user.telephone_encrypted),
                    "specialty": decrypt_data(doctor.specialty_encrypted) if doctor.specialty_encrypted else None,
                    "email": decrypt_data(user.email_encrypted),
                    'role': user.role,
                    'hospital_id': doctor.hospital_id,
                    'license_number': decrypt_data(doctor.license_number_encrypted) if doctor.license_number_encrypted else None,
                    'submission_date': doctor.submission_date_encrypted,
                    'degree': decrypt_data(doctor.degree_encrypted) if doctor.degree_encrypted else None,
                    'profile_image': decrypt_data(doctor.profile_image_encrypted) if doctor.profile_image_encrypted else None,
                    'documents': [
                        {
                            'license': decrypt_data(doctor.license_document_encrypted) if doctor.license_document_encrypted else None,
                        }
                    ],
                }
                users_data.append(user_data)
                
            except Exception as decryption_error:
                current_app.logger.error(
                    f"Error processing user ID {user.id}: {str(decryption_error)}",
                    exc_info=True,
                    extra={
                        'user_id': user.id,
                        'error_type': type(decryption_error).__name__
                    }
                )
                continue
        
        current_app.logger.debug("Generating CSRF token")
        csrf_token = generate_secure_token()
        timestamp = int(datetime.now().timestamp())  
        token_data = {'token': csrf_token, 'timestamp': timestamp}
        s = URLSafeSerializer(current_app.secret_key)
        signed_token = s.dumps(token_data)
        
        response_data = {
            'data': users_data,
            'pagination': {
                'total': user_pagination.total,
                'pages': user_pagination.pages,
                'current_page': page,
                'per_page': per_page
            },
            'token': csrf_token
        }
        
        response = make_response(jsonify(response_data), 200)
        response.set_cookie(
            'XSRF-TOKEN',
            value=signed_token,
            secure=True,
            httponly=False,
            samesite='Strict',
            max_age=3600  
        )
        
        current_app.logger.info(
            f"Successfully returned unverified doctors data. "
            f"Items returned: {len(users_data)}, "
            f"CSRF token generated: {csrf_token[:6]}..."
        )
        
        return response
        
    except SQLAlchemyError as db_error:
        current_app.logger.critical(
            "Database error fetching unverified doctors",
            exc_info=True,
            extra={
                'error_type': type(db_error).__name__,
                'error_details': str(db_error),
                'endpoint': '/unverified-doctor',
                'request_method': 'GET'
            }
        )
        return jsonify({
            'message': 'Database error while retrieving unverified doctors',
            'error': 'Database operation failed'
        }), 500
        
    except Exception as ser_error:  # Replace SerializationError with a generic Exception
        current_app.logger.error(
            "Token serialization error",
            exc_info=True,
            extra={
                'error_type': type(ser_error).__name__,
                'error_details': str(ser_error)
            }
        )
        return jsonify({
            'message': 'Security token generation failed',
            'error': 'Token processing error'
        }), 500
        
    except Exception as e:
        current_app.logger.error(
            'Unexpected error fetching unverified doctors',
            exc_info=True,
            extra={
                'error_type': type(e).__name__,
                'error_details': str(e),
                'stack_trace': traceback.format_exc(),
                'request_data': {
                    'args': dict(request.args),
                    'headers': dict(request.headers)
                }
            }
        )
        return jsonify({
            'message': 'Failed to retrieve unverified doctors',
            'error': 'Unexpected server error'
        }), 500