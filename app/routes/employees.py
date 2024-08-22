from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Employee  # Assuming models.py contains the Employee model
from flask_jwt_extended import jwt_required

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/employees', methods=['GET'])
@jwt_required()
def get_employees():
    employees = Employee.query.all()
    return jsonify([employee.to_dict() for employee in employees]), 200

@employees_bp.route('/employees', methods=['POST'])
@jwt_required()
def create_employee():
    data = request.get_json()
    username = data.get('username')
    if Employee.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_employee = Employee(
        name=data['name'],
        username=data['username'],
        password=hashed_password,
        gender=data['gender'],
        birthdate=data['birthdate']
    )
    db.session.add(new_employee)
    db.session.commit()
    return jsonify(new_employee.to_dict()), 201

@employees_bp.route('/employees/<int:id>', methods=['GET'])
@jwt_required()
def get_employee(id):
    employee = Employee.query.get_or_404(id)
    return jsonify(employee.to_dict()), 200

@employees_bp.route('/employees/<int:id>', methods=['PUT'])
@jwt_required()
def update_employee(id):
    employee = Employee.query.get_or_404(id)
    data = request.get_json()
    
    if 'username' in data and Employee.query.filter(Employee.username == data['username'], Employee.id != id).first():
        return jsonify({'message': 'Username already taken'}), 400
    
    employee.name = data.get('name', employee.name)
    employee.username = data.get('username', employee.username)
    employee.gender = data.get('gender', employee.gender)
    employee.birthdate = data.get('birthdate', employee.birthdate)
    
    if 'password' in data:
        employee.password = generate_password_hash(data['password'], method='sha256')
    
    db.session.commit()
    return jsonify(employee.to_dict()), 200

@employees_bp.route('/employees/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    return '', 204
