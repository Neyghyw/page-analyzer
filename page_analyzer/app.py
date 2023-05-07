import os
from datetime import date
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from flask import Flask, get_flashed_messages, flash
from flask import render_template, redirect, request, url_for, abort
from validators.url import url as validate

from .utils.db_utils import run_cursor,\
    handle_none_values,\
    create_fields_and_values
from .utils.parse_utils import parse_markup
from .utils.url_utils import get_url, create_validation_flashes

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.config.update(SECRET_KEY=SECRET_KEY,
                  DATABASE_URL=DATABASE_URL)


@app.route('/')
def index():
    return render_template('index.html')


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
    if not validate(url):
        create_validation_flashes(url)
        abort(422, {'url': url})
    if exist_url:
        url_id = exist_url['id']
        flash('info', 'Страница уже существует')
    else:
        new_url = run_cursor(f"INSERT INTO urls(name, created_at) "
                             f"VALUES('{short_url}', '{date.today()}')"
                             f"RETURNING *;").fetchone()
        url_id = new_url['id']
        flash('success', 'Страница успешно добавлена')
    return redirect(url_for("url", url_id=url_id))


@app.post('/urls/<int:url_id>/checks')
def add_check(url_id):
    url = get_url(f"id={url_id}")
    try:
        request = requests.get(url['name'])
        request.raise_for_status()
    except requests.exceptions.RequestException:
        flash('error', 'Произошла ошибка при проверке')
        return redirect(url_for("url", url_id=url_id))
    check = {'url_id': url_id,
             'created_at': date.today(),
             'status_code': request.status_code
             }
    check.update(parse_markup(request.text))
    fields, values = create_fields_and_values(check)
    run_cursor(f"INSERT INTO url_checks ({fields}) VALUES ({values});")
    flash('success', 'Страница успешно проверена')
    return redirect(url_for("url", url_id=url_id))


@app.errorhandler(422)
def unprocessable_entity(error):
    messages = get_flashed_messages(with_categories=True)
    url = error['url']
    return render_template('index.html', flash_messages=messages, url=url), 422
