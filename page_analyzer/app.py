import os
import psycopg2
from dotenv import load_dotenv
from datetime import date
from urllib.parse import urlparse
from flask import Flask, g, get_flashed_messages, flash
from flask import render_template, redirect, request, url_for, abort
from validators.url import url as validate
from .utils.db_utils import get_urls, get_url, insert_url
from .utils.db_utils import get_checks, insert_check
from .utils.url_utils import flash_url_errors, run_request, parse_markup

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.config.update(SECRET_KEY=SECRET_KEY,
                  DATABASE_URL=DATABASE_URL)


def get_conn():
    if not hasattr(g, 'db_connect'):
        g.db_connect = psycopg2.connect(DATABASE_URL)
        g.db_connect.autocommit = True
    return g.db_connect


@app.teardown_appcontext
def close_conn(error):
    if hasattr(g, 'db_connect'):
        g.db_connect.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def urls():
    messages = get_flashed_messages(with_categories=True)
    urls = get_urls(get_conn())
    return render_template('urls.html', flash_messages=messages, urls=urls)


@app.get('/urls/<int:url_id>')
def url(url_id):
    messages = get_flashed_messages(with_categories=True)
    url = get_url("id=%s", url_id, get_conn())
    checks = get_checks(url_id, get_conn())
    return render_template('url.html', flash_messages=messages, url=url,
                           url_checks=checks)


@app.post('/urls')
def add_url():
    url = request.form.get('url')
    parts = urlparse(url)
    formatted_url = f'{parts.scheme}://{parts.netloc}'
    query_params = ("name=%s", (formatted_url,))
    exist_url = get_url(*query_params, get_conn())
    if not validate(url):
        flash_url_errors(url)
        abort(422, {'url': url})
    if exist_url:
        flash('info', 'Страница уже существует')
        url_id = exist_url['id']
    else:
        new_url = insert_url(formatted_url, date.today(), get_conn())
        url_id = new_url['id']
        flash('success', 'Страница успешно добавлена')
    return redirect(url_for("url", url_id=url_id))


@app.post('/urls/<int:url_id>/checks')
def add_check(url_id):
    query_params = ("id=%s", (url_id,))
    url = get_url(*query_params, get_conn())
    request = run_request(url['name'])
    if request:
        check = {'url_id': url_id, 'created_at': date.today(),
                 'status_code': request.status_code,
                 **parse_markup(request.text)
                 }
        insert_check(check, get_conn())
        flash('success', 'Страница успешно проверена')
    return redirect(url_for("url", url_id=url_id))


@app.errorhandler(422)
def unprocessable_entity(error):
    messages = get_flashed_messages(with_categories=True)
    url = error.description['url']
    return render_template('index.html', flash_messages=messages, url=url), 422
