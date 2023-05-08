import os

from dotenv import load_dotenv
from psycopg2 import extras

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def run_cursor(query_string: str, connection, fetch='one'):
    with connection.cursor(cursor_factory=extras.DictCursor) as cursor:
        cursor.execute(query_string)
        if fetch == 'one':
            results = cursor.fetchone()
        else:
            results = cursor.fetchall()
    connection.commit()
    return results


def get_urls(connection):
    query_str = 'SELECT urls.id, urls.name,' \
                'MAX(url_checks.created_at) as last_check,' \
                'MIN(url_checks.status_code) as ' \
                'status_code FROM urls INNER JOIN url_checks ' \
                'ON urls.id = url_checks.url_id GROUP BY (urls.id);'
    urls = run_cursor(query_str, connection, 'all')
    urls = [handle_none_values(url) for url in urls]
    return urls


def get_checks(url_id, connection):
    query_str = f'SELECT * FROM url_checks WHERE url_id={url_id};'
    checks = run_cursor(query_str, connection, 'all')
    checks = [handle_none_values(check) for check in checks]
    return checks


def get_url(condition, connection):
    url = run_cursor(f"SELECT * FROM urls WHERE ({condition});", connection)
    return url


def insert_url(url, created_at, connection):
    query_str = f"INSERT INTO urls(name, created_at) " \
                f"VALUES('{url}', '{created_at}') RETURNING *;"
    new_url = run_cursor(query_str, connection)
    return new_url


def insert_check(check, connection):
    fields, values = create_fields_and_values(check)
    query_str = f"INSERT INTO url_checks({fields}) VALUES({values}) " \
                f"RETURNING *;"
    new_check = run_cursor(query_str, connection)
    return new_check


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
