import os
import json
import logging
from pathlib import Path
from agent.tools.log_utils import log_state, log_llm_call
from agent.state import ConversionState


class LLMConverterNode:
    """
    Основний вузол для LLM-конвертації Rails структури у Django.
    Використовує промпт з описом Rails архітектури (з discovery_node)
    та генерує JSON-план Django-проєкту (apps, models, views, urls, templates).
    """

    def __init__(self, client, prompt_path="agent/prompts/convert_prompt.txt"):
        self.client = client
        self.prompt_path = Path(prompt_path)

    def __call__(self, state: ConversionState):
        node = "LLMConverterNode"
        logging.info(f"[3/6] 🔄 {node} started...")

        if not state.rails_structure:
            raise ValueError("❌ Missing Rails structure in state — run discovery first.")

        # --- Крок 1: Підготовка промпта ---
        prompt_template = self.prompt_path.read_text(encoding="utf-8")
        prompt = (
            prompt_template
            .replace("{{rails_structure}}", json.dumps(state.rails_structure, indent=2))
        )

        # --- Крок 2: Виклик LLM ---
        response = self.client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        llm_output = response.choices[0].message.content.strip()

        log_llm_call(node, prompt, llm_output)

        # --- Крок 3: Парсинг відповіді у JSON ---
        try:
            django_plan = json.loads(llm_output)
        except json.JSONDecodeError:
            logging.warning("⚠️ LLM output not valid JSON, wrapping raw text instead.")
            django_plan = {"raw_plan": llm_output}

        # --- Крок 4: Оновлення стану ---
        state.django_plan = django_plan
        log_state(node, state)

        logging.info(f"✅ {node} completed. Django plan generated.")
        return state
