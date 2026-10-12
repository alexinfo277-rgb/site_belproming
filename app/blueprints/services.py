from flask import Blueprint, render_template, abort

services_bp = Blueprint('services', __name__)

# Список доступных slug'ов услуг
SERVICES = {
    'engineering',
    'installation',
    'machining',
    'automation',
}


@services_bp.route('/<slug>')
def detail(slug):
    if slug not in SERVICES:
        abort(404)
    return render_template(f'services/{slug}.html', slug=slug)