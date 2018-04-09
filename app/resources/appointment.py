from datetime import datetime, timedelta
import json
from typing import List

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
    'start': fields.DateTime(required=True),
    'duration': fields.Int(),  # in minutes
    'department': fields.Str()
}

# Configure serializing models to JSON for response
appointments_list_schema = AppointmentSchema(many=True)
appointment_schema = AppointmentSchema()


################
# Helper Methods
################

def _appointment_starts_before_booking_delay(appt_start, booking_start):
    """
    Some clinics might have rules regarding how far in advance appointments
    can be made

    If appointment is made before allowable time, inform of error
    """
    if not appt_start >= booking_start:
        error_text = 'Appointment begin before booking window starts'
        response = create_response(status_code=400, error=error_text)
        abort(response)

def _appointment_longer_than_max_length(duration):
    """
    If appointment duration longer than allowed, return a 400
    """
    if duration > MAX_APPT_LENGTH_IN_MINUTES:
        error_text = 'Appointment length exceeds maximum allowed'
        response = create_response(status_code=400, error=error_text)
        abort(response)

def _start_time_overlaps(provider_id_field, provider_id, start_time, allowed_overlap:List=[]):
    """
    Given start time, find what appointments start time overlaps with

    If there is an overlap that is not allowed, let the user know about the
    conflict, else continue
    """
    appointments_start_time_interrupts = (
        Appointment.query
                   .filter(provider_id_field == provider_id)
                   .filter(and_(start_time >= Appointment.start,
                                start_time < Appointment.end))
                   .all())

    for appointment in appointments_start_time_interrupts:
        if appointment.id not in allowed_overlap:
            response = create_response(
                status_code=409,
                error='New appointment starts before already booked appointment ends.')
            abort(response)

def _end_time_overlaps(provider_id_field, provider_id, end_time, allowed_overlap:List=[]):
    """
    Given start time, find what appointments start time overlaps with

    If there is an overlap that is not allowed, let the user know about the
    conflict, else continue
    """
    appointments_end_time_interrupts = (
        Appointment.query
                .filter(provider_id_field == provider_id)
                .filter(and_(end_time > Appointment.start,
                             end_time <= Appointment.end))
                .all())

    for appointment in appointments_end_time_interrupts:
        if appointment.id not in allowed_overlap:
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
        patient = getitem_or_404(Patient, Patient.id, args['patient_id'], error_text="Patient not found")
        provider = getitem_or_404(Provider, Provider.id, args['provider_id'], error_text="Provider not found")

        # is timeslot in the future (given a delay)
        appt_start_time = args['start'].replace(tzinfo=None)
        booking_start = datetime.now() + timedelta(hours=BOOKING_DELAY_IN_HOURS)
        _appointment_starts_before_booking_delay(appt_start_time, booking_start)

        # is appointment duration longer than allowed
        duration = args['duration']
        _appointment_longer_than_max_length(duration)

        # check if double booked
        appt_end_time = appt_start_time + timedelta(minutes=duration)
        # TODO should check if patient double book? need clarification
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

        # need to think about best way to implement a webhook
        # when it's created push it to a pubsub queue
        # can handle the webhook from there... since we don't have that
        # have a AppointmentNotifierWebhook

        HEADERS = {
            'Location': f'{BASE_URL}/appointments/{new_appointment.id}',
        }
        return create_response(status_code=201, headers=HEADERS, data={})


class AppointmentsItemResource(Resource):
    def get(self, appointment_id):
        appointment = getitem_or_404(Appointment, Appointment.id, appointment_id)
        result = appointment_schema.dump(appointment)
        return create_response(status_code=200, data=result.data)

    def delete(self, appointment_id):
        appointment = getitem_or_404(Appointment, Appointment.id, appointment_id)
        db.session.delete(appointment)
        db.session.commit()
        return create_response(status_code=204, data={})

    @use_args(APPOINTMENT_SCHEMA_PATCH)
    def patch(self, args, appointment_id):
        """
        Change the appointment start time, duration, and department.

        If you want to change provider and patient, delete and create new.
        """
        appointment = getitem_or_404(Appointment, Appointment.id, appointment_id)

        ##################
        # Handle Arguments
        ##################
        if 'duration' in args:
            duration = args['duration']
            appt_end_time = appt_start_time + timedelta(minutes=duration)
        else:
            appt_end_time = appointment.end
            duration = (appt_end_time - appointment.start).seconds // 60

        if 'start' in args:
            appt_start_time = args['start'].replace(tzinfo=None)
            appt_end_time = appt_start_time + timedelta(minutes=duration)
        else:
            appt_start_time = appointment.start

        if 'department' in args:
            department = args['department']
        else:
            department = appointment.department

        provider = appointment.provider
        patient = appointment.patient

        ####################
        # Check Restrictions
        ####################
        if appointment.start < datetime.utcnow():
            error_text = 'Cannot modify appointments in the past'
            response = create_response(status_code=400, error=error_text)
            return response

        booking_start = datetime.now() + timedelta(hours=BOOKING_DELAY_IN_HOURS)
        _appointment_starts_before_booking_delay(appt_start_time, booking_start)

        _appointment_longer_than_max_length(duration)

        _start_time_overlaps(Appointment.provider_id, provider.id,
                             appt_start_time, allowed_overlap=[appointment.id])
        _end_time_overlaps(Appointment.provider_id, provider.id, appt_end_time,
                           allowed_overlap=[appointment.id])

        ###############
        # Update record
        ###############
        appointment.start = appt_start_time
        appointment.end = appt_end_time
        appointment.department = department
        db.session.add(appointment)
        db.session.commit()

        # Send back result
        result = appointment_schema.dump(appointment)
        return create_response(status_code=200, data=result.data)
