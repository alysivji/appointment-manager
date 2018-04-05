from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .config import Config

# create and config app
app = Flask(__name__)
app.config.from_object(Config)

# set up plugins
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import models, routes  # noqa
from .models import Appointment, Patient, Provider  # noqa


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Appointment': Appointment,
        'Patient': Patient,
        'Provider': Provider,
    }
