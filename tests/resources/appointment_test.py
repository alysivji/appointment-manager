"""
Testing appointments resource
"""

from datetime import datetime, timedelta
import json

import pytest

from app import app

BOOKING_DELAY_IN_HOURS = app.config.get('BOOKING_DELAY_IN_HOURS')
MAX_APPT_LENGTH_IN_MINUTES = app.config.get('MAX_APPT_LENGTH_IN_MINUTES')


@pytest.mark.freeze_time('2018-04-04T10:00:00.000000+00:00')
def test_create_appointment(client, single_patient, single_provider):
    """
    Create appointment like normal
    """
    body = {
        "start": "2018-04-05T10:00:00.000000+00:00",
        "duration": 60,
        "provider_id": single_provider,
        "patient_id": single_patient,
        "department": "radiology",
    }
    result = client.post('/appointments', data=body)
    assert result.status_code == 201

    appointment_id = int(result.headers['Location'].split('/')[-1])
    result = client.delete(f'/appointments/{appointment_id}')
    assert result.status_code == 204


@pytest.mark.freeze_time('2018-04-04T10:00:00.000000+00:00')
def test_create_appointment_before_booking_window_starts(client, single_patient, single_provider):
    """
    Do not allow the creation of an appointment before the specified window
    """
    right_now = datetime.utcnow()
    right_before_booking_window_opens = (
        right_now +
        timedelta(hours=BOOKING_DELAY_IN_HOURS) +
        timedelta(seconds=-5))

    body = {
        "start": right_before_booking_window_opens,
        "duration": 60,
        "provider_id": single_provider,
        "patient_id": single_patient,
        "department": "radiology",
    }
    result = client.post('/appointments', data=body)
    assert result.status_code == 400

    resp_body = json.loads(result.get_data(as_text=True))
    assert resp_body['error'] == 'Appointment begin before booking window starts'


@pytest.mark.freeze_time('2018-04-04T10:00:00.000000+00:00')
def test_create_appointment_with_nonexistent_provider(client, single_patient, single_provider):
    """
    Create appointment with provider that does not exist
    """
    body = {
        "start": "2018-04-05T10:00:00.000000+00:00",
        "duration": 60,
        "provider_id": single_provider + 100,
        "patient_id": single_patient,
        "department": "radiology",
    }
    result = client.post('/appointments', data=body)
    assert result.status_code == 404


@pytest.mark.freeze_time('2018-04-04T10:00:00.000000+00:00')
def test_create_appointment_with_nonexistent_patient(client, single_patient, single_provider):
    """
    Create appointment with patient that does not exist
    """
    body = {
        "start": "2018-04-05T10:00:00.000000+00:00",
        "duration": 60,
        "provider_id": single_provider,
        "patient_id": single_patient + 100,
        "department": "radiology",
    }
    result = client.post('/appointments', data=body)
    assert result.status_code == 404


@pytest.mark.freeze_time('2018-04-04T10:00:00.000000+00:00')
def test_create_appointment_exceeding_max_duration(client, single_patient, single_provider):
    """
    Create appointment with duration greater than max allowed
    """
    body = {
        "start": "2018-04-05T10:00:00.000000+00:00",
        "duration": MAX_APPT_LENGTH_IN_MINUTES + 1,
        "provider_id": single_provider,
        "patient_id": single_patient,
        "department": "radiology",
    }
    result = client.post('/appointments', data=body)
    assert result.status_code == 400

    resp_body = json.loads(result.get_data(as_text=True))
    assert resp_body['error'] == 'Appointment length exceeds maximum allowed'


@pytest.mark.freeze_time('2018-04-04T10:00:00.000000+00:00')
def test_create_appointment_that_starts_too_early(client, single_patient, single_provider):
    """
    Create appointment that starts before the previous appointment ends
    """
    # create first apopintment
    body = {
        "start": "2018-04-05T10:00:00.000000+00:00",
        "duration": 60,
        "provider_id": single_provider,
        "patient_id": single_patient,
        "department": "radiology",
    }
    result = client.post('/appointments', data=body)
    assert result.status_code == 201

    appointment_id = int(result.headers['Location'].split('/')[-1])

    # create second appointment
    body['start'] = "2018-04-05T10:59:00.000000+00:00"  # still 1 min left
    result = client.post('/appointments', data=body)
    assert result.status_code == 409

    resp_body = json.loads(result.get_data(as_text=True))
    assert resp_body['error'] == (
        "New appointment starts before already booked appointment ends.")

    result = client.delete(f'/appointments/{appointment_id}')
    assert result.status_code == 204


