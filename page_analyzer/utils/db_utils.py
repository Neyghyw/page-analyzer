from dotenv import dotenv_values
import psycopg2
from psycopg2 import extras

DATABASE_URL = dotenv_values('.env').get('DATABASE_URL')


def run_cursor(query_string: str):
    with psycopg2.connect(DATABASE_URL) as connection:
        cursor = connection.cursor(cursor_factory=extras.DictCursor)
        cursor.execute(query_string)
        return cursor


def get_fields_and_values(parts):
    fields = str.join(', ', [f'{key}' for key
                             in parts.keys()
                             if key])

    values = str.join(', ', [f"'{value}'" for value
                             in parts.values()
                             if value])
    return fields, values
