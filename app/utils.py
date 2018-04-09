"""
Useful Utility Functions
"""

import json

from flask import abort, Response


def create_response(status_code=200, headers=None, data=None, error=None):
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


def getitem_or_404(model, model_id_field, id_to_search, error_text=None):
    """
    Helper function to search model for given id
    """
    item = model.query.filter(model_id_field == id_to_search).all()

    if len(item) == 0:
        response = create_response(status_code=404, error=error_text)
        return abort(response)

    return item[0]
