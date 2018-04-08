"""
Useful Utility Functions
"""

from flask import abort


def getitem_or_404(model, model_id_field, id_to_search):
    """
    Helper function to search model for given id
    """
    item = model.query.filter(model_id_field == id_to_search).all()

    if len(item) == 0:
        return abort(404)

    return item[0]
