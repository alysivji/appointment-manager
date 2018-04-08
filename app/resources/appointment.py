from datetime import datetime, timedelta

from flask_restful import Resource
from sqlalchemy import and_
from webargs import fields
from webargs.flaskparser import use_args
from werkzeug.exceptions import NotFound

from app import app, db, Appointment, Patient, Provider
from app.schemas import AppointmentSchema
from app.utils import getitem_or_404

###############
# Configuration
###############

BASE_URL = app.config.get('BASE_URL')
BOOKING_DELAY_IN_HOURS = app.config.get('BOOKING_DELAY_IN_HOURS')
MAX_APPT_LENGTH_IN_MINUTES = app.config.get('MAX_APPT_LENGTH_IN_MINUTES')

# Configure reading from requests
APPOINTMENT_SCHEMA_POST = {
    'start': fields.DateTime(locations='json', required=True),
    'duration': fields.Int(locations='json', required=True),  # in minutes
    'patient_id': fields.Int(locations='json', required=True),
    'provider_id': fields.Int(locations='json', required=True),
    'department': fields.Str(locations='json', required=True),
}

# Configure serializing models to JSON for response
appointments_list_schema = AppointmentSchema(many=True)
appointment_schema = AppointmentSchema()


###########
# Resources
###########

class AppointmentsResource(Resource):
    def get(self):
        all_appointments = Appointment.query.all()
        result = appointments_list_schema.dump(all_appointments)
        return result.data, 200

    @use_args(APPOINTMENT_SCHEMA_POST)
    def post(self, args):
        output = {
            'data': None,
            'error': None,
        }

        # does patient exist?
        try:
            patient = getitem_or_404(Patient, Patient.id, args['patient_id'])
        except NotFound:
            output['error'] = 'Patient not found'
            return output, 404

        # does provider exist?
        try:
            provider = getitem_or_404(
                Provider, Provider.id, args['provider_id'])
        except NotFound:
            output['error'] = 'Provider not found'
            return output, 404

        # is timeslot in the future (given a delay)
        appt_start_time = args['start'].replace(tzinfo=None)
        booking_start = (
            datetime.now() + timedelta(hours=BOOKING_DELAY_IN_HOURS))

        if not appt_start_time >= booking_start:
            output['error'] = 'Appointment begin before booking window starts'
            return output, 400

        # is appointment duration longer than allowed
        appt_length = args['duration']
        if appt_length > MAX_APPT_LENGTH_IN_MINUTES:
            output['error'] = 'Appointment length exceeds maximum allowed'
            return output, 400

        appt_end_time = appt_start_time + timedelta(minutes=appt_length)

        # TODO check if patient is double booked

        # is the doctor already booked for this slot?
        appointments_start_time_interrupts = (
            Appointment.query
                       .filter(Appointment.provider_id == provider.id)
                       .filter(and_(appt_start_time >= Appointment.start,
                                    appt_start_time < Appointment.end))
                       .all())

        if len(appointments_start_time_interrupts):
            output['error'] = "New appointment starts before already booked appointment ends."
            return output, 409

        appointments_end_time_interrupts = (
            Appointment.query
                       .filter(Appointment.provider_id == provider.id)
                       .filter(and_(appt_end_time > Appointment.start,
                                    appt_end_time <= Appointment.end))
                       .all())

        if len(appointments_end_time_interrupts):
            output['error'] = "New appointment ends after already booked appointment starts."
            return output, 409

        # is it during "Office Hours?" for this doctor (another lookup)
        is_office_hours = True

        if not is_office_hours:
            output['error'] = 'Office closed'
            return output, 409

        new_appointment = Appointment(start=appt_start_time,
                                      end=appt_end_time,
                                      department=args['department'],
                                      patient=patient,
                                      provider=provider)

        db.session.add(new_appointment)
        db.session.commit()

        HEADERS = {
            'Location': f'{BASE_URL}/appointments/{new_appointment.id}',
        }

        # need to think about best way to implement a webhook
        # when it's created push it to a pubsub queue
        # can handle the webhook from there... since we don't have that
        # have a AppointmentNotifierWebhook

        return {}, 201, HEADERS


class AppointmentsItemResource(Resource):
    def get(self, appointment_id):
        appointment = Appointment.query.filter(Appointment.id == appointment_id).all()
        if len(appointment) == 0:
            return None, 404

        result = appointment_schema.dump(appointment[0])
        return result.data, 200

    def delete(self, appointment_id):
        appointment = Appointment.query.filter(Appointment.id == appointment_id).all()
        if len(appointment) == 0:
            return None, 404

        db.session.delete(appointment[0])
        db.session.commit()
        return None, 204
