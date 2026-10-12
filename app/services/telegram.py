import requests
from flask import current_app


def send_to_telegram(text: str) -> None:
    """Отправляет текст в Telegram через Bot API."""
    cfg = current_app.config
    token = cfg.get('TG_BOT_TOKEN')
    chat_id = cfg.get('TG_CHAT_ID')

    if not token or not chat_id:
        current_app.logger.warning('Telegram not configured — skip')
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True,
    }

    try:
        resp = requests.post(url, json=payload, timeout=8)
        resp.raise_for_status()
    except Exception:
        current_app.logger.exception('Telegram send failed')