@pytest.mark.freeze_time('2018-04-04T10:00:00.000000+00:00')
def test_create_appointment_that_ends_too_late(client, single_patient, single_provider):
    """
    Create appointment that starts before the previous appointment ends
    """
    # create first apopintment
    body = {
        "start": "2018-04-05T11:00:00.000000+00:00",
        "duration": 60,
        "provider_id": single_provider,
        "patient_id": single_patient,
        "department": "radiology",
    }
    result = client.post('/appointments', data=body)
    assert result.status_code == 201

    appointment_id = int(result.headers['Location'].split('/')[-1])

    # create second appointment
    body['start'] = "2018-04-05T10:00:00.000000+00:00"
    body['duration'] = 61  # ends 1 minute too late

    result = client.post('/appointments', data=body)
    assert result.status_code == 409

    resp_body = json.loads(result.get_data(as_text=True))
    assert resp_body['error'] == (
        "New appointment ends after already booked appointment starts.")

    result = client.delete(f'/appointments/{appointment_id}')
    assert result.status_code == 204


@pytest.mark.freeze_time('2018-04-04T10:00:00.000000+00:00')
def test_create_two_appointments_with_no_conflicts(client, single_patient, single_provider):
    """
    Create appointment that starts before the previous appointment ends
    """
    # create first apopintment
    body = {
        "start": "2018-04-05T11:00:00.000000+00:00",
        "duration": 60,
        "provider_id": single_provider,
        "patient_id": single_patient,
        "department": "radiology",
    }
    result = client.post('/appointments', data=body)
    assert result.status_code == 201

    appointment_ids = []
    appointment_ids.append(int(result.headers['Location'].split('/')[-1]))

    # create second appointment
    body['start'] = "2018-04-05T10:00:00.000000+00:00"
    body['duration'] = 60

    result = client.post('/appointments', data=body)
    assert result.status_code == 201
    appointment_ids.append(int(result.headers['Location'].split('/')[-1]))

    for appointment_id in appointment_ids:
        result = client.delete(f'/appointments/{appointment_id}')
        assert result.status_code == 204


def test_modify_already_occured_appointment(
        client, freezer, single_patient, single_provider):
    """
    Create an appointment and try to modify it after it occurs
    """
    # Create first appointment
    freezer.move_to('2018-04-04T10:00:00.000000+00:00')
    body = {
        "start": "2018-04-05T10:00:00.000000+00:00",
        "duration": 60,
        "provider_id": single_provider,
        "patient_id": single_patient,
        "department": "radiology",
    }
    result = client.post('/appointments', data=body)
    assert result.status_code == 201
    appointment_id = int(result.headers['Location'].split('/')[-1])

    # Move a day in the future (after apopintment has started)
    freezer.move_to('2018-04-05T11:00:00.000000+00:00')

    # Try to modify first appointment
    body = {
        "start": "2018-04-06T13:00:00.000000+00:00"
    }
    result = client.patch(f'/appointments/{appointment_id}', data=body)

    assert result.status_code == 400

    resp_body = json.loads(result.get_data(as_text=True))
    assert resp_body['error'] == 'Cannot modify appointments in the past'

    result = client.delete(f'/appointments/{appointment_id}')
    assert result.status_code == 204


@pytest.mark.freeze_time('2018-04-04T10:00:00.000000+00:00')
def test_successful_appointment_modification(client, single_patient, single_provider):
    """
    Create an appointment and try to modify it after it occurs
    """
    # Create appointment
    body = {
        "start": "2018-04-30T10:00:00.000000+00:00",
        "duration": 60,
        "provider_id": single_provider,
        "patient_id": single_patient,
        "department": "radiology",
    }
    result = client.post('/appointments', data=body)
    assert result.status_code == 201
    appointment_id = int(result.headers['Location'].split('/')[-1])

    # Modify appointment start
    new_start_time = "2018-04-20T13:00:00+00:00"
    new_end_time = "2018-04-20T14:00:00+00:00"
    body = {
        "start": new_start_time
    }
    result = client.patch(f'/appointments/{appointment_id}', data=body)

    assert result.status_code == 200
    resp_body = json.loads(result.get_data(as_text=True))['data']
    assert resp_body['start'] == new_start_time
    assert resp_body['end'] == new_end_time
    assert resp_body['department'] == 'radiology'

    result = client.delete(f'/appointments/{appointment_id}')
    assert result.status_code == 204
