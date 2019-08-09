import boto3
import os


def get_table():
    dynamodb = boto3.resource("dynamodb")
    table_name = os.environ['CONNECTIONS_TABLE_NAME']

    return dynamodb.Table(table_name)
