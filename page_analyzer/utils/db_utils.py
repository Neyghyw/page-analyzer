import os

from dotenv import load_dotenv
import psycopg2
from psycopg2 import extras

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def run_cursor(query_string: str):
    with psycopg2.connect(DATABASE_URL) as connection:
        cursor = connection.cursor(cursor_factory=extras.DictCursor)
        cursor.execute(query_string)
        return cursor


def create_fields_and_values(_object: dict):
    columns = str.join(', ', [f'{key}' for key
                              in _object.keys()
                              if key])

    values = str.join(', ', [f"$${value}$$" for value
                             in _object.values()
                             if value])
    return columns, values


def handle_none_values(row):
    for key, value in row.items():
        if value is None:
            row[key] = ''
    return row
