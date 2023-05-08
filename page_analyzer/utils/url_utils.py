import requests
from bs4 import BeautifulSoup
from flask import flash

URL_LENGTH = 255


def run_request(url):
    try:
        request = requests.get(url)
        request.raise_for_status()
        return request
    except requests.exceptions.RequestException:
        flash('error', 'Произошла ошибка при проверке')


def flash_url_errors(url: str):
    if not url:
        flash('error', 'URL обязателен.')
    elif len(url) > URL_LENGTH:
        flash('error', f'Длина URL должна быть не более {URL_LENGTH} символов.')
    else:
        flash('error', 'Некорректный URL')


def parse_markup(markup):
    soup = BeautifulSoup(markup, 'html.parser')
    parts = dict()
    meta = soup.head.find('meta', {'name': 'description'})
    if soup.title:
        parts['title'] = soup.title.text
    if meta:
        parts['description'] = meta.get('content')
    if soup.h1.text:
        parts['h1'] = soup.h1.text
    return parts
