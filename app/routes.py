import logging

from flask import jsonify, request

from app import app, api
from app.resources.appointment import AppointmentsResource, AppointmentsItemResource
from app.resources.patient import PatientsResource, PatientsItemResource
from app.resources.provider import ProvidersResource, ProvidersItemResource

logger = logging.getLogger(__name__)

API_PREFIX = '/v1/'

@app.route('/')
def index():
    return jsonify({'index': 'page'})


api.add_resource(AppointmentsResource, f'{API_PREFIX}/appointments')
api.add_resource(AppointmentsItemResource, f'{API_PREFIX}/appointments/<int:appointment_id>')

api.add_resource(PatientsResource, f'{API_PREFIX}/patients')
api.add_resource(PatientsItemResource, f'{API_PREFIX}/patients/<int:patient_id>')

api.add_resource(ProvidersResource, f'{API_PREFIX}/providers')
api.add_resource(ProvidersItemResource, f'{API_PREFIX}/providers/<int:provider_id>')


###############################
# Notification Webhook Endpoint
###############################

@app.route('/receive_notifications', methods=['POST'])
def webhook_notification_receiver():
    """
    Endpoint to receive notifications. Aware of separation of concern issues

    Only putting it here as this is a prototype and want to show we recieved
    a POST request from a webhook
    """
    logger.info(request.values)
    return jsonify({'all': 'good'})
