import logging

import boto3
from botocore.exceptions import ClientError

from lib import connections_table

logger = logging.getLogger()
logger.setLevel('DEBUG')

dynamodb = boto3.resource("dynamodb")


# One global entrypoint to keep the template as simple as possible.
def handle_gateway_request(event, context):
    event_type = event['requestContext']['eventType']

    if event_type == 'CONNECT':
        return handle_connect(event, context)
    elif event_type == 'DISCONNECT':
        return handle_disconnect(event, context)
    else:
        return handle_message(event, context)


# Handling of the $connect route
def handle_connect(event, context):
    connection_id = event['requestContext']['connectionId']

    return on_connect(connection_id)


def on_connect(connection_id):
    logger.info('Client connected (connectionId={})'.format(connection_id))

    table = connections_table.get_table()

    try:
        table.put_item(Item={"connectionId": connection_id, "scheduledMessages": []})
        return response(200, "connected")
    except ClientError as client_error:
        logger.error("Error adding connection to dynamodb table: {}".format(client_error))
        return response(500, "error connecting")


# Handling of the $disconnect route
def handle_disconnect(event, context):
    connection_id = event['requestContext']['connectionId']

    return on_disconnect(connection_id)


def on_disconnect(connection_id):
    logger.info('Client disconnected (connectionId={})'.format(connection_id))

    table = connections_table.get_table()

    try:
        table.delete_item(Key={"connectionId": connection_id})
        return response(200, "connected")

    except ClientError as client_error:
        logger.error("Error removing connection from dynamodb table: {}".format(client_error))
        return response(500, "error disconnecting")


# All other messages end up here, and are treated as messages to be scheduled.
def handle_message(event, context):
    connection_id = event['requestContext']['connectionId']
    table = connections_table.get_table()

    try:
        connection_query_response = table.get_item(Key={"connectionId": connection_id})
    except ClientError as client_error:
        logger.error("Something went wrong fetching the connection: {}".format(client_error))
        return response(500, "error while scheduling")

    connection = connection_query_response['Item']
    scheduled_messages = connection['scheduledMessages']

    new_message = event['body']

    scheduled_messages.append(new_message)

    try:
        table.update_item(
            Key={"connectionId": connection_id},
            UpdateExpression="set scheduledMessages = :messages",
            ExpressionAttributeValues={':messages': scheduled_messages}
        )
    except ClientError as client_error:
        logger.error("Something went wrong adding the new message: {}".format(client_error))
        return response(500, "error while scheduling")

    return response(200, "scheduled")


def response(status_code, body):
    return {"statusCode": 200, "body": body}
