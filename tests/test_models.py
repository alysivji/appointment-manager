"""
Test creation of models
"""

from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Appointment, Patient, Provider


def test_create_patient():
    """
    Test creating a patient
    """
    # Arrange
    p = Patient(first_name="Aly", last_name="Sivji")

    # Act
    db.session.add(p)
    db.session.commit()

    # Assert
    assert len(Patient.query.all()) == 1

    queried_patient = Patient.query.one()
    assert queried_patient.first_name == 'Aly'
    assert queried_patient.last_name == 'Sivji'

    db.session.delete(p)
    db.session.commit()


def test_create_provider():
    """
    Test creating a provider
    """
    # Arrange
    p = Provider(first_name="Doctor", last_name="Acula")

    # Act
    db.session.add(p)
    db.session.commit()

    # Assert
    assert len(Provider.query.all()) == 1

    queried_provider = Provider.query.one()
    assert queried_provider.first_name == 'Doctor'
    assert queried_provider.last_name == 'Acula'

    db.session.delete(p)
    db.session.commit()


def test_create_appointment():
    """
    Test creating an appointment with a patient and a provider
    """
    # Arrange
    patient = Patient(first_name="Aly", last_name="Sivji")
    provider = Provider(first_name="Doctor", last_name="Acula")
    now = datetime.now()
    a = Appointment(start=now, end=now, department='foo',
                    patient=patient, provider=provider)

    # Act
    db.session.add(a)
    db.session.commit()

    # Assert
    assert len(Appointment.query.all()) == 1

    queried_appointment = Appointment.query.one()
    assert queried_appointment.department == 'foo'
    assert queried_appointment.patient_id == patient.id
    assert queried_appointment.provider_id == provider.id

    db.session.delete(a)
    db.session.delete(patient)
    db.session.delete(provider)
    db.session.commit()


def test_create_invalid_appointment_missing_patient():
    """
    Test creating an appointment with a provider and no patient
    """
    # Arrange
    provider = Provider(first_name="Doctor", last_name="Acula")
    now = datetime.now()
    a = Appointment(start=now, end=now, department='foo', provider=provider)

    # Act
    db.session.add(a)

    # Assert
    with pytest.raises(IntegrityError):
        db.session.commit()

    db.session.rollback()
    assert len(Appointment.query.all()) == 0


def test_create_invalid_appointment_missing_provider():
    """
    Test creating an appointment with a patient and no provider
    """
    # Arrange
    patient = Patient(first_name="Aly", last_name="Sivji")
    now = datetime.now()
    a = Appointment(start=now, end=now, department='foo', patient=patient)

    # Act
    db.session.add(a)

    # Assert
    with pytest.raises(IntegrityError):
        db.session.commit()

    db.session.rollback()
    assert len(Appointment.query.all()) == 0
