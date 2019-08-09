import os
import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel('DEBUG')

dynamodb = boto3.resource("dynamodb")


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
    logger.warning("Connection request came in: event={}".format(event))
    connection_id = event['requestContext']['connectionId']

    on_connect(connection_id)
    return make_response(200, "connected")


def disconnect_handler(event, context):
    connection_id = event['requestContext']['connectionId']

    on_disconnect(connection_id)
    return make_response(200, "disconnected")


def default_handler(event, context):
    logger.warning("Unimplemented request came in: event={}".format(event))

    body = event['body']
    logger.info("Body for default request is {}".format(body))

    return make_response(200, "pong")


def on_connect(connection_id):
    table = get_connections_table()
    table.put_item(Item={"connectionId": connection_id})


def on_disconnect(connection_id):
    table = get_connections_table()
    table.delete_item(Key={"connectionId": connection_id})


def make_response(status_code, body):
    if not isinstance(body, str):
        body = json.dumps(body)

    return {"statusCode": status_code, "body": body}


def get_connections_table():
    table_name = os.environ['CONNECTIONS_TABLE_NAME']
    return dynamodb.Table(table_name)
