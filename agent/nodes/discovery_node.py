import os
import logging
from pathlib import Path
from agent.tools.log_utils import log_state, log_llm_call
from agent.tools.rails_parser import parse_rails_app
from agent.state import ConversionState


class LLMDiscoveryNode:
    """
    Аналізує Rails-проєкт і створює структуроване представлення його складових.
    Використовує локальний парсер + LLM для уточнення архітектури.
    """

    def __init__(self, client, prompt_path="agent/prompts/discovery_prompt.txt"):
        self.client = client
        self.prompt_path = Path(prompt_path)

    def __call__(self, state: ConversionState):
        node = "LLMDiscoveryNode"
        logging.info(f"[2/6] 🔍 {node} started...")

        input_dir = Path(state.input_dir)
        if not input_dir.exists():
            raise FileNotFoundError(f"❌ Input directory not found: {input_dir}")

        # --- Крок 1: Локальний парсинг ---
        rails_structure = parse_rails_app(input_dir)
        state.rails_structure = rails_structure

        # --- Крок 2: Формування промпта для уточнення через LLM ---
        prompt_template = self.prompt_path.read_text(encoding="utf-8")
        prompt = prompt_template.replace("{{rails_structure}}", str(rails_structure))

        # --- Крок 3: Виклик LLM для уточнення структури ---
        response = self.client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        llm_output = response.choices[0].message.content.strip()
        log_llm_call(node, prompt, llm_output)

        # --- Крок 4: Збереження ---
        state.rails_summary = llm_output
        log_state(node, state)

        logging.info(f"✅ {node} completed. Files analyzed: {len(rails_structure.get('files', []))}")
        return state
