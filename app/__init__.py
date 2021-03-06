import logging.config

from flask import Flask
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from app.config import Config

# create and config app
app = Flask("app")
app.config.from_object(Config)

logging.config.dictConfig(app.config.get('LOGGING_CONFIG'))

# set up plugins
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)
ma = Marshmallow(app)

from .models import Appointment, Patient, Provider, Webhook  # noqa
from . import routes  # noqa

# set up flask konch (beefed up flask shell)
app.config.update({
    'KONCH_CONTEXT': {
        'db': db,
        'Appointment': Appointment,
        'Patient': Patient,
        'Provider': Provider,
        'Webhook': Webhook,
    }
})
