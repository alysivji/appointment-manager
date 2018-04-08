import os


class Config(object):
    BOOKING_DELAY_IN_HOURS = os.getenv('BOOKING_DELAY', 24)
    MAX_APPT_LENGTH_IN_MINUTES = os.getenv('MAX_APPOINTMENT_LENGTH', 240)

    BASE_URL = ''

    SECRET_KEY = os.getenv('SECRET_KEY', 'you-will-never-guess')

    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 'postgresql://sivpack:sivpack_dev@db:5432/sivdev')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    KONCH_SHELL = 'ipy'
