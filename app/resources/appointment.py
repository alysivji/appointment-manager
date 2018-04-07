from flask import abort
from flask_restful import Resource


class AppointmentResource(Resource):
    def get(self):
        return abort(503, 'Service Unavailable')

    def post(self):
        return {'hello': 'world'}
