from flask import flash
from validators.url import url as validate


def validate_url(url: str):
    if not url or len(url) > 255 or not validate(url):
        return False
    return True


def create_validation_flashes(url: str):
    if not url:
        flash('error', 'URL обязателен.')
    elif len(url) > 255:
        flash('error', 'Длина URL должна быть не более 255 символов.')
    else:
        flash('error', 'URL не существует.')
