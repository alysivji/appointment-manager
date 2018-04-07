from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from .config import Config

# create and config app
app = Flask(__name__)
app.config.from_object(Config)

# set up plugins
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)

from app import models, routes  # noqa
from .models import Appointment, Patient, Provider  # noqa

# set up flask konch (beefed up flask shell)
app.config.update({
    'KONCH_CONTEXT': {
        'db': db,
        'Appointment': Appointment,
        'Patient': Patient,
        'Provider': Provider,
    }
})
