from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models import db, Doctor  # Assuming models.py contains the Doctor model
from flask_jwt_extended import jwt_required

doctors_bp = Blueprint('doctors', __name__)

@doctors_bp.route('/doctors', methods=['GET'])
@jwt_required()
def get_doctors():
    doctors = Doctor.query.all()
    return jsonify([doctor.to_dict() for doctor in doctors]), 200

@doctors_bp.route('/doctors', methods=['POST'])
@jwt_required()
def create_doctor():
    data = request.get_json()
    username = data.get('username')
    
    if Doctor.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_doctor = Doctor(
        name=data['name'],
        username=data['username'],
        password=hashed_password,
        gender=data['gender'],
        birthdate=data['birthdate'],
        work_start_time=data['work_start_time'],
        work_end_time=data['work_end_time']
    )
    db.session.add(new_doctor)
    db.session.commit()
    return jsonify(new_doctor.to_dict()), 201

@doctors_bp.route('/doctors/<int:id>', methods=['GET'])
@jwt_required()
def get_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    return jsonify(doctor.to_dict()), 200

@doctors_bp.route('/doctors/<int:id>', methods=['PUT'])
@jwt_required()
def update_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    data = request.get_json()
    
    if 'username' in data and Doctor.query.filter(Doctor.username == data['username'], Doctor.id != id).first():
        return jsonify({'message': 'Username already taken'}), 400
    
    doctor.name = data.get('name', doctor.name)
    doctor.username = data.get('username', doctor.username)
    doctor.gender = data.get('gender', doctor.gender)
    doctor.birthdate = data.get('birthdate', doctor.birthdate)
    doctor.work_start_time = data.get('work_start_time', doctor.work_start_time)
    doctor.work_end_time = data.get('work_end_time', doctor.work_end_time)
    
    if 'password' in data:
        doctor.password = generate_password_hash(data['password'], method='sha256')
    
    db.session.commit()
    return jsonify(doctor.to_dict()), 200

@doctors_bp.route('/doctors/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    db.session.delete(doctor)
    db.session.commit()
    return '', 204
