from google.cloud import bigquery
from app.models import Patient
from app import db
import os

def fetch_and_update_patient_data():
    credentials_path = os.path.join(os.path.dirname(__file__), '../../credentials/bigquery_credentials.json')
    client = bigquery.Client.from_service_account_json(credentials_path)
    
    query = """
    SELECT no_ktp, vaccine_type, vaccine_count
    FROM `delman-internal.delman_interview.vaccine_data`
    """
    query_job = client.query(query)
    results = query_job.result()

    for row in results:
        patient = Patient.query.filter_by(no_ktp=row.no_ktp).first()
        if patient:
            patient.vaccine_type = row.vaccine_type
            patient.vaccine_count = row.vaccine_count
            db.session.commit()
