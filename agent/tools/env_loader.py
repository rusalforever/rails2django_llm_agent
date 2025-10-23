import os
import logging
from pathlib import Path
from dotenv import load_dotenv


def load_env(env_path: str = ".env"):
    """
    Завантажує .env файл і виводить інформацію про успішне зчитування.
    Якщо файл не знайдено — попереджає, але не зупиняє виконання.
    """

    env_file = Path(env_path).resolve()
    if not env_file.exists():
        logging.warning(f"⚠️  .env файл не знайдено: {env_file}")
        return

    load_dotenv(env_file)
    logging.info(f"✅ .env файл завантажено: {env_file}")

    # Логування основних змінних для перевірки
    for key in ["OPENAI_API_KEY", "MODEL_NAME"]:
        value = os.getenv(key)
        if value:
            masked = value[:5] + "..." + value[-3:] if len(value) > 8 else "***"
            logging.info(f"🔹 {key} = {masked}")
        else:
            logging.warning(f"⚠️  Змінна {key} не визначена у .env")


def require_env(var_name: str) -> str:
    """
    Перевіряє, що змінна середовища встановлена, і повертає її значення.
    Якщо змінної немає — викликає помилку.
    """
    value = os.getenv(var_name)
    if not value:
        raise EnvironmentError(f"❌ Змінна середовища {var_name} не встановлена.")
    return value
