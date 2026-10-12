from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

limiter = Limiter(key_func=get_remote_address)
cache = Cache()
csrf = CSRFProtect()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'admin.login'          # куда редиректить незалогиненных
login_manager.login_message = 'Войдите, чтобы продолжить'
login_manager.login_message_category = 'error'