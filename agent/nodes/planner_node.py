import logging
import json
import re
from pathlib import Path
from agent.tools.log_utils import log_state, log_llm_call
from agent.state import ConversionState


class LLMPlannerNode:
    """
    Побудова початкового плану конвертації Rails→Django.
    Викликає LLM для створення покрокового плану дій на основі вхідного проєкту.
    """

    def __init__(self, client, prompt_path: str = "agent/prompts/plan_prompt.txt"):
        self.client = client
        self.prompt_path = Path(prompt_path)

    def __call__(self, state: ConversionState):
        node = "LLMPlannerNode"
        logging.info(f"[1/6] 🧭 {node} started...")

        # --- Завантаження промпта ---
        if self.prompt_path.exists():
            prompt_template = self.prompt_path.read_text(encoding="utf-8")
        else:
            # fallback-промпт, якщо файла немає
            logging.warning(f"⚠️ Prompt file not found at {self.prompt_path}. Using default prompt.")
            prompt_template = (
                "You are an expert AI assistant specializing in converting Ruby on Rails projects to Django. "
                "Analyze the Rails project located at '{{input_dir}}' and produce a detailed JSON plan for conversion. "
                "The JSON should include a list of steps with clear actions, descriptions, and dependencies."
            )

        # --- Формування динамічного промпта ---
        input_dir = Path(state.input_dir).resolve()
        prompt = prompt_template.replace("{{input_dir}}", str(input_dir))

        # --- Виклик LLM ---
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a senior software architect."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            llm_output = response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"❌ LLM API call failed: {e}")
            raise

        # --- Логування ---
        log_llm_call(node, prompt, llm_output)

        # --- Обробка та парсинг відповіді ---
        # видаляємо код-блоки ```json ... ```
        clean_output = re.sub(r"^```(json|python)?|```$", "", llm_output.strip(), flags=re.MULTILINE).strip()

        try:
            parsed = json.loads(clean_output)
        except json.JSONDecodeError:
            logging.warning("⚠️ Planner output is not valid JSON. Storing raw output instead.")
            parsed = {"raw_plan": clean_output}

        # --- Оновлення стану ---
        state.plan = parsed
        state.llm_response = llm_output
        state.current_node = "planner"

        log_state(node, state)
