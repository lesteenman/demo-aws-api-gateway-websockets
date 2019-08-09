import json
import logging

logger = logging.getLogger()
logger.setLevel('DEBUG')


def handle_gateway_request(event, context):
    request_context = event['requestContext']
    event_type = request_context['eventType']

    logger.debug("Event requestcontext: {}".format(request_context))
    logger.debug("Event connection_id: {}".format(request_context['connectionId']))
    logger.debug("Event type: {}".format(request_context['eventType']))

    if event_type == "CONNECT":
        return connect_handler(event, context)

    elif event_type == "DISCONNECT":
        return disconnect_handler(event, context)

    else:
        return default_handler(event, context)


def connect_handler(event, context):
    return response(200, "connected")


def disconnect_handler(event, context):
    return response(200, "disconnected")


def default_handler(event, context):
    return response(200, "pong")


def response(status_code, body):
    if not isinstance(body, str):
        body = json.dumps(body)

    return {"statusCode": status_code, "body": body}

