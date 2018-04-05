from datetime import datetime

from . import db


class TimestampMixin(object):
    created = db.Column(db.DateTime, index=True,
                        nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)


class Patient(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    # Relationships
    appointments = db.relationship('Appointment', back_populates='patient')

    def __repr__(self):
        return f'<Patient {self.first_name} {self.last_name}>'


class Provider(TimestampMixin, db.Model):
    """
    Doctors can have specialities and be scheduled for appointments across
    departments (Eric Topol)
    """
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    # Relationships
    appointments = db.relationship('Appointment', back_populates='provider')

    def __repr__(self):
        return f'<Provider {self.first_name} {self.last_name}>'


class Appointment(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    patiend_id = db.Column(
        db.Integer, db.ForeignKey('patient.id'), nullable=False)
    provider_id = db.Column(
        db.Integer, db.ForeignKey('provider.id'), nullable=False)

    # Relationships
    patient = db.relationship('Patient', back_populates='appointments')
    provider = db.relationship('Provider', back_populates='appointments')

    def __repr__(self):
        return (
            f'<Appointment {self.patient} with {self.patient} @ {self.start}>')
