import requests
from flask import flash

from page_analyzer.utils.db_utils import run_cursor


def run_request(url):
    try:
        request = requests.get(url['name'])
        request.raise_for_status()
    except requests.exceptions.RequestException:
        flash('error', 'Произошла ошибка при проверке')
        return None


def get_url(condition):
    url = run_cursor(f"SELECT * FROM urls "
                     f"WHERE ({condition});"
                     ).fetchone()
    return url


def create_validation_flashes(url: str):
    if not url:
        flash('error', 'URL обязателен.')
    elif len(url) > 255:
        flash('error', 'Длина URL должна быть не более 255 символов.')
    else:
        flash('error', 'Некорректный URL')
