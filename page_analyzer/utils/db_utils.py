from dotenv import dotenv_values
import psycopg2
from psycopg2 import extras

DATABASE_URL = dotenv_values('.env').get('DATABASE_URL')


def run_cursor(query_string: str):
    with psycopg2.connect(DATABASE_URL) as connection:
        cursor = connection.cursor(cursor_factory=extras.DictCursor)
        cursor.execute(query_string)
        return cursor
