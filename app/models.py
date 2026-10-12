from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(UserMixin, db.Model):
    """Пользователь админки."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f'<User {self.username}>'


class Request(db.Model):
    """Заявка с формы сайта."""
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(150))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(40))
    service = db.Column(db.String(50))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='new', index=True)  # new / in_progress / done
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Request {self.id} {self.name}>'


class News(db.Model):
    """Новость компании."""
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    title_ru = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200))
    body_ru = db.Column(db.Text, nullable=False)
    body_en = db.Column(db.Text)
    image = db.Column(db.String(200))              # имя файла в uploads/
    is_published = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<News {self.slug}>'

class Project(db.Model):
    """Реализованный проект."""
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title_ru = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200))
    desc_ru = db.Column(db.Text, nullable=False)
    desc_en = db.Column(db.Text)
    image = db.Column(db.String(200))              # имя файла в uploads/
    is_published = db.Column(db.Boolean, default=True, index=True)
    sort_order = db.Column(db.Integer, default=0)  # ручная сортировка
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Project {self.id} {self.title_ru}>'

class Equipment(db.Model):
    """Единица оборудования в каталоге."""
    __tablename__ = 'equipment'

    id = db.Column(db.Integer, primary_key=True)
    title_ru = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200))
    desc_ru = db.Column(db.Text, nullable=False)
    desc_en = db.Column(db.Text)
    category = db.Column(db.String(30), nullable=False, default='other', index=True)
    # category: 'tanks' / 'cip' / 'heat' / 'other'
    image = db.Column(db.String(200))
    is_published = db.Column(db.Boolean, default=True, index=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Equipment {self.id} {self.title_ru}>'

class EquipmentCategory(db.Model):
    """Категория оборудования (для фильтров)."""
    __tablename__ = 'equipment_categories'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(30), unique=True, nullable=False, index=True)
    name_ru = db.Column(db.String(80), nullable=False)
    name_en = db.Column(db.String(80))
    icon = db.Column(db.String(60))              # FA-класс, например 'fa-database'
    sort_order = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<EquipmentCategory {self.slug}>'