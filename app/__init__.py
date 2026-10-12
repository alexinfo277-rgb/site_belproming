from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, g, jsonify, send_from_directory
from flask_wtf.csrf import CSRFError

from app.config import CONFIG
from app.extensions import limiter, cache, csrf, db, login_manager
from app.i18n import TRANSLATIONS

from app.blueprints.main_bp import main_bp
from app.blueprints.news_bp import news_bp
from app.blueprints.contacts_bp import contacts_bp
from app.blueprints.admin import admin_bp
from app.blueprints.equipment import equipment_bp
from app.blueprints.services import services_bp

def create_app(config_name='dev'):
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static',
    )
    app.config.from_object(CONFIG[config_name])

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    limiter.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(news_bp, url_prefix='/news')
    app.register_blueprint(contacts_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(equipment_bp, url_prefix='/equipment')
    app.register_blueprint(services_bp, url_prefix='/services')

    # Загрузка пользователя для Flask-Login
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.before_request
    def set_language():
        lang = request.args.get('lang') or session.get('lang', 'ru')
        if lang not in TRANSLATIONS:
            lang = 'ru'
        session['lang'] = lang
        g.lang = lang

    @app.context_processor
    def inject_globals():
        return {
            't': TRANSLATIONS.get(g.lang, TRANSLATIONS['ru']),
            'lang': g.lang,
            'alt_lang': 'en' if g.lang == 'ru' else 'ru',
            'now': datetime.now(),
        }

    @app.route('/lang/<code>')
    def set_lang(code):
        if code in TRANSLATIONS:
            session['lang'] = code
        return redirect(request.referrer or url_for('main.index'))

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.exception('Server error')
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        if request.accept_mimetypes.accept_json or request.is_json:
            return jsonify({
                'success': False,
                'message': 'Сессия устарела. Обновите страницу и попробуйте снова.'
            }), 400
        return 'Сессия устарела. Обновите страницу и попробуйте снова.', 400

    with app.app_context():
        db.create_all()

    # Отдача загруженных файлов (фото новостей)


    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    return app