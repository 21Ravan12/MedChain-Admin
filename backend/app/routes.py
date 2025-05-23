# backend/app/routes.py

from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "active", "message": "MedChain API çalışıyor!"}), 200
