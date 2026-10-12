import smtplib
from email.message import EmailMessage
from flask import current_app


def send_quote_request(data: dict) -> None:
    """Отправляет заявку на email через SMTP (Gmail)."""
    cfg = current_app.config
    host = cfg.get('SMTP_HOST')
    port = cfg.get('SMTP_PORT', 465)
    user = cfg.get('SMTP_USER')
    password = cfg.get('SMTP_PASS')
    mail_to = cfg.get('MAIL_TO')

    if not all([host, user, password, mail_to]):
        current_app.logger.warning('SMTP not configured — skip email')
        return

    msg = EmailMessage()
    msg['Subject'] = f"Новая заявка с сайта — {data.get('name', 'без имени')}"
    msg['From'] = user
    msg['To'] = mail_to

    body = (
        f"Новая заявка с сайта БелПромИнжиниринг\n"
        f"{'=' * 40}\n\n"
        f"Имя:      {data.get('name', '—')}\n"
        f"Компания: {data.get('company', '—')}\n"
        f"Email:    {data.get('email', '—')}\n"
        f"Телефон:  {data.get('phone', '—')}\n"
        f"Услуга:   {data.get('service', '—')}\n\n"
        f"Сообщение:\n{data.get('message', '—')}\n"
    )
    msg.set_content(body)

    try:
        # Используем SMTP_SSL для порта 465 (шифрование с самого начала)
        with smtplib.SMTP_SSL(host, port, timeout=10) as smtp:
            smtp.login(user, password)
            smtp.send_message(msg)
    except Exception:
        current_app.logger.exception('Email send failed')