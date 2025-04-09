from threading import Thread
from datetime import datetime
from flask import current_app
from app import db
from sqlalchemy import event

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(255), nullable=False, default='patient')
    email_encrypted = db.Column(db.String(255), nullable=False, unique=True)
    email_hash = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password = db.Column(db.String(255), nullable=False)
    name_encrypted = db.Column(db.String(255))
    telephone_encrypted = db.Column(db.String(255))
    telephone_hash = db.Column(db.String(255), unique=True, index=True)
    mfa_enabled = db.Column(db.Boolean, default=False)
    last_password_change = db.Column(db.DateTime, default=datetime.utcnow)
    account_verified = db.Column(db.Boolean, default=False)

    patient = db.relationship('Patient', back_populates='user')
    doctor = db.relationship('Doctor', back_populates='user', cascade='all, delete-orphan', uselist=False)
    hospital_admin = db.relationship('HospitalAdmin', back_populates='user', cascade='all, delete-orphan', uselist=False)
    pharmacy_admin = db.relationship('PharmacyAdmin', back_populates='user', cascade='all, delete-orphan', uselist=False)
    pharmacist = db.relationship('Pharmacist', back_populates='user', cascade='all, delete-orphan', uselist=False)
    admin = db.relationship('Admin', back_populates='user', cascade='all, delete-orphan', uselist=False)

class Hospital(db.Model):
    __tablename__ = 'hospitals'
    user_id = db.Column(db.Integer, primary_key=True)
    logo_encrypted = db.Column(db.Text)
    type_encrypted = db.Column(db.String(255))
    beds_encrypted = db.Column(db.String(255))
    established_year_encrypted = db.Column(db.String(255))
    address_encrypted = db.Column(db.Text)
    license_number_encrypted = db.Column(db.String(255), unique=True)
    submission_date_encrypted = db.Column(db.Text)
    license_document_encrypted = db.Column(db.Text)
    accreditation_document_encrypted = db.Column(db.Text)
    operating_hours_encrypted = db.Column(db.Text)
    emergency_services_encrypted = db.Column(db.Text)
    medical_staff_encrypted = db.Column(db.Text)
    status_encrypted = db.Column(db.String(255))
    description_encrypted = db.Column(db.Text)
    verified = db.Column(db.Boolean, default=False, nullable=False)

    doctors = db.relationship('Doctor', back_populates='hospital')
    admins = db.relationship('HospitalAdmin', back_populates='hospital')

class Admin(db.Model):
    __tablename__ = 'admins'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    profile_image_encrypted = db.Column(db.Text)
    security_level_encrypted = db.Column(db.String(255)) 
    audit_access_encrypted = db.Column(db.Text)
    submission_date_encrypted = db.Column(db.Text)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    status_encrypted = db.Column(db.String(255))
    description_encrypted = db.Column(db.Text)
        
    user = db.relationship('User', back_populates='admin')

class HospitalAdmin(db.Model):
    __tablename__ = 'hospital_admins'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    profile_image_encrypted = db.Column(db.Text)
    hospital_id_encrypted = db.Column(db.String(255))
    admin_id_encrypted = db.Column(db.String(255))
    submission_date_encrypted = db.Column(db.Text)
    qualifications_encrypted = db.Column(db.Text)
    department_encrypted = db.Column(db.String(255))
    access_level_encrypted = db.Column(db.String(255))
    last_active_encrypted = db.Column(db.Text)
    license_document_encrypted = db.Column(db.Text)
    employment_verification_encrypted = db.Column(db.Text)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    status_encrypted = db.Column(db.String(255))
    description_encrypted = db.Column(db.Text)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.user_id'))
    
    user = db.relationship('User', back_populates='hospital_admin')
    hospital = db.relationship('Hospital', back_populates='admins')

