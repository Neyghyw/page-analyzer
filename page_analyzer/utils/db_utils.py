from psycopg2 import extras


def get_urls(connection):
    query_str = 'SELECT urls.id, urls.name,' \
                'MAX(url_checks.created_at) as last_check,' \
                'MIN(url_checks.status_code) as status_code ' \
                'FROM urls INNER JOIN url_checks ' \
                'ON urls.id = url_checks.url_id GROUP BY (urls.id);'
    with connection.cursor(cursor_factory=extras.DictCursor) as cursor:
        cursor.execute(query_str)
        urls = cursor.fetchall()
    urls = [handle_none_values(url) for url in urls]
    return urls


def get_checks(url_id, connection):
    query_str = 'SELECT * FROM url_checks WHERE url_id=%s;'
    with connection.cursor(cursor_factory=extras.DictCursor) as cursor:
        cursor.execute(query_str, (url_id,))
        checks = cursor.fetchall()
    checks = [handle_none_values(check) for check in checks]
    return checks


def get_url(condition, value, connection):
    query_str = f"SELECT * FROM urls WHERE ({condition});"
    with connection.cursor(cursor_factory=extras.DictCursor) as cursor:
        cursor.execute(query_str, (value,))
        url = cursor.fetchone()
    return url


def insert_url(url, created_at, connection):
    query_str = "INSERT INTO urls(name, created_at) " \
                "VALUES(%s, %s) RETURNING *;"
    with connection.cursor(cursor_factory=extras.DictCursor) as cursor:
        cursor.execute(query_str, (url, created_at,))
        new_url = cursor.fetchone()
    return new_url


def insert_check(check, connection):
    fields = str.join(', ', check.keys())
    placeholders = '%s,' * len(check.values())
    placeholders = placeholders[:-1]
    query_str = f"INSERT INTO url_checks({fields}) " \
                f"VALUES({placeholders}) " \
                f"RETURNING *;"
    with connection.cursor(cursor_factory=extras.DictCursor) as cursor:
        cursor.execute(query_str, (*check.values(),))
        new_check = cursor.fetchone()
    return new_check


def handle_none_values(row):
    for key, value in row.items():
        if value is None:
            row[key] = ''
    return row
