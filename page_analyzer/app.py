# region imports
import datetime
import urllib.parse

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
    db_cursor = run_cursor('SELECT id, name '
                           'FROM urls '
                           'ORDER BY created_at;')
    extant_urls = [row for row in db_cursor.fetchall()]
    return render_template('urls.html',
                           flash_messages=messages,
                           urls=extant_urls)


@app.get('/urls/<int:url_id>')
def url(url_id):
    messages = get_flashed_messages(with_categories=True)
    db_cursor = run_cursor(f'SELECT id, name, '
                           f'created_at FROM urls '
                           f'WHERE id={url_id};')
    exist_url = db_cursor.fetchone()
    return render_template('url.html',
                           flash_messages=messages,
                           url=exist_url)


@app.post('/urls')
def add_url():
    url = request.form.get('url')
    url_parts = urllib.parse.urlparse(url)
    short_url = f'{url_parts.scheme}://{url_parts.netloc}'

    exist_row = run_cursor(f"SELECT id "
                           f"FROM urls "
                           f"WHERE name = '{short_url}';").fetchone()
    if exist_row:
        flash('info', 'Страница уже существует')
        return redirect(f'urls/{exist_row["id"]}')

    if not validate_url(url):
        create_validation_flashes(url)
        session['URL'] = url
        return redirect(url_for('index'))

    db_cursor = run_cursor(f"INSERT INTO urls (name, created_at) "
                           f"VALUES ('{short_url}', '{datetime.date.today()}') "
                           f"RETURNING id;")

    id = db_cursor.fetchone()['id']
    flash('success', 'Url добавлен в базу данных.')
    return redirect(f'{url_for("urls")}/{id}')
