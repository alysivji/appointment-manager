from flask import Flask

from .config import Config

# create and config app
app = Flask(__name__)
app.config.from_object(Config)

# set up plugins


from app import routes  # noqa
