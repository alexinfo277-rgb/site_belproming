from flask import Blueprint, render_template, abort, g
from app.models import News

news_bp = Blueprint('news', __name__)


@news_bp.route('/')
def list_news():
    """Список всех опубликованных новостей."""
    items = (News.query
             .filter_by(is_published=True)
             .order_by(News.created_at.desc())
             .all())
    return render_template('news/list.html', news=items)


@news_bp.route('/<slug>')
def detail(slug):
    """Одна новость по slug."""
    item = News.query.filter_by(slug=slug, is_published=True).first()
    if not item:
        abort(404)

    # Выбираем язык контента
    lang = g.lang
    title = item.title_en if (lang == 'en' and item.title_en) else item.title_ru
    body = item.body_en if (lang == 'en' and item.body_en) else item.body_ru

    return render_template('news/detail.html', item=item, title=title, body=body)