import os

from dotenv import load_dotenv
from flask import Flask, g, get_flashed_messages, flash
from flask import render_template, redirect, request, url_for, abort
from validators.url import url as validate

from page_analyzer import db
from page_analyzer.utils.url_utils import get_url_errors, \
    run_request, cut_url, build_check

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.config.update(SECRET_KEY=SECRET_KEY,
                  DATABASE_URL=DATABASE_URL)


def get_connection():
    if not hasattr(g, 'db_connect'):
        g.db_connect = db.create_connection(DATABASE_URL)
    return g.db_connect


@app.teardown_appcontext
def close_conn(error):
    if hasattr(g, 'db_connect'):
        db.close_connection(g.db_connect)


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def urls():
    conn = get_connection()
    messages = get_flashed_messages(with_categories=True)
    urls = db.get_urls(conn)
    return render_template('urls.html', urls=urls, flashes=messages)


@app.get('/urls/<int:url_id>')
def url(url_id):
    conn = get_connection()
    messages = get_flashed_messages(with_categories=True)
    url = db.get_url(conn, url_id)
    if not url:
        abort(404)
    checks = db.get_checks(conn, url_id)
    return render_template('url.html', url=url, checks=checks, flashes=messages)


@app.post('/urls')
def add_url():
    conn = get_connection()
    url = request.form.get('url')
    short_url = cut_url(url)
    exist_url = db.get_url_by_name(conn, short_url)
    if not validate(url):
        [flash('error', error_text) for error_text in get_url_errors(url)]
        abort(422, {'url': url})
    if exist_url:
        flash('info', 'Страница уже существует')
        url_id = exist_url['id']
    else:
        new_url = db.insert_url(conn, short_url)
        url_id = new_url['id']
        flash('success', 'Страница успешно добавлена')
    return redirect(url_for("url", url_id=url_id))


@app.post('/urls/<int:url_id>/checks')
def add_check(url_id):
    conn = get_connection()
    url = db.get_url(conn, url_id)
    response = run_request(url['name'])
    if response:
        check = build_check(url_id, response)
        db.insert_check(conn, check)
        flash('success', 'Страница успешно проверена')
    else:
        flash('error', 'Произошла ошибка при проверке')
        abort(500)
    return redirect(url_for("url", url_id=url_id))


@app.errorhandler(422)
def unprocessable_entity(error):
    messages = get_flashed_messages(with_categories=True)
    url = error.description['url']
    return render_template('index.html', flashes=messages, url=url), 422


@app.errorhandler(404)
def page_not_found(error):
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', flashes=messages), 404


@app.errorhandler(500)
def internal_server_error(error):
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', flashes=messages), 500
