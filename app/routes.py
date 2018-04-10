import logging

from flask import jsonify, request

from app import app, api
from app.resources.appointment import AppointmentsResource, AppointmentsItemResource
from app.resources.patient import PatientsResource, PatientsItemResource
from app.resources.provider import ProvidersResource, ProvidersItemResource

logger = logging.getLogger(__name__)


@app.route('/')
def index():
    return jsonify({'index': 'page'})


api.add_resource(AppointmentsResource, '/appointments')
api.add_resource(AppointmentsItemResource, '/appointments/<int:appointment_id>')

api.add_resource(PatientsResource, '/patients')
api.add_resource(PatientsItemResource, '/patients/<int:patient_id>')

api.add_resource(ProvidersResource, '/providers')
api.add_resource(ProvidersItemResource, '/providers/<int:provider_id>')


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
