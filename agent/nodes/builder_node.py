import os
import json
import logging
import subprocess
from pathlib import Path
from agent.tools.django_builder import build_django_project
from agent.tools.log_utils import log_state
from agent.state import ConversionState


class LLMProjectBuilderNode:
    """
    Побудова реального Django-проєкту згідно з планом,
    створеним LLMConverterNode.
    """

    def __call__(self, state: ConversionState):
        node = "LLMProjectBuilderNode"
        logging.info(f"[4/6] 🏗️ {node} started...")

        if not state.django_plan:
            raise ValueError("❌ Missing Django plan in state — run converter first.")

        out_dir = Path(state.output_dir).resolve()
        proj_name = "converted_project"

        # --- 1️⃣ створюємо базову структуру проєкту ---
        subprocess.run(["django-admin", "startproject", proj_name, str(out_dir)], check=False)
        state.project_root = str(out_dir / proj_name)

        # --- 2️⃣ будуємо внутрішні Django-app-и ---
        build_django_project(state.django_plan, Path(state.project_root))

        # --- 3️⃣ логування ---
        log_state(node, state)
        logging.info(f"✅ {node} completed. Project root: {state.project_root}")

        return state
