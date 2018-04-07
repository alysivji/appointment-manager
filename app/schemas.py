from app import ma
from app.models import Appointment, Patient, Provider


class AppointmentSchema(ma.ModelSchema):
    class Meta:
        model = Appointment


class PatientSchema(ma.ModelSchema):
    class Meta:
        model = Patient


class ProviderSchema(ma.ModelSchema):
    class Meta:
        model = Provider
