from flask import jsonify

from app import app, api
from app.resources.appointment import AppointmentResource
from app.resources.patient import PatientResource
from app.resources.provider import ProviderResource


@app.route('/')
def index():
    return jsonify({'index': 'page'})


api.add_resource(AppointmentResource, '/appointments')
api.add_resource(PatientResource, '/patients')
api.add_resource(ProviderResource, '/providers')