class Pharmacy(db.Model):
    __tablename__ = 'pharmacies'
    user_id = db.Column(db.Integer, primary_key=True)
    logo_encrypted = db.Column(db.Text)
    address_encrypted = db.Column(db.Text)
    type_encrypted = db.Column(db.String(255))
    submission_date_encrypted = db.Column(db.Text)
    license_number_encrypted = db.Column(db.String(255), unique=True)
    established_year_encrypted = db.Column(db.String(255))
    prescriptions_filled_encrypted = db.Column(db.String(255))
    operating_hours_encrypted = db.Column(db.Text)
    inventory_size_encrypted = db.Column(db.String(255))
    license_document_encrypted = db.Column(db.Text)
    accreditation_document_encrypted = db.Column(db.Text)
    status_encrypted = db.Column(db.String(255))
    description_encrypted = db.Column(db.Text)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    
    admins = db.relationship('PharmacyAdmin', back_populates='pharmacy')
    pharmacists = db.relationship('Pharmacist', back_populates='pharmacy')

class PharmacyAdmin(db.Model):
    __tablename__ = 'pharmacy_admins'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    profile_image_encrypted = db.Column(db.Text)
    admin_id_encrypted = db.Column(db.String(255))
    submission_date_encrypted = db.Column(db.Text)
    access_level_encrypted = db.Column(db.String(255))
    last_active_encrypted = db.Column(db.Text)
    pharmacist_cert_encrypted = db.Column(db.Text)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    status_encrypted = db.Column(db.String(255))
    description_encrypted = db.Column(db.Text)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.user_id'))
    
    user = db.relationship('User', back_populates='pharmacy_admin')
    pharmacy = db.relationship('Pharmacy', back_populates='admins')

class Pharmacist(db.Model):
    __tablename__ = 'pharmacists'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    license_number_encrypted = db.Column(db.String(255), unique=True)
    profile_image_encrypted = db.Column(db.Text)
    submission_date_encrypted = db.Column(db.Text)
    pharmacist_cert_encrypted = db.Column(db.Text)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    status_encrypted = db.Column(db.String(255))
    description_encrypted = db.Column(db.Text)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.user_id'))
    
    user = db.relationship('User', back_populates='pharmacist')
    pharmacy = db.relationship('Pharmacy', back_populates='pharmacists')

class Patient(db.Model):
    __tablename__ = 'patients'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    birthyear_encrypted = db.Column(db.String(255))
    profile_image_encrypted = db.Column(db.Text)
    submission_date_encrypted = db.Column(db.Text)
    patient_id_encrypted = db.Column(db.String(255), unique=True)
    id_proof_encrypted = db.Column(db.Text)
    insurance_encrypted = db.Column(db.Text)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    status_encrypted = db.Column(db.String(255))
    description_encrypted = db.Column(db.Text)
    
    user = db.relationship('User', back_populates='patient')

class Doctor(db.Model):
    __tablename__ = 'doctors'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    specialty_encrypted = db.Column(db.String(255))
    profile_image_encrypted = db.Column(db.Text)
    submission_date_encrypted = db.Column(db.Text)
    license_number_encrypted = db.Column(db.String(255), unique=True)
    license_document_encrypted = db.Column(db.Text)
    degree_encrypted = db.Column(db.String(255))
    verified = db.Column(db.Boolean, default=False, nullable=False)
    status_encrypted = db.Column(db.String(255))
    description_encrypted = db.Column(db.Text)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.user_id'))
    
    user = db.relationship('User', back_populates='doctor')
    hospital = db.relationship('Hospital', back_populates='doctors')

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(100), nullable=False)
    user = db.Column(db.String(255))
    ip = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    log_metadata = db.Column(db.JSON)  
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def log_async(cls, **kwargs):
        kwargs['log_metadata'] = kwargs.pop('metadata', {})
        try:
            app = current_app._get_current_object()
            
            def log_in_app_context():
                with app.app_context():
                    log_entry = cls(**kwargs)
                    db.session.add(log_entry)
                    db.session.commit()

            Thread(target=log_in_app_context).start()
        except Exception as e:
            current_app.logger.error(f"AuditLog hatası: {str(e)}")

class TokenBlacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
