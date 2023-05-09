import os
import psycopg2
from dotenv import load_dotenv
from datetime import date
from flask import Flask, g, get_flashed_messages, flash
from flask import render_template, redirect, request, url_for, abort
from validators.url import url as validate
from .utils.db_utils import get_urls, get_url, insert_url
from .utils.db_utils import get_checks, insert_check
from .utils.url_utils import flash_url_errors, run_request, parse_html, cut_url

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.config.update(SECRET_KEY=SECRET_KEY,
                  DATABASE_URL=DATABASE_URL)


def get_connection():
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
    conn = get_connection()
    messages = get_flashed_messages(with_categories=True)
    urls = get_urls(conn)
    return render_template('urls.html', urls=urls, flashes=messages)


@app.get('/urls/<int:url_id>')
def url(url_id):
    conn = get_connection()
    messages = get_flashed_messages(with_categories=True)
    url = get_url("id", url_id, conn)
    checks = get_checks(url_id, conn)
    return render_template('url.html', url=url, checks=checks, flashes=messages)


@app.post('/urls')
def add_url():
    conn = get_connection()
    url = request.form.get('url')
    short_url = cut_url(url)
    exist_url = get_url("name", short_url, conn)
    if not validate(url):
        flash_url_errors(url)
        abort(422, {'url': url})
    if exist_url:
        flash('info', 'Страница уже существует')
        url_id = exist_url['id']
    else:
        new_url = insert_url(short_url, date.today(), conn)
        url_id = new_url['id']
        flash('success', 'Страница успешно добавлена')
    return redirect(url_for("url", url_id=url_id))


@app.post('/urls/<int:url_id>/checks')
def add_check(url_id):
    conn = get_connection()
    url = get_url("id", url_id, conn)
    request = run_request(url['name'])
    if request:
        check = {'url_id': url_id,
                 'created_at': date.today(),
                 'status_code': request.status_code,
                 **parse_html(request.text)
                 }
        insert_check(check, conn)
        flash('success', 'Страница успешно проверена')
    return redirect(url_for("url", url_id=url_id))


@app.errorhandler(422)
def unprocessable_entity(error):
    messages = get_flashed_messages(with_categories=True)
    url = error.description['url']
    return render_template('index.html', flashes=messages, url=url), 422
