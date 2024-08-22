from flask import Blueprint, request, jsonify
from models import db, Appointment, Doctor, Patient  # Assuming models.py contains the Appointment, Doctor, and Patient models
from flask_jwt_extended import jwt_required
from datetime import datetime

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    appointments = Appointment.query.all()
    return jsonify([appointment.to_dict() for appointment in appointments]), 200

@appointments_bp.route('/appointments', methods=['POST'])
@jwt_required()
def create_appointment():
    data = request.get_json()
    doctor = Doctor.query.get(data['doctor_id'])
    patient = Patient.query.get(data['patient_id'])
    
    if not doctor or not patient:
        return jsonify({'message': 'Doctor or Patient not found'}), 404
    
    appointment_datetime = datetime.fromisoformat(data['datetime'])
    
    if appointment_datetime.time() < doctor.work_start_time or appointment_datetime.time() > doctor.work_end_time:
        return jsonify({'message': 'Appointment time is outside doctor\'s working hours'}), 400
    
    # Check if the doctor is already booked at the given datetime
    existing_appointment = Appointment.query.filter_by(doctor_id=doctor.id, datetime=appointment_datetime).first()
    
    if existing_appointment:
        return jsonify({'message': 'Doctor is already booked at this time'}), 400
    
    new_appointment = Appointment(
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id'],
        datetime=appointment_datetime,
        status=data.get('status', 'IN_QUEUE'),
        diagnose=data.get('diagnose', ''),
        notes=data.get('notes', '')
    )
    
    db.session.add(new_appointment)
    db.session.commit()
    
    return jsonify(new_appointment.to_dict()), 201

@appointments_bp.route('/appointments/<int:id>', methods=['GET'])
@jwt_required()
def get_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    return jsonify(appointment.to_dict()), 200

@appointments_bp.route('/appointments/<int:id>', methods=['PUT'])
@jwt_required()
def update_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    data = request.get_json()
    
    doctor = Doctor.query.get(data['doctor_id'])
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404
    
    appointment_datetime = datetime.fromisoformat(data['datetime'])
    
    if appointment_datetime.time() < doctor.work_start_time or appointment_datetime.time() > doctor.work_end_time:
        return jsonify({'message': 'Appointment time is outside doctor\'s working hours'}), 400
    
    existing_appointment = Appointment.query.filter(Appointment.doctor_id == doctor.id,
                                                    Appointment.datetime == appointment_datetime,
                                                    Appointment.id != id).first()
    
    if existing_appointment:
        return jsonify({'message': 'Doctor is already booked at this time'}), 400
    
    appointment.patient_id = data['patient_id']
    appointment.doctor_id = data['doctor_id']
    appointment.datetime = appointment_datetime
    appointment.status = data.get('status', appointment.status)
    appointment.diagnose = data.get('diagnose', appointment.diagnose)
    appointment.notes = data.get('notes', appointment.notes)
    
    db.session.commit()
    
    return jsonify(appointment.to_dict()), 200

@appointments_bp.route('/appointments/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    db.session.delete(appointment)
    db.session.commit()
    return '', 204
