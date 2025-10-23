import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any


def setup_logging(log_dir: str = "logs"):
    """
    Ініціалізує логування з часом, кольорами і файлом для запису.
    """
    Path(log_dir).mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("run_%Y%m%d_%H%M")
    log_path = Path(log_dir) / f"{timestamp}.log"

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

    logging.info(f"📝 Logging to: {log_path}")
    return log_path


def log_state(node_name: str, state: Any):
    """
    Логує поточний стан після кожного вузла у форматі JSON.
    """
    try:
        # Уникаємо надто великих даних (якщо є файли)
        filtered = {}
        for k, v in state.__dict__.items():
            if isinstance(v, (str, int, float, bool, list, dict, type(None))):
                filtered[k] = v
            else:
                filtered[k] = str(v)

        state_json = json.dumps(filtered, indent=2, ensure_ascii=False)
        logging.debug(f"\n📦 STATE SNAPSHOT AFTER [{node_name}]\n{state_json}\n")

    except Exception as e:
        logging.error(f"❌ Помилка при логуванні стану: {e}")


def log_llm_call(node_name: str, prompt: str, response: str):
    """
    Форматоване логування LLM викликів (prompt + response).
    """
    logging.debug(f"\n--- LLM CALL [{node_name}] ---")
    logging.debug(f"[PROMPT ↓]\n{prompt.strip()}\n")
    logging.debug(f"[RESPONSE ↓]\n{response.strip()}\n")
    logging.debug(f"--- END LLM CALL ---\n")


def summarize_state_changes(old_state: Any, new_state: Any) -> str:
    """
    Порівнює зміни у state до і після ноди.
    Повертає короткий текст для діагностики.
    """
    try:
        summary = []
        old_dict = old_state.__dict__
        new_dict = new_state.__dict__

        for key, new_val in new_dict.items():
            old_val = old_dict.get(key)
            if new_val != old_val:
                summary.append(f"🔹 {key}: {old_val} → {new_val}")

        if summary:
            msg = "\n".join(summary)
        else:
            msg = "🟢 Без змін у state."

        logging.info(f"📊 Зміни після ноди:\n{msg}")
        return msg

    except Exception as e:
        logging.error(f"❌ Не вдалося порівняти стани: {e}")
        return "⚠️ Помилка при аналізі змін."
