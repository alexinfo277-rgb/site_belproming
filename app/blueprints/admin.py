from functools import wraps
import re
from datetime import datetime
from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, abort
)
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired

from app.extensions import db, limiter
from app.models import User, Request, News, Project, Equipment, EquipmentCategory, HeroVideo

from app.utils.uploads import save_upload, delete_upload

admin_bp = Blueprint('admin', __name__, template_folder='../../templates/admin')


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')


@admin_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            # Защита от open redirect: next должен быть относительным
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('admin.dashboard'))
        flash('Неверный логин или пароль', 'error')

    return render_template('admin/login.html', form=form)


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из админки', 'success')
    return redirect(url_for('main.index'))

@admin_bp.route('/requests')
@login_required
def requests_list():
    status = request.args.get('status', '').strip()

    query = Request.query
    if status in ('new', 'in_progress', 'done'):
        query = query.filter_by(status=status)

    items = query.order_by(Request.created_at.desc()).all()

    return render_template(
        'admin/requests.html',
        requests=items,
        current_status=status,
    )


@admin_bp.route('/requests/<int:req_id>/status', methods=['POST'])
@login_required
def request_set_status(req_id):
    req = Request.query.get_or_404(req_id)
    new_status = request.form.get('status', '').strip()
    if new_status not in ('new', 'in_progress', 'done'):
        flash('Недопустимый статус', 'error')
        return redirect(url_for('admin.requests_list'))
    req.status = new_status
    db.session.commit()
    flash(f'Статус заявки #{req.id} изменён на «{new_status}»', 'success')
    return redirect(request.referrer or url_for('admin.requests_list'))


@admin_bp.route('/requests/<int:req_id>/delete', methods=['POST'])
@login_required
def request_delete(req_id):
    req = Request.query.get_or_404(req_id)
    db.session.delete(req)
    db.session.commit()
    flash(f'Заявка #{req_id} удалена', 'success')
    return redirect(url_for('admin.requests_list'))

@admin_bp.route('/')
@login_required
def dashboard():
    stats = {
        'requests_total': Request.query.count(),
        'requests_new': Request.query.filter_by(status='new').count(),
        'requests_in_progress': Request.query.filter_by(status='in_progress').count(),
        'requests_done': Request.query.filter_by(status='done').count(),
        'news_total': News.query.count(),
        'news_published': News.query.filter_by(is_published=True).count(),
    }
    recent_requests = (Request.query
                       .order_by(Request.created_at.desc())
                       .limit(5)
                       .all())
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_requests=recent_requests,
    )

def _slugify(text: str) -> str:
    """Транслитерация + slug для URL."""
    translit = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    }
    text = text.lower()
    text = ''.join(translit.get(ch, ch) for ch in text)
    text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    return text or f'news-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}'


@admin_bp.route('/news')
@login_required
def news_list():
    items = News.query.order_by(News.created_at.desc()).all()
    return render_template('admin/news.html', news=items)


@admin_bp.route('/news/new', methods=['GET', 'POST'])
@login_required
def news_create():
    if request.method == 'POST':
        title_ru = (request.form.get('title_ru') or '').strip()
        if not title_ru:
            flash('Заголовок (RU) обязателен', 'error')
            return redirect(url_for('admin.news_create'))

        slug = (request.form.get('slug') or '').strip() or _slugify(title_ru)

        # Уникальность slug
        base_slug = slug
        counter = 1
        while News.query.filter_by(slug=slug).first():
            counter += 1
            slug = f'{base_slug}-{counter}'

        image = save_upload(request.files.get('image'))

        item = News(
            slug=slug,
            title_ru=title_ru,
            title_en=(request.form.get('title_en') or '').strip() or None,
            body_ru=(request.form.get('body_ru') or '').strip() or title_ru,
            body_en=(request.form.get('body_en') or '').strip() or None,
            image=image,
            is_published=bool(request.form.get('is_published')),
        )
        db.session.add(item)
        db.session.commit()

        flash(f'Новость «{item.title_ru}» создана', 'success')
        return redirect(url_for('admin.news_list'))

    return render_template('admin/news_form.html', item=None)


