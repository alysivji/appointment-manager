from flask_restful import Resource


class Appointment(Resource):
    def post(self):
        return {'hello': 'world'}
