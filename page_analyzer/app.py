# region imports
from datetime import date
import urllib.parse
import requests
from requests.exceptions import ConnectionError

from dotenv import dotenv_values
from flask import Flask
from flask import flash, get_flashed_messages
from flask import render_template, redirect, request
from flask import url_for, session

from .utils.db_utils import run_cursor
from .utils.url_utils import validate_url, create_validation_flashes

# endregion


SECRET_KEY = dotenv_values('.env').get('SECRET_KEY')
app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    entered_url = session.get('URL', '')
    session.clear()
    return render_template('index.html',
                           flash_messages=messages,
                           url=entered_url)


@app.get('/urls')
def urls():
    messages = get_flashed_messages(with_categories=True)
    extant_urls = run_cursor('SELECT urls.id, urls.name, '
                             'url_checks.created_at as last_check, '
                             'url_checks.status_code '
                             'FROM urls INNER JOIN '
                             'url_checks ON urls.id = url_checks.url_id;'
                             ).fetchall()
    return render_template('urls.html',
                           flash_messages=messages,
                           urls=extant_urls)


@app.get('/urls/<int:url_id>')
def url(url_id):
    messages = get_flashed_messages(with_categories=True)
    url = run_cursor(f'SELECT id, name, '
                     f'created_at FROM urls '
                     f'WHERE id={url_id};'
                     ).fetchone()

    checks = run_cursor(f'SELECT id, status_code, h1, '
                        f'title, description, '
                        f'created_at FROM url_checks '
                        f'WHERE url_id={url_id};'
                        ).fetchall()

    return render_template('url.html',
                           flash_messages=messages,
                           url=url,
                           url_checks=checks)


@app.post('/urls')
def add_url():
    url = request.form.get('url')
    url_parts = urllib.parse.urlparse(url)
    short_url = f'{url_parts.scheme}://{url_parts.netloc}'

    exist_row = run_cursor(f"SELECT id FROM urls "
                           f"WHERE name = '{short_url}';").fetchone()
    if exist_row:
        flash('info', 'Страница уже существует')
        id = exist_row['id']
    elif not validate_url(url):
        create_validation_flashes(url)
        session['URL'] = url
        return redirect(url_for('index'))
    else:
        cursor = run_cursor(f"INSERT INTO urls(name, created_at) "
                            f"VALUES('{short_url}', '{date.today()}') "
                            f"RETURNING id;")
        id = cursor.fetchone()['id']
        flash('success', 'Url добавлен в базу данных.')

    return redirect(url_for("url", url_id=id))


@app.post('/urls/<int:url_id>/checks')
def add_check(url_id):
    url = run_cursor(f'SELECT * FROM urls WHERE id={url_id};').fetchone()
    try:
        request_sender = requests.get(url['name'])
        code = request_sender.status_code
        run_cursor(f"INSERT INTO url_checks (url_id, created_at, status_code) "
                   f"VALUES ({url_id}, '{date.today()}', '{code}');")
    except ConnectionError:
        flash('error', 'Произошла ошибка при проверке.')
    return redirect(url_for("url", url_id=url_id))