@admin_bp.route('/news/<int:news_id>/edit', methods=['GET', 'POST'])
@login_required
def news_edit(news_id):
    item = News.query.get_or_404(news_id)

    if request.method == 'POST':
        title_ru = (request.form.get('title_ru') or '').strip()
        if not title_ru:
            flash('Заголовок (RU) обязателен', 'error')
            return redirect(url_for('admin.news_edit', news_id=news_id))

        item.title_ru = title_ru
        item.title_en = (request.form.get('title_en') or '').strip() or None
        item.body_ru = (request.form.get('body_ru') or '').strip() or title_ru
        item.body_en = (request.form.get('body_en') or '').strip() or None
        item.is_published = bool(request.form.get('is_published'))

        new_slug = (request.form.get('slug') or '').strip()
        if new_slug and new_slug != item.slug:
            candidate = new_slug
            base_slug = candidate
            counter = 1
            while News.query.filter(News.slug == candidate, News.id != item.id).first():
                counter += 1
                candidate = f'{base_slug}-{counter}'
            item.slug = candidate

        new_file = request.files.get('image')
        if new_file and new_file.filename:
            if item.image:
                delete_upload(item.image)
            item.image = save_upload(new_file)

        db.session.commit()
        flash('Новость обновлена', 'success')
        return redirect(url_for('admin.news_list'))

    return render_template('admin/news_form.html', item=item)


@admin_bp.route('/news/<int:news_id>/delete', methods=['POST'])
@login_required
def news_delete(news_id):
    item = News.query.get_or_404(news_id)
    if item.image:
        delete_upload(item.image)
    db.session.delete(item)
    db.session.commit()
    flash(f'Новость «{item.title_ru}» удалена', 'success')
    return redirect(url_for('admin.news_list'))


@admin_bp.route('/news/<int:news_id>/toggle', methods=['POST'])
@login_required
def news_toggle(news_id):
    item = News.query.get_or_404(news_id)
    item.is_published = not item.is_published
    db.session.commit()
    state = 'опубликована' if item.is_published else 'снята с публикации'
    flash(f'Новость «{item.title_ru}» {state}', 'success')
    return redirect(url_for('admin.news_list'))


@admin_bp.route('/news/<int:news_id>/image/delete', methods=['POST'])
@login_required
def news_image_delete(news_id):
    item = News.query.get_or_404(news_id)
    if item.image:
        delete_upload(item.image)
        item.image = None
        db.session.commit()
        flash('Фото удалено', 'success')
    return redirect(url_for('admin.news_edit', news_id=news_id))

# ═══════════════════════════════════════════════════════════════
#  ПРОЕКТЫ — CRUD
# ═══════════════════════════════════════════════════════════════

@admin_bp.route('/projects')
@login_required
def projects_list():
    items = Project.query.order_by(Project.sort_order, Project.created_at.desc()).all()
    return render_template('admin/projects.html', projects=items)


@admin_bp.route('/projects/new', methods=['GET', 'POST'])
@login_required
def project_create():
    if request.method == 'POST':
        title_ru = (request.form.get('title_ru') or '').strip()
        desc_ru = (request.form.get('desc_ru') or '').strip()
        if not title_ru or not desc_ru:
            flash('Заголовок (RU) и описание (RU) обязательны', 'error')
            return redirect(url_for('admin.project_create'))

        image = save_upload(request.files.get('image'))

        item = Project(
            title_ru=title_ru,
            title_en=(request.form.get('title_en') or '').strip() or None,
            desc_ru=desc_ru,
            desc_en=(request.form.get('desc_en') or '').strip() or None,
            image=image,
            is_published=bool(request.form.get('is_published')),
            sort_order=int(request.form.get('sort_order') or 0),
        )
        db.session.add(item)
        db.session.commit()

        flash(f'Проект «{item.title_ru}» создан', 'success')
        return redirect(url_for('admin.projects_list'))

    return render_template('admin/project_form.html', item=None)


@admin_bp.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def project_edit(project_id):
    item = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        title_ru = (request.form.get('title_ru') or '').strip()
        desc_ru = (request.form.get('desc_ru') or '').strip()
        if not title_ru or not desc_ru:
            flash('Заголовок (RU) и описание (RU) обязательны', 'error')
            return redirect(url_for('admin.project_edit', project_id=project_id))

        item.title_ru = title_ru
        item.title_en = (request.form.get('title_en') or '').strip() or None
        item.desc_ru = desc_ru
        item.desc_en = (request.form.get('desc_en') or '').strip() or None
        item.is_published = bool(request.form.get('is_published'))
        item.sort_order = int(request.form.get('sort_order') or 0)

        new_file = request.files.get('image')
        if new_file and new_file.filename:
            if item.image:
                delete_upload(item.image)
            item.image = save_upload(new_file)

        db.session.commit()
        flash('Проект обновлён', 'success')
        return redirect(url_for('admin.projects_list'))

    return render_template('admin/project_form.html', item=item)


