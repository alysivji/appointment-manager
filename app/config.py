import os

BASE_URL = ''


class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'you-will-never-guess')

    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 'postgresql://sivpack:sivpack_dev@db:5432/sivdev')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    KONCH_SHELL = 'ipy'
