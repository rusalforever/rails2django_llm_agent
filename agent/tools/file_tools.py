import os
import logging
from pathlib import Path
from typing import List, Optional


def list_files(base_dir: str, extensions: Optional[List[str]] = None) -> List[str]:
    """
    Рекурсивно повертає список файлів у директорії base_dir.
    Можна вказати список розширень (наприклад ['.rb', '.erb']).
    """
    base_path = Path(base_dir)
    if not base_path.exists():
        logging.warning(f"⚠️ Директорія не знайдена: {base_path}")
        return []

    result = []
    for root, _, files in os.walk(base_path):
        for f in files:
            if not extensions or any(f.endswith(ext) for ext in extensions):
                result.append(str(Path(root) / f))
    logging.debug(f"📄 Знайдено {len(result)} файлів у {base_dir}")
    return result


def read_file(file_path: str) -> str:
    """
    Зчитує вміст текстового файлу з кодуванням UTF-8.
    """
    path = Path(file_path)
    if not path.exists():
        logging.error(f"❌ Файл не знайдено: {file_path}")
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            logging.debug(f"📖 Прочитано файл: {file_path} ({len(content)} симв.)")
            return content
    except Exception as e:
        logging.error(f"❌ Помилка при читанні {file_path}: {e}")
        return ""


def write_file(file_path: str, content: str):
    """
    Записує текст у файл. Створює директорії, якщо їх немає.
    """
    path = Path(file_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        logging.debug(f"💾 Записано файл: {file_path} ({len(content)} симв.)")
    except Exception as e:
        logging.error(f"❌ Помилка при записі у {file_path}: {e}")


def ensure_dir(directory: str):
    """
    Переконується, що директорія існує.
    """
    path = Path(directory)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        logging.debug(f"📁 Створено директорію: {path}")
    else:
        logging.debug(f"📂 Директорія вже існує: {path}")


def copy_static_assets(src: str, dst: str):
    """
    Копіює статичні файли (CSS, JS, images) з Rails у Django-проєкт.
    """
    from shutil import copytree, ignore_patterns

    try:
        if not Path(src).exists():
            logging.warning(f"⚠️ Статичні ресурси не знайдено: {src}")
            return
        copytree(src, dst, dirs_exist_ok=True, ignore=ignore_patterns("*.pyc", "__pycache__"))
        logging.info(f"✨ Скопійовано статичні файли з {src} → {dst}")
    except Exception as e:
        logging.error(f"❌ Не вдалося скопіювати статичні файли: {e}")
