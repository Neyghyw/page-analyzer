import psycopg2
from psycopg2 import extras
from datetime import datetime


def create_connection(connection_str):
    db_connect = psycopg2.connect(connection_str)
    db_connect.autocommit = True
    return db_connect


def close_connection(connection):
    connection.close()


def get_urls(conn):
    with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
        cursor.execute("SELECT urls.id, urls.name, "
                       "MAX(url_checks.created_at) as last_check, "
                       "MIN(url_checks.status_code) as status_code "
                       "FROM urls INNER JOIN url_checks "
                       "ON urls.id = url_checks.url_id "
                       "GROUP BY (urls.id);")
        urls = cursor.fetchall()
    return urls


def get_checks(conn, url_id):
    query_str = "SELECT * FROM url_checks WHERE url_id=%s"
    with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
        cursor.execute(query_str, (url_id,))
        checks = cursor.fetchall()
    return checks


def get_url(conn, id):
    query_str = "SELECT * FROM urls WHERE id=%s;"
    with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
        cursor.execute(query_str, (id,))
        url = cursor.fetchone()
    return url


def get_url_by_name(conn, name):
    query_str = "SELECT * FROM urls WHERE name=%s;"
    with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
        cursor.execute(query_str, (name,))
        url = cursor.fetchone()
    return url


def insert_url(conn, url):
    query_str = "INSERT INTO urls(name, created_at) VALUES(%s, %s) RETURNING *;"

    with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
        cursor.execute(query_str, (url, datetime.now(),))
        new_url = cursor.fetchone()
    return new_url


def insert_check(conn, check):
    values = (
        check.get('url_id'),
        check.get('created_at'),
        check.get('status_code'),
        check.get('h1'),
        check.get('description'),
        check.get('title')
    )
    query_str = ("INSERT INTO url_checks(url_id, created_at, "
                 "status_code, h1, description, title) "
                 "VALUES(%s,%s,%s,%s,%s,%s) RETURNING *;")
    with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
        cursor.execute(query_str, (*values,))
        new_check = cursor.fetchone()
    return new_check
