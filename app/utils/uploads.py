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


def save_upload(file, subfolder: str = '', allowed: set | None = None) -> str | None:
    """
    Сохраняет файл в UPLOAD_FOLDER (или в UPLOAD_FOLDER/subfolder).
    Возвращает относительный путь ('имя.mp4' или 'hero/имя.mp4') или None.

    :param subfolder: подпапка внутри UPLOAD_FOLDER (например 'hero')
    :param allowed:   своё множество расширений; по умолчанию — ALLOWED_EXTENSIONS
    """
    if not file or not file.filename:
        return None

    original = file.filename

    if '.' not in original:
        return None
    ext = original.rsplit('.', 1)[-1].lower()

    allowed_exts = allowed if allowed is not None else current_app.config['ALLOWED_EXTENSIONS']
    if ext not in allowed_exts:
        return None

    base = _translit(original.rsplit('.', 1)[0])[:40]
    unique = f"{base}-{uuid.uuid4().hex[:8]}.{ext}"

    root = Path(current_app.config['UPLOAD_FOLDER'])
    folder = root / subfolder if subfolder else root
    folder.mkdir(parents=True, exist_ok=True)
    file.save(folder / unique)

    return f"{subfolder}/{unique}" if subfolder else unique


def delete_upload(filename: str | None) -> None:
    """Удаляет файл из UPLOAD_FOLDER (учитывает подпапки)."""
    if not filename:
        return
    path = Path(current_app.config['UPLOAD_FOLDER']) / filename
    if path.exists():
        try:
            path.unlink()
            # Заодно подчистим пустую подпапку
            parent = path.parent
            if parent != Path(current_app.config['UPLOAD_FOLDER']) and parent.is_dir():
                try:
                    parent.rmdir()  # сработает только если пустая
                except OSError:
                    pass
        except OSError:
            current_app.logger.exception(f'Не удалось удалить файл {path}')