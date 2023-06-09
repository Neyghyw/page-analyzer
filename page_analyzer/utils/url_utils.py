from urllib.parse import urlparse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from flask import flash

URL_LENGTH = 255


def run_request(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException:
        flash('error', 'Произошла ошибка при проверке')


def flash_url_errors(url: str):
    if not url:
        flash('error', 'URL обязателен.')
    elif len(url) > URL_LENGTH:
        flash('error', f'Длина URL должна быть не более {URL_LENGTH} символов.')
    else:
        flash('error', 'Некорректный URL')


def parse_html(markup):
    soup = BeautifulSoup(markup, 'html.parser')
    parts = dict()
    meta = soup.head.find('meta', {'name': 'description'})
    if soup.title:
        parts['title'] = soup.title.text
    if meta:
        parts['description'] = meta.get('content')
    if soup.h1:
        parts['h1'] = soup.h1.text
    return parts


def build_check(url_id, response):
    check = {'url_id': url_id,
             'created_at': datetime.now(),
             'status_code': response.status_code,
             **parse_html(response.text)
             }
    return check


def cut_url(url):
    parts = urlparse(url)
    formatted_url = f'{parts.scheme}://{parts.netloc}'
    return formatted_url