@admin_bp.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def project_delete(project_id):
    item = Project.query.get_or_404(project_id)
    if item.image:
        delete_upload(item.image)
    db.session.delete(item)
    db.session.commit()
    flash(f'Проект «{item.title_ru}» удалён', 'success')
    return redirect(url_for('admin.projects_list'))


@admin_bp.route('/projects/<int:project_id>/toggle', methods=['POST'])
@login_required
def project_toggle(project_id):
    item = Project.query.get_or_404(project_id)
    item.is_published = not item.is_published
    db.session.commit()
    state = 'опубликован' if item.is_published else 'снят с публикации'
    flash(f'Проект «{item.title_ru}» {state}', 'success')
    return redirect(url_for('admin.projects_list'))


@admin_bp.route('/projects/<int:project_id>/image/delete', methods=['POST'])
@login_required
def project_image_delete(project_id):
    item = Project.query.get_or_404(project_id)
    if item.image:
        delete_upload(item.image)
        item.image = None
        db.session.commit()
        flash('Фото удалено', 'success')
    return redirect(url_for('admin.project_edit', project_id=project_id))

# ═══════════════════════════════════════════════════════════════
#  ОБОРУДОВАНИЕ — CRUD
# ═══════════════════════════════════════════════════════════════

EQ_CATEGORIES = ('tanks', 'cip', 'heat', 'other')


@admin_bp.route('/equipment')
@login_required
def equipment_list():
    items = Equipment.query.order_by(Equipment.sort_order, Equipment.created_at.desc()).all()
    return render_template('admin/equipment.html', equipment=items, categories=EQ_CATEGORIES)


@admin_bp.route('/equipment/new', methods=['GET', 'POST'])
@login_required
def equipment_create():
    if request.method == 'POST':
        title_ru = (request.form.get('title_ru') or '').strip()
        desc_ru = (request.form.get('desc_ru') or '').strip()
        category = (request.form.get('category') or 'other').strip()

        if not title_ru or not desc_ru:
            flash('Заголовок и описание (RU) обязательны', 'error')
            return redirect(url_for('admin.equipment_create'))
        valid_slugs = {c.slug for c in EquipmentCategory.query.all()}
        if category not in valid_slugs:
            category = 'other'  # или первая доступная

        image = save_upload(request.files.get('image'))

        item = Equipment(
            title_ru=title_ru,
            title_en=(request.form.get('title_en') or '').strip() or None,
            desc_ru=desc_ru,
            desc_en=(request.form.get('desc_en') or '').strip() or None,
            category=category,
            image=image,
            is_published=bool(request.form.get('is_published')),
            sort_order=int(request.form.get('sort_order') or 0),
        )
        db.session.add(item)
        db.session.commit()
        flash(f'Оборудование «{item.title_ru}» создано', 'success')
        return redirect(url_for('admin.equipment_list'))

    cats = EquipmentCategory.query.order_by(EquipmentCategory.sort_order).all()
    return render_template('admin/equipment_form.html', item=None, categories=cats)


