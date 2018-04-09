"""
Useful Utility Functions
"""

import json

from flask import abort, Response


def create_response(data=None, headers=None, error=None, status_code=200):
    """
    Given data and error, create response
    """
    # format output
    output = {
        'data': data,
        'error': error,
    }

    # create response
    return Response(
        response=json.dumps(output),
        status=status_code,
        headers=headers,
        content_type='application/json',
    )


def getitem_or_404(model, model_id_field, id_to_search):
    """
    Helper function to search model for given id
    """
    item = model.query.filter(model_id_field == id_to_search).all()

    if len(item) == 0:
        return abort(404)

    return item[0]
