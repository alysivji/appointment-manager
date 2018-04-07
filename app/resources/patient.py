from flask_restful import Resource
from webargs import fields
from webargs.flaskparser import use_args

from app import db, Patient
from app.config import BASE_URL
from app.schemas import PatientSchema


# Configure reading from requests
PATIENTS_SCHEMA_POST = {
  'first_name': fields.Str(locations='json', required=True),
  'last_name': fields.Str(locations='json', required=True),
}

# Configure serializing models to JSON for response
patient_list_schema = PatientSchema(many=True)
patient_schema = PatientSchema()


class PatientsResource(Resource):
    def get(self):
        all_patients = Patient.query.all()
        result = patient_list_schema.dump(all_patients)
        return result.data, 200

    @use_args(PATIENTS_SCHEMA_POST)
    def post(self, args):
        new_patient = Patient(first_name=args['first_name'],
                              last_name=args['last_name'])

        db.session.add(new_patient)
        db.session.commit()

        HEADERS = {
            'Location': f'{BASE_URL}/patients/{new_patient.id}',
        }

        return {}, 201, HEADERS


class PatientsItemResource(Resource):
    def get(self, patient_id):
        patient = Patient.query.filter(Patient.id == patient_id).all()
        if len(patient) == 0:
            return None, 404

        result = patient_schema.dump(patient[0])
        return result.data, 200

    def delete(self, patient_id):
        patient = Patient.query.filter(Patient.id == patient_id).all()
        if len(patient) == 0:
            return None, 404

        db.session.delete(patient[0])
        db.session.commit()
        return None, 204
