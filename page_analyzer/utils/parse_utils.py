import requests
from bs4 import BeautifulSoup
from flask import flash


def send_request(url):
    try:
        request = requests.get(url)
        return request
    except ConnectionError:
        flash('error', 'Произошла ошибка при проверке.')


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
