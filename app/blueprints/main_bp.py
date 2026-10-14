from flask import Blueprint, render_template, url_for, Response, current_app, send_from_directory
from app.models import News, Project, Equipment, HeroVideo

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Главная страница."""
    hero_videos = (HeroVideo.query
                   .filter_by(is_active=True)
                   .order_by(HeroVideo.sort_order, HeroVideo.id)
                   .all())

    projects = (Project.query
                .filter_by(is_published=True)
                .order_by(Project.sort_order, Project.created_at.desc())
                .all())

    equipment_preview = (Equipment.query
                         .filter_by(is_published=True)
                         .order_by(Equipment.sort_order, Equipment.created_at)
                         .limit(4)
                         .all())

    latest_news = (News.query
                   .filter_by(is_published=True)
                   .order_by(News.created_at.desc())
                   .limit(3)
                   .all())

    return render_template(
        'index.html',
        hero_videos=hero_videos,
        projects=projects,
        equipment_preview=equipment_preview,
        latest_news=latest_news,
    )


@main_bp.route('/sitemap.xml')
def sitemap():
    pages = []
    pages.append({'loc': url_for('main.index', _external=True), 'priority': '1.0'})
    pages.append({'loc': url_for('news.list_news', _external=True), 'priority': '0.8'})
    pages.append({'loc': url_for('equipment.catalog', _external=True), 'priority': '0.8'})

    for item in News.query.filter_by(is_published=True).all():
        pages.append({
            'loc': url_for('news.detail', slug=item.slug, _external=True),
            'lastmod': item.created_at.strftime('%Y-%m-%d'),
            'priority': '0.6',
        })

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for p in pages:
        xml += '  <url>\n'
        xml += f"    <loc>{p['loc']}</loc>\n"
        if 'lastmod' in p:
            xml += f"    <lastmod>{p['lastmod']}</lastmod>\n"
        xml += f"    <priority>{p['priority']}</priority>\n"
        xml += '  </url>\n'
    xml += '</urlset>'
    return Response(xml, mimetype='application/xml')


@main_bp.route('/robots.txt')
def robots():
    """Отдаёт robots.txt из static/."""
    return send_from_directory(
        current_app.static_folder, 'robots.txt', mimetype='text/plain'
    )