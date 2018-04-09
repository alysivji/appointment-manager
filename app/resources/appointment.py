from datetime import datetime, timedelta
import json

from flask import abort
from flask_restful import Resource
from sqlalchemy import and_
from webargs import fields
from webargs.flaskparser import use_args
from werkzeug.exceptions import NotFound

from app import app, db, Appointment, Patient, Provider
from app.schemas import AppointmentSchema
from app.utils import create_response, getitem_or_404

###############
# Configuration
###############

BASE_URL = app.config.get('BASE_URL')
BOOKING_DELAY_IN_HOURS = app.config.get('BOOKING_DELAY_IN_HOURS')
MAX_APPT_LENGTH_IN_MINUTES = app.config.get('MAX_APPT_LENGTH_IN_MINUTES')

# Configure reading from requests
APPOINTMENT_SCHEMA_POST = {
    'start': fields.DateTime(required=True),
    'duration': fields.Int(required=True),  # in minutes
    'patient_id': fields.Int(required=True),
    'provider_id': fields.Int(required=True),
    'department': fields.Str(required=True),
}

APPOINTMENT_SCHEMA_GET = {
    'dt_gte': fields.DateTime(location='query'),
    'dt_lte': fields.DateTime(location='query'),
}

APPOINTMENT_SCHEMA_PATCH = {
    'start': fields.DateTime(),
    'duration': fields.Int(),  # in minutes
    'department': fields.Str(),
    'appointment_id': fields.Int(location='view_args', required=True),
}

# Configure serializing models to JSON for response
appointments_list_schema = AppointmentSchema(many=True)
appointment_schema = AppointmentSchema()


################
# Helper Methods
################

def _start_time_overlaps(provider_id_field, provider_id, start_time):
    """
    Given start time, find what appointments start time overlaps with

    If there is an overlap, let the user know about the conflict, else continue
    """
    appointments_start_time_interrupts = (
        Appointment.query
                   .filter(provider_id_field == provider_id)
                   .filter(and_(start_time >= Appointment.start,
                                start_time < Appointment.end))
                   .all())

    if len(appointments_start_time_interrupts):
        response = create_response(
            status_code=409,
            error='New appointment starts before already booked appointment ends.')
        abort(response)

def _end_time_overlaps(provider_id_field, provider_id, end_time):
    """
    Given start time, find what appointments start time overlaps with

    If there is an overlap, let the user know about the conflict, else continue
    """
    appointments_end_time_interrupts = (
        Appointment.query
                .filter(provider_id_field == provider_id)
                .filter(and_(end_time > Appointment.start,
                             end_time <= Appointment.end))
                .all())

    if len(appointments_end_time_interrupts):
        response = create_response(
            status_code=409,
            error='New appointment ends after already booked appointment starts.')
        abort(response)


###########
# Resources
###########

class AppointmentsResource(Resource):
    @use_args(APPOINTMENT_SCHEMA_GET)
    def get(self, args):
        # set up query
        all_appointments = Appointment.query

        # filter by query parameters as required
        if 'dt_lte' in args:
            all_appointments = all_appointments.filter(Appointment.start <= args['dt_lte'])
        if 'dt_gte' in args:
            all_appointments = all_appointments.filter(Appointment.end >= args['dt_gte'])

        # output query
        all_appointments = all_appointments.all()
        result = appointments_list_schema.dump(all_appointments)

        return result.data, 200

    @use_args(APPOINTMENT_SCHEMA_POST)
    def post(self, args):
        # does patient exist?
        patient = getitem_or_404(Patient, Patient.id, args['patient_id'], error_text="Patient not found")
        provider = getitem_or_404(Provider, Provider.id, args['provider_id'], error_text="Provider not found")

        # is timeslot in the future (given a delay)
        appt_start_time = args['start'].replace(tzinfo=None)
        booking_start = (
            datetime.now() + timedelta(hours=BOOKING_DELAY_IN_HOURS))

        if not appt_start_time >= booking_start:
            response = create_response(status_code=400, error='Appointment begin before booking window starts')
            return response

        # is appointment duration longer than allowed
        duration = args['duration']
        if duration > MAX_APPT_LENGTH_IN_MINUTES:
            response = create_response(status_code=400, error='Appointment length exceeds maximum allowed')
            return response

        appt_end_time = appt_start_time + timedelta(minutes=duration)

        # TODO check if patient is double booked (need clarification on requirements)

        _start_time_overlaps(Appointment.provider_id, provider.id, appt_start_time)
        _end_time_overlaps(Appointment.provider_id, provider.id, appt_end_time)

        # TODO is it during "Office Hours?" for this doctor (another lookup)
        is_office_hours = True
        if not is_office_hours:
            response = create_response(status_code=409, error='Office closed')
            return response

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

        return create_response(status_code=201, headers=HEADERS, data={})


class AppointmentsItemResource(Resource):
    # TODO refactor getitem_404 into function to prevent repeating code
    # talk about in code review

    def get(self, appointment_id):
        output = {
            'data': None,
            'error': None,
        }

        try:
            appointment = getitem_or_404(Appointment, Appointment.id, appointment_id)
        except NotFound:
            output['error'] = 'Appointment not found'
            return output, 404

        result = appointment_schema.dump(appointment)
        return result.data, 200

    def delete(self, appointment_id):
        output = {
            'data': None,
            'error': None,
        }

        try:
            appointment = getitem_or_404(Appointment, Appointment.id, appointment_id)
        except NotFound:
            output['error'] = 'Appointment not found'
            return output, 404

        db.session.delete(appointment)
        db.session.commit()
        return None, 204

    @use_args(APPOINTMENT_SCHEMA_PATCH, locations=('view_args', 'json'))
    def patch(self, args, appointment_id):
        """
        Can change the appointment start time, duration, and department.
        If you want to change provider and patient, delete and create new.
        """
        output = {
            'data': None,
            'error': None,
        }

        try:
            appointment = getitem_or_404(Appointment, Appointment.id, appointment_id)
        except NotFound:
            output['error'] = 'Appointment not found'
            return output, 404

        # if start time is entered, account for it
        if 'start' in args:
            appt_start_time = args['start'].replace(tzinfo=None)
        else:
            appt_start_time = appointment.start

        booking_start = (
            datetime.now() + timedelta(hours=BOOKING_DELAY_IN_HOURS))

        if not appt_start_time >= booking_start:
            output['error'] = 'Appointment begin before booking window starts'
            return output, 400

        # if duration is entered, account for it
        if 'duration' in args:
            duration = args['duration']
            appt_end_time = appt_start_time + timedelta(minutes=duration)
        else:
            appt_end_time = appointment.end

        # if department is entered
        if 'department' in args:
            department = args['department']
        else:
            department = appointment.department

        # TODO perform same checks we do when we create an appointment
        # given more time, I would refactor that out to create a new method

        appointment.start = appt_start_time
        appointment.end = appt_end_time
        appointment.department = department

        db.session.add(appointment)
        db.session.commit()

        return None, 200
