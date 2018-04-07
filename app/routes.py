from flask import jsonify

from app import app, api
from app.resources.appointment import Appointment


@app.route('/')
def index():
    return jsonify({'index': 'page'})


api.add_resource(Appointment, '/appointments')
