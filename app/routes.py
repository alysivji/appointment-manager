from flask import jsonify

from app import app


@app.route('/')
def index():
    return jsonify({'Hello': 'World'})