@admin_bp.route('/equipment/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def equipment_edit(item_id):
    item = Equipment.query.get_or_404(item_id)

    if request.method == 'POST':
        title_ru = (request.form.get('title_ru') or '').strip()
        desc_ru = (request.form.get('desc_ru') or '').strip()
        category = (request.form.get('category') or 'other').strip()

        if not title_ru or not desc_ru:
            flash('Заголовок и описание (RU) обязательны', 'error')
            return redirect(url_for('admin.equipment_edit', item_id=item_id))
        valid_slugs = {c.slug for c in EquipmentCategory.query.all()}
        if category not in valid_slugs:
            category = 'other'  # или первая доступная

        item.title_ru = title_ru
        item.title_en = (request.form.get('title_en') or '').strip() or None
        item.desc_ru = desc_ru
        item.desc_en = (request.form.get('desc_en') or '').strip() or None
        item.category = category
        item.is_published = bool(request.form.get('is_published'))
        item.sort_order = int(request.form.get('sort_order') or 0)

        new_file = request.files.get('image')
        if new_file and new_file.filename:
            if item.image:
                delete_upload(item.image)
            item.image = save_upload(new_file)

        db.session.commit()
        flash('Оборудование обновлено', 'success')
        return redirect(url_for('admin.equipment_list'))

    cats = EquipmentCategory.query.order_by(EquipmentCategory.sort_order).all()
    return render_template('admin/equipment_form.html', item=item, categories=cats)


@admin_bp.route('/equipment/<int:item_id>/delete', methods=['POST'])
@login_required
def equipment_delete(item_id):
    item = Equipment.query.get_or_404(item_id)
    if item.image:
        delete_upload(item.image)
    db.session.delete(item)
    db.session.commit()
    flash(f'Оборудование «{item.title_ru}» удалено', 'success')
    return redirect(url_for('admin.equipment_list'))


@admin_bp.route('/equipment/<int:item_id>/toggle', methods=['POST'])
@login_required
def equipment_toggle(item_id):
    item = Equipment.query.get_or_404(item_id)
    item.is_published = not item.is_published
    db.session.commit()
    state = 'опубликовано' if item.is_published else 'снято с публикации'
    flash(f'Оборудование «{item.title_ru}» {state}', 'success')
    return redirect(url_for('admin.equipment_list'))


@admin_bp.route('/equipment/<int:item_id>/image/delete', methods=['POST'])
@login_required
def equipment_image_delete(item_id):
    item = Equipment.query.get_or_404(item_id)
    if item.image:
        delete_upload(item.image)
        item.image = None
        db.session.commit()
        flash('Фото удалено', 'success')
    return redirect(url_for('admin.equipment_edit', item_id=item_id))

# ═══════════════════════════════════════════════════════════════
#  КАТЕГОРИИ ОБОРУДОВАНИЯ — CRUD
# ═══════════════════════════════════════════════════════════════

@admin_bp.route('/equipment-categories')
@login_required
def equipment_categories_list():
    items = EquipmentCategory.query.order_by(
        EquipmentCategory.sort_order, EquipmentCategory.created_at
    ).all()

    # Посчитать, сколько оборудования в каждой категории
    usage = {}
    for cat in items:
        usage[cat.slug] = Equipment.query.filter_by(category=cat.slug).count()

    return render_template('admin/equipment_categories.html',
                           categories=items, usage=usage)


@admin_bp.route('/equipment-categories/new', methods=['GET', 'POST'])
@login_required
def equipment_category_create():
    if request.method == 'POST':
        name_ru = (request.form.get('name_ru') or '').strip()
        slug = (request.form.get('slug') or '').strip().lower()

        if not name_ru:
            flash('Название (RU) обязательно', 'error')
            return redirect(url_for('admin.equipment_category_create'))
        if not slug:
            slug = _slugify(name_ru)[:30]

        if EquipmentCategory.query.filter_by(slug=slug).first():
            flash(f'Slug «{slug}» уже используется', 'error')
            return redirect(url_for('admin.equipment_category_create'))

        item = EquipmentCategory(
            slug=slug,
            name_ru=name_ru,
            name_en=(request.form.get('name_en') or '').strip() or None,
            icon=(request.form.get('icon') or '').strip() or None,
            sort_order=int(request.form.get('sort_order') or 0),
            is_published=bool(request.form.get('is_published')),
        )
        db.session.add(item)
        db.session.commit()
        flash(f'Категория «{name_ru}» создана', 'success')
        return redirect(url_for('admin.equipment_categories_list'))

    return render_template('admin/equipment_category_form.html', item=None)


@admin_bp.route('/equipment-categories/<int:cat_id>/edit', methods=['GET', 'POST'])
@login_required
def equipment_category_edit(cat_id):
    item = EquipmentCategory.query.get_or_404(cat_id)

    if request.method == 'POST':
        name_ru = (request.form.get('name_ru') or '').strip()
        slug = (request.form.get('slug') or '').strip().lower()

        if not name_ru:
            flash('Название (RU) обязательно', 'error')
            return redirect(url_for('admin.equipment_category_edit', cat_id=cat_id))
        if not slug:
            slug = item.slug  # оставляем как было

        # Проверить уникальность slug (кроме самой себя)
        dup = EquipmentCategory.query.filter(
            EquipmentCategory.slug == slug,
            EquipmentCategory.id != item.id
        ).first()
        if dup:
            flash(f'Slug «{slug}» уже используется', 'error')
            return redirect(url_for('admin.equipment_category_edit', cat_id=cat_id))

        # Если slug меняется, а на нём уже висит оборудование — предупреждаем
        old_slug = item.slug
        if slug != old_slug:
            used = Equipment.query.filter_by(category=old_slug).count()
            if used > 0:
                flash(f'Нельзя изменить slug: на нём {used} единиц оборудования. '
                      f'Сначала переназначьте их на другую категорию.', 'error')
                return redirect(url_for('admin.equipment_category_edit', cat_id=cat_id))

        item.slug = slug
        item.name_ru = name_ru
        item.name_en = (request.form.get('name_en') or '').strip() or None
        item.icon = (request.form.get('icon') or '').strip() or None
        item.sort_order = int(request.form.get('sort_order') or 0)
        item.is_published = bool(request.form.get('is_published'))

        db.session.commit()
        flash('Категория обновлена', 'success')
        return redirect(url_for('admin.equipment_categories_list'))

    return render_template('admin/equipment_category_form.html', item=item)


@admin_bp.route('/equipment-categories/<int:cat_id>/delete', methods=['POST'])
@login_required
def equipment_category_delete(cat_id):
    item = EquipmentCategory.query.get_or_404(cat_id)
    used = Equipment.query.filter_by(category=item.slug).count()

    if used > 0:
        flash(f'Нельзя удалить «{item.name_ru}»: к ней привязано {used} единиц оборудования. '
              f'Переназначьте их на другую категорию.', 'error')
        return redirect(url_for('admin.equipment_categories_list'))

    db.session.delete(item)
    db.session.commit()
    flash(f'Категория «{item.name_ru}» удалена', 'success')
    return redirect(url_for('admin.equipment_categories_list'))


@admin_bp.route('/equipment-categories/<int:cat_id>/toggle', methods=['POST'])
@login_required
def equipment_category_toggle(cat_id):
    item = EquipmentCategory.query.get_or_404(cat_id)
    item.is_published = not item.is_published
    db.session.commit()
    state = 'видна на сайте' if item.is_published else 'скрыта с фильтров'
    flash(f'Категория «{item.name_ru}» — {state}', 'success')
    return redirect(url_for('admin.equipment_categories_list'))

# ─── Список видео ───
@admin_bp.route('/hero-videos')
@login_required
def hero_videos_list():
    videos = HeroVideo.query.order_by(HeroVideo.sort_order, HeroVideo.id).all()
    return render_template('admin/hero_videos.html', videos=videos)


# ─── Загрузка нового видео ───
@admin_bp.route('/hero-videos/new', methods=['GET', 'POST'])
@login_required
def hero_video_new():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        sort_order = request.form.get('sort_order', 0, type=int)
        is_active = bool(request.form.get('is_active'))

        file = request.files.get('video')
        if not file or not file.filename:
            flash('Выберите видеофайл', 'error')
            return redirect(request.url)

        # Разрешаем только видео
        allowed = {'mp4', 'webm', 'mov'}
        ext = file.filename.rsplit('.', 1)[-1].lower()
        if ext not in allowed:
            flash('Допустимы только mp4, webm, mov', 'error')
            return redirect(request.url)

        filename = save_upload(file, subfolder='hero')

        video = HeroVideo(
            title=title,
            filename=filename,
            sort_order=sort_order,
            is_active=is_active,
        )
        db.session.add(video)
        db.session.commit()
        flash('Видео добавлено', 'success')
        return redirect(url_for('admin.hero_videos_list'))

    return render_template('admin/hero_video_form.html', video=None)


# ─── Редактирование ───
@admin_bp.route('/hero-videos/<int:vid>/edit', methods=['GET', 'POST'])
@login_required
def hero_video_edit(vid):
    video = HeroVideo.query.get_or_404(vid)

    if request.method == 'POST':
        video.title = request.form.get('title', '').strip()
        video.sort_order = request.form.get('sort_order', 0, type=int)
        video.is_active = bool(request.form.get('is_active'))

        # Если загрузили новое видео — заменяем старое
        file = request.files.get('video')
        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[-1].lower()
            if ext not in {'mp4', 'webm', 'mov'}:
                flash('Допустимы только mp4, webm, mov', 'error')
                return redirect(request.url)
            delete_upload(video.filename)
            video.filename = save_upload(file, subfolder='hero')

        db.session.commit()
        flash('Видео обновлено', 'success')
        return redirect(url_for('admin.hero_videos_list'))

    return render_template('admin/hero_video_form.html', video=video)


# ─── Удаление ───
@admin_bp.route('/hero-videos/<int:vid>/delete', methods=['POST'])
@login_required
def hero_video_delete(vid):
    video = HeroVideo.query.get_or_404(vid)
    delete_upload(video.filename)
    db.session.delete(video)
    db.session.commit()
    flash('Видео удалено', 'success')
    return redirect(url_for('admin.hero_videos_list'))


# ─── Быстрое вкл/выкл ───
@admin_bp.route('/hero-videos/<int:vid>/toggle', methods=['POST'])
@login_required
def hero_video_toggle(vid):
    video = HeroVideo.query.get_or_404(vid)
    video.is_active = not video.is_active
    db.session.commit()
    return redirect(url_for('admin.hero_videos_list'))