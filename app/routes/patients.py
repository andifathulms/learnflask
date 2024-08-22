from flask import Blueprint, request, jsonify
from models import db, Patient, Appointment  # Assuming models.py contains the Patient and Appointment models
from flask_jwt_extended import jwt_required
from google.cloud import bigquery
import os

patients_bp = Blueprint('patients', __name__)

# Setup BigQuery client
bq_client = bigquery.Client.from_service_account_json('path/to/your/credentials.json')
vaccine_table_id = 'delman-internal.delman_interview.vaccine_data'

def get_vaccine_data(no_ktp):
    query = f"""
        SELECT vaccine_type, COUNT(*) as vaccine_count
        FROM `{vaccine_table_id}`
        WHERE no_ktp = '{no_ktp}'
        GROUP BY vaccine_type
    """
    query_job = bq_client.query(query)
    results = query_job.result()
    
    if results.total_rows > 0:
        result = list(results)[0]
        return result['vaccine_type'], result['vaccine_count']
    return None, 0

@patients_bp.route('/patients', methods=['GET'])
@jwt_required()
def get_patients():
    patients = Patient.query.all()
    patients_list = []

    for patient in patients:
        vaccine_type, vaccine_count = get_vaccine_data(patient.no_ktp)
        patient_dict = patient.to_dict()
        patient_dict['vaccine_type'] = vaccine_type
        patient_dict['vaccine_count'] = vaccine_count
        patients_list.append(patient_dict)

    return jsonify(patients_list), 200

@patients_bp.route('/patients', methods=['POST'])
@jwt_required()
def create_patient():
    data = request.get_json()
    
    existing_patient = Patient.query.filter_by(no_ktp=data['no_ktp']).first()
    if existing_patient:
        return jsonify({'message': 'Patient with this KTP number already exists.'}), 400
    
    new_patient = Patient(
        name=data['name'],
        gender=data['gender'],
        birthdate=data['birthdate'],
        no_ktp=data['no_ktp'],
        address=data['address']
    )
    
    db.session.add(new_patient)
    db.session.commit()
    
    return jsonify(new_patient.to_dict()), 201

@patients_bp.route('/patients/<int:id>', methods=['GET'])
@jwt_required()
def get_patient(id):
    patient = Patient.query.get_or_404(id)
    
    vaccine_type, vaccine_count = get_vaccine_data(patient.no_ktp)
    appointments = Appointment.query.filter_by(patient_id=id).all()
    
    patient_dict = patient.to_dict()
    patient_dict['vaccine_type'] = vaccine_type
    patient_dict['vaccine_count'] = vaccine_count
    patient_dict['appointments'] = [appointment.to_dict() for appointment in appointments]

    return jsonify(patient_dict), 200

@patients_bp.route('/patients/<int:id>', methods=['PUT'])
@jwt_required()
def update_patient(id):
    patient = Patient.query.get_or_404(id)
    data = request.get_json()
    
    if 'name' in data:
        patient.name = data['name']
    if 'gender' in data:
        patient.gender = data['gender']
    if 'birthdate' in data:
        patient.birthdate = data['birthdate']
    if 'no_ktp' in data:
        existing_patient = Patient.query.filter_by(no_ktp=data['no_ktp']).first()
        if existing_patient and existing_patient.id != id:
            return jsonify({'message': 'Another patient with this KTP number already exists.'}), 400
        patient.no_ktp = data['no_ktp']
    if 'address' in data:
        patient.address = data['address']
    
    db.session.commit()
    
    return jsonify(patient.to_dict()), 200

@patients_bp.route('/patients/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_patient(id):
    patient = Patient.query.get_or_404(id)
    db.session.delete(patient)
    db.session.commit()
    return '', 204
