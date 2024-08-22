from flask import Blueprint, request, jsonify
from app.models import Employee
from app import db, bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    employee = Employee.query.filter_by(username=data['username']).first()

    if not employee or not bcrypt.check_password_hash(employee.password, data['password']):
        return jsonify({"message": "Invalid credentials"}), 401
    
    return jsonify({"message": "Login successful"}), 200
