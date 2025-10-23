import os
import logging
from pathlib import Path
from agent.tools.log_utils import log_state, log_llm_call
from agent.state import ConversionState


class LLMIntegrationNode:
    """
    Завершальний етап конвертації:
    - Генерує README.md
    - Генерує requirements.txt
    - Підсумовує процес і лог
    """

    def __init__(self, client, prompt_path="agent/prompts/integration_prompt.txt"):
        self.client = client
        self.prompt_path = Path(prompt_path)

    def __call__(self, state: ConversionState):
        node = "LLMIntegrationNode"
        logging.info(f"[5/6] 📦 {node} started...")

        if not state.project_root:
            raise ValueError("❌ Missing project_root — build step must run first.")

        project_root = Path(state.project_root)

        # --- 1️⃣ README.md ---
        readme_prompt = self.prompt_path.read_text(encoding="utf-8")
        readme_prompt = (
            readme_prompt
            .replace("{{rails_structure}}", str(state.rails_structure))
            .replace("{{django_plan}}", str(state.django_plan))
        )

        readme_response = self.client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "gpt-4o"),
            messages=[{"role": "user", "content": readme_prompt}],
            temperature=0.2,
        )

        readme_md = readme_response.choices[0].message.content.strip()
        log_llm_call(node, readme_prompt, readme_md)

        with open(project_root / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_md)

        # --- 2️⃣ requirements.txt ---
        req_prompt = "Generate minimal requirements.txt for Django 5 project with SQLite."
        req_response = self.client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "gpt-4o"),
            messages=[{"role": "user", "content": req_prompt}],
            temperature=0.1,
        )
        req_text = req_response.choices[0].message.content.strip()
        log_llm_call(node, req_prompt, req_text)

        with open(project_root / "requirements.txt", "w", encoding="utf-8") as f:
            f.write(req_text)

        # --- 3️⃣ логування фінального стану ---
        log_state(node, state)

        logging.info(f"✅ {node} completed. Django project ready at {state.output_dir}")
        return state
