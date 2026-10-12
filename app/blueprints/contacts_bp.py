from flask import Blueprint, request, jsonify, session, current_app
from app.extensions import db, limiter
from app.i18n import TRANSLATIONS
from app.models import Request
from app.services.telegram import send_to_telegram
from app.services.mail import send_quote_request

contacts_bp = Blueprint('contacts', __name__)


@contacts_bp.route('/submit', methods=['POST'])
@limiter.limit("5 per minute")
def submit_form():
    # Honeypot: если бот заполнил скрытое поле — тихо игнорируем
    if request.form.get('website'):
        return jsonify({'success': True})

    data = {
        k: (request.form.get(k) or '').strip()
        for k in ('name', 'company', 'email', 'phone', 'service', 'message')
    }

    if not data['name'] or not data['email']:
        return jsonify({'success': False, 'message': 'Заполните имя и email'}), 400

    # ─── 1. Сохраняем в БД ───────────────────────────────────
    req = Request(
        name=data['name'],
        company=data['company'] or None,
        email=data['email'],
        phone=data['phone'] or None,
        service=data['service'] or None,
        message=data['message'] or None,
        status='new',
    )
    db.session.add(req)
    db.session.commit()

    # ─── 2. Уведомления ──────────────────────────────────────
    tg_text = (
        f"<b>Новая заявка #{req.id}</b>\n\n"
        f"<b>Имя:</b> {data['name']}\n"
        f"<b>Компания:</b> {data['company'] or '—'}\n"
        f"<b>Email:</b> {data['email']}\n"
        f"<b>Телефон:</b> {data['phone'] or '—'}\n"
        f"<b>Услуга:</b> {data['service'] or '—'}\n"
        f"<b>Сообщение:</b>\n{data['message'] or '—'}"
    )

    try:
        send_to_telegram(tg_text)
    except Exception:
        current_app.logger.exception('Telegram notify failed')

    try:
        send_quote_request(data)
    except Exception:
        current_app.logger.exception('Email notify failed')

    # ─── 3. Ответ клиенту ────────────────────────────────────
    lang = session.get('lang', 'ru')
    return jsonify({
        'success': True,
        'message': TRANSLATIONS[lang]['form_success'],
        'request_id': req.id,
    })