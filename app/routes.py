from flask import jsonify

from app import app, api
from app.resources.appointment import AppointmentResource
from app.resources.patient import PatientsResource, PatientsItemResource
from app.resources.provider import ProvidersResource, ProvidersItemResource


@app.route('/')
def index():
    return jsonify({'index': 'page'})


api.add_resource(AppointmentResource, '/appointments')

api.add_resource(PatientsResource, '/patients')
api.add_resource(PatientsItemResource, '/patients/<int:patient_id>')

api.add_resource(ProvidersResource, '/providers')
api.add_resource(ProvidersItemResource, '/providers/<int:provider_id>')
