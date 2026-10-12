import re
import uuid
from pathlib import Path
from flask import current_app


def allowed_file(filename: str) -> bool:
    """Проверяет расширение файла по белому списку."""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[-1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']


def _translit(name: str) -> str:
    """Транслитерация кириллицы в латиницу + очистка."""
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    }
    name = name.lower()
    name = ''.join(translit_map.get(ch, ch) for ch in name)
    name = re.sub(r'[^a-z0-9]+', '-', name).strip('-')
    return name or 'file'


def save_upload(file) -> str | None:
    """
    Сохраняет файл в UPLOAD_FOLDER.
    Возвращает имя сохранённого файла или None, если файл невалидный.
    """
    if not file or not file.filename:
        return None

    original = file.filename

    # Расширение берём из ОРИГИНАЛЬНОГО имени — не через secure_filename
    if '.' not in original:
        return None
    ext = original.rsplit('.', 1)[-1].lower()

    if ext not in current_app.config['ALLOWED_EXTENSIONS']:
        return None

    # Транслитерируем имя без расширения (для читаемости — можно и без него)
    base = _translit(original.rsplit('.', 1)[0])[:40]
    unique = f"{base}-{uuid.uuid4().hex[:8]}.{ext}"

    folder = Path(current_app.config['UPLOAD_FOLDER'])
    folder.mkdir(parents=True, exist_ok=True)
    file.save(folder / unique)
    return unique


def delete_upload(filename: str | None) -> None:
    """Удаляет файл из UPLOAD_FOLDER, если он существует."""
    if not filename:
        return
    path = Path(current_app.config['UPLOAD_FOLDER']) / filename
    if path.exists():
        try:
            path.unlink()
        except OSError:
            current_app.logger.exception(f'Не удалось удалить файл {path}')