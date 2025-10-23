import argparse
import logging
from datetime import datetime
from agent.graph import run_conversion_pipeline
from agent.tools.env_loader import load_env


def setup_logging():
    """Налаштовуємо розширене логування в консоль і файл"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    log_file = f"logs/run_{timestamp}.log"
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    logging.info(f"🧠 Логування активовано → {log_file}")
    return log_file


def main():
    load_env()  # зчитуємо .env і виводимо ключові параметри
    log_path = setup_logging()

    parser = argparse.ArgumentParser(description="Rails → Django LLM Converter")
    parser.add_argument("--input", required=True, help="Шлях до Rails-проєкту")
    parser.add_argument("--output", required=True, help="Шлях для Django-виводу")
    args = parser.parse_args()

    logging.info("🚀 Запуск конвертера...")
    run_conversion_pipeline(args.input, args.output, log_path)
    logging.info("✅ Конверсія завершена успішно!")


if __name__ == "__main__":
    main()
