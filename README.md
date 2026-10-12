# ООО «БелПромИнжиниринг» — корпоративный сайт

Flask-приложение: публичный сайт + админка (CMS) для управления контентом.
Двуязычный (RU/EN), с формой заявок, уведомлениями в Telegram и на email,
и редактируемыми через браузер новостями, проектами и каталогом оборудования.

---

## Стек

- **Backend:** Flask 3, SQLAlchemy 3, Flask-Login, Flask-WTF, Flask-Limiter
- **БД:** SQLite (файл `instance/app.db`)
- **Frontend:** Jinja2, чистый CSS + JS (без сборщиков и фреймворков)
- **Уведомления:** Telegram Bot API + Gmail SMTP
- **Сервер для прода:** gunicorn (за nginx)

---

## Возможности

### Публичная часть
- Двуязычность RU / EN (переключатель в navbar, хранится в session)
- Главная: hero с анимированными счётчиками, о компании, услуги, проекты (слайдер), контакты
- 4 страницы услуг: `/services/engineering`, `/installation`, `/machining`, `/automation`
- Каталог оборудования `/equipment` с фильтрами по категориям
- Раздел новостей `/news` (с двуязычными заголовками и текстом)
- Форма заявки с AJAX, honeypot-защитой, CSRF, rate-limit
- Страницы ошибок 404 / 500 в фирменном стиле
- Sitemap.xml и robots.txt
- Мобильная адаптация (бургер-меню, респонсивные гриды, слайдер проектов)

### Админка (`/admin`)
- Вход по логину и паролю (хэш PBKDF2, rate-limit на форму)
- Дашборд со сводкой (заявки по статусам, новости, оборудование)
- **Заявки:** список с фильтрами по статусу, смена статуса, удаление
- **Новости:** CRUD, загрузка фото, двуязычные заголовки/текст, публикация/черновик
- **Проекты:** CRUD, загрузка фото, ручная сортировка, публикация/черновик
- **Оборудование:** CRUD, загрузка фото, привязка к категории, публикация/черновик
- **Категории оборудования:** CRUD, иконки Font Awesome, порядок сортировки

### Уведомления о заявке
При отправке формы заявка:
1. Сохраняется в БД
2. Отправляется в Telegram (бот)
3. Отправляется на email (Gmail SMTP)

Если один канал падает — второй всё равно срабатывает (каждый в своём `try/except`).

---

## Структура проекта
belproming_app/
├── run.py # Запуск dev-сервера
├── wsgi.py # Точка входа для gunicorn (prod)
├── requirements.txt # Зависимости Python
├── .env # Секреты (НЕ коммитить)
├── .env.example # Шаблон переменных окружения
├── .gitignore
├── README.md # Этот файл
├── instance/
│ └── app.db # SQLite (создаётся автоматически)
├── uploads/ # Загруженные через админку фото
├── static/
│ ├── css/
│ │ ├── style.css # Публичные стили
│ │ └── admin.css # Стили админки
│ ├── js/
│ │ └── main.js # Navbar, бургер, счётчики, фильтры, AJAX-форма, слайдер
│ ├── img/ # Логотипы, favicon, hero-фон, фото по умолчанию
│ └── robots.txt
├── templates/
│ ├── base.html # Публичный каркас (navbar + footer)
│ ├── index.html # Главная
│ ├── equipment.html # Каталог
│ ├── news/
│ │ ├── list.html
│ │ └── detail.html
│ ├── services/
│ │ ├── _base.html # Общий каркас страниц услуг
│ │ ├── engineering.html
│ │ ├── installation.html
│ │ ├── machining.html
│ │ └── automation.html
│ ├── errors/
│ │ ├── 404.html
│ │ └── 500.html
│ └── admin/
│ ├── base.html # Каркас админки (sidebar + контент)
│ ├── login.html
│ ├── dashboard.html
│ ├── requests.html
│ ├── news.html
│ ├── news_form.html
│ ├── projects.html
│ ├── project_form.html
│ ├── equipment.html
│ ├── equipment_form.html
│ ├── equipment_categories.html
│ └── equipment_category_form.html
└── app/
├── init.py # create_app()
├── config.py # Config / DevelopmentConfig / ProductionConfig
├── extensions.py # db, login_manager, csrf, limiter, cache
├── models.py # User, Request, News, Project, Equipment, EquipmentCategory
├── i18n/
│ ├── init.py # Сборка TRANSLATIONS из ru.py и en.py
│ ├── ru.py
│ └── en.py
├── blueprints/
│ ├── main.py # /, /sitemap.xml, /robots.txt
│ ├── services.py # /services/<slug>
│ ├── equipment.py # /equipment
│ ├── news.py # /news, /news/<slug>
│ ├── contacts.py # POST /submit
│ └── admin.py # /admin/*
├── services/
│ ├── telegram.py # send_to_telegram()
│ └── mail.py # send_quote_request() через SMTP
└── utils/
└── uploads.py # save_upload() / delete_upload() с транслитом имён

---

## Запуск (локально)

### 1. Виртуальное окружение

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

2. Зависимости
pip install -r requirements.txt

3. Переменные окружения
