from app import db

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    work_start_time = db.Column(db.Time, nullable=False)
    work_end_time = db.Column(db.Time, nullable=False)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    no_ktp = db.Column(db.String(64), unique=True, nullable=False)
    address = db.Column(db.String(256), nullable=False)
    vaccine_type = db.Column(db.String(64))
    vaccine_count = db.Column(db.Integer)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('IN_QUEUE', 'DONE', 'CANCELLED', name='status_enum'), nullable=False, default='IN_QUEUE')
    diagnose = db.Column(db.Text, default='')
    notes = db.Column(db.Text, default='')

    patient = db.relationship('Patient', backref=db.backref('appointments', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('appointments', lazy=True))
