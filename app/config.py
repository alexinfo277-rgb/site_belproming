import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-me')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'instance' / 'app.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200 МБ
    ALLOWED_EXTENSIONS = {
        # картинки
        'png', 'jpg', 'jpeg', 'webp', 'gif', 'svg',
        # видео для hero
        'mp4', 'webm', 'mov',
    }

    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300

    # ─── Email (SMTP) ─────────────────────────────────────────
    SMTP_HOST = os.environ.get('SMTP_HOST')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USER = os.environ.get('SMTP_USER')
    SMTP_PASS = os.environ.get('SMTP_PASS')
    MAIL_TO = os.environ.get('MAIL_TO')

    # ─── Telegram ─────────────────────────────────────────────
    TG_BOT_TOKEN = os.environ.get('TG_BOT_TOKEN')
    TG_CHAT_ID = os.environ.get('TG_CHAT_ID')


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


CONFIG = {'dev': DevelopmentConfig, 'prod': ProductionConfig}