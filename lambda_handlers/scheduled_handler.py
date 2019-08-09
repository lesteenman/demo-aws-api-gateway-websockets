import logging
import typing

from lib import connections_table

logger = logging.getLogger()
logger.setLevel('DEBUG')


def handle_trigger(event, context):
    logger.warning("===== TRIGGER! EVENT={}".format(event))

    pending_connections = find_pending_connections()
    logger.debug("Found the following pending connections: {}".format(pending_connections))

    respond_messages(pending_connections)


def find_pending_connections() -> typing.List:
    table = connections_table.get_table()

    scan_response = table.scan()

    pending_connections = []

    # TODO: Obviously deduplicate this.
    for connection in scan_response['Items']:
        logger.debug("Found connection: {}".format(connection))
        if len(connection['scheduledMessages']) > 0:
            logger.info("Connection {} has pending messages".format(connection['connectionId']))
            pending_connections.append(connection)

    while 'LastEvaluatedKey' in scan_response:
        # TODO: Obviously deduplicate this.
        for connection in scan_response['Items']:
            logger.debug("Found connection: {}".format(connection))
            if len(connection['scheduledMessages']) > 0:
                logger.info("Connection {} has pending messages".format(connection['connectionId']))
                pending_connections.append(connection)

        scan_response = table.scan(
            ExclusiveStartKey=scan_response['LastEvaluatedKey']
        )

    return pending_connections


def respond_messages(pending_connections: typing.List):
    for connection in pending_connections:
        connection_id = connection['connectionId']
        for message in connection['scheduledMessages']:
            logger.debug("-> Send {} to {}".format(message, connection_id))
