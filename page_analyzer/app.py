# region imports
import os
from datetime import date
from urllib.parse import urlparse

from dotenv import load_dotenv
from flask import Flask
from flask import flash, get_flashed_messages
from flask import render_template, redirect, request
from flask import url_for, session
from validators.url import url as validate

from .utils.db_utils import run_cursor, \
    create_fields_and_values, \
    handle_none_values
from .utils.parse_utils import parse_markup, send_request
from .utils.url_utils import create_validation_flashes, get_url

# endregion

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.config.update(SECRET_KEY=SECRET_KEY,
                  DATABASE_URL=DATABASE_URL)


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
    urls = run_cursor('SELECT urls.id, urls.name, '
                      'url_checks.created_at as last_check, '
                      'url_checks.status_code '
                      'FROM urls INNER JOIN '
                      'url_checks ON urls.id = url_checks.url_id;'
                      ).fetchall()
    urls = [handle_none_values(url) for url in urls]
    return render_template('urls.html',
                           flash_messages=messages,
                           urls=urls)


@app.get('/urls/<int:url_id>')
def url(url_id):
    messages = get_flashed_messages(with_categories=True)
    url = get_url(f'id={url_id}')
    checks = run_cursor(f'SELECT * FROM url_checks '
                        f'WHERE url_id={url_id};'
                        ).fetchall()
    checks = [handle_none_values(check) for check in checks]
    return render_template('url.html',
                           flash_messages=messages,
                           url=url,
                           url_checks=checks)


@app.post('/urls')
def add_url():
    url = request.form.get('url')
    parts = urlparse(url)
    short_url = f'{parts.scheme}://{parts.netloc}'
    exist_url = get_url(f"name='{short_url}'")
    if exist_url:
        flash('info', 'Страница уже существует')
        url_id = exist_url['id']
    elif not validate(url):
        create_validation_flashes(url)
        session['URL'] = url
        return redirect(url_for("index"))
    else:
        new_url = run_cursor(f"INSERT INTO urls(name, created_at) "
                             f"VALUES('{short_url}', '{date.today()}')"
                             f"RETURNING *;").fetchone()
        url_id = new_url['id']
        flash('success', 'URL добавлен в базу данных.')
    return redirect(url_for("url", url_id=url_id))


@app.post('/urls/<int:url_id>/checks')
def add_check(url_id):
    url = get_url(f"id={url_id}'")
    request = send_request(url['name'])
    if request:
        check = {
            'url_id': url_id,
            'created_at': date.today(),
            'status_code': request.status_code
        }
        check.update(parse_markup(request.text))
        fields, values = create_fields_and_values(check)
        run_cursor(f"INSERT INTO url_checks ({fields}) VALUES ({values});")
    return redirect(url_for("url", url_id=url_id))
