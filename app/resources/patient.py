from flask_restful import Resource
from webargs import fields
from webargs.flaskparser import use_args

from app import app, db, Patient
from app.schemas import PatientSchema
from app.utils import create_response, getitem_or_404

###############
# Configuration
###############

BASE_URL = app.config.get('BASE_URL')

# Configure reading from requests
PATIENTS_SCHEMA_POST = {
  'first_name': fields.Str(required=True),
  'last_name': fields.Str(required=True),
}

# Configure serializing models to JSON for response
patient_list_schema = PatientSchema(many=True)
patient_schema = PatientSchema()


###########
# Resources
###########

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

        return create_response(status_code=201, headers=HEADERS, data={})


class PatientsItemResource(Resource):
    def get(self, patient_id):
        patient = getitem_or_404(Patient, Patient.id, patient_id)
        result = patient_schema.dump(patient)
        return create_response(status_code=200, data=result.data)

    def delete(self, patient_id):
        patient = getitem_or_404(Patient, Patient.id, patient_id)
        db.session.delete(patient)
        db.session.commit()
        return create_response(status_code=204, data={})
