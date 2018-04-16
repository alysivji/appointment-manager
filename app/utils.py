"""
Useful Utility Functions
"""

from datetime import datetime
import json
import logging
from typing import Dict

from flask import abort, Response
import requests

from app import Webhook

logger = logging.getLogger(__name__)


def appointment_notification_webhook(notification_type: str, data: Dict) -> None:
    """
    Webhook that goes thru all active webhooks and sends notification if
    appointment has been created or updated.

    Being a prototype, I'm directly calling the endpoints which subscribed to
    the appointment_notification webhook. Also passing in data directly,
    should probably pass in a reference to the database just in case something
    changes.

    If this was going into production, it would make sense to use a task
    queue and message broker (RabbitMQ, SQS, PubSub, Kafka) to inform another
    process which would have workers go out and send notifications.

    Also discuss if we should include patient and provider information so the
    receiving API does not need to make another 2 round-trips to get that
    information. More requirement clarification
    """
    data_copy = dict(data)

    # Create dictionary that we will send to user
    output = {}
    output['data'] = data_copy
    output['authorization'] = 'Some user specific hash to verify sender'
    output['timestamp'] = datetime.utcnow()
    output['type'] = notification_type

    all_active_webhooks = Webhook.query.filter(Webhook.active == True).all()

    for webhook in all_active_webhooks:
        r = requests.post(webhook.endpoint_url, data=output)
        logger.info(f"{r.status_code} for {webhook.id}")


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
