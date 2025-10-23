import re
import logging
from pathlib import Path
from typing import Dict, List, Any
from agent.tools.file_tools import list_files, read_file


def parse_rails_app(app_dir: str) -> Dict[str, Any]:
    """
    Аналізує структуру Rails-додатку та повертає словник з:
    - models
    - controllers
    - routes
    - templates
    """

    logging.info(f"🔍 Аналізуємо Rails-додаток у {app_dir}")
    rails_structure = {
        "models": parse_models(Path(app_dir) / "app" / "models"),
        "controllers": parse_controllers(Path(app_dir) / "app" / "controllers"),
        "routes": parse_routes(Path(app_dir) / "config" / "routes.rb"),
        "templates": parse_templates(Path(app_dir) / "app" / "views"),
    }

    logging.info(f"✅ Rails структура проаналізована: "
                 f"{len(rails_structure['models'])} моделей, "
                 f"{len(rails_structure['controllers'])} контролерів, "
                 f"{len(rails_structure['routes'])} маршрутів, "
                 f"{len(rails_structure['templates'])} шаблонів")

    return rails_structure


# --------------------------
# MODELS
# --------------------------
def parse_models(models_dir: Path) -> List[Dict[str, Any]]:
    models = []
    for file in list_files(str(models_dir), [".rb"]):
        code = read_file(file)
        model = extract_model_info(code)
        if model:
            models.append(model)
    return models


def extract_model_info(code: str) -> Dict[str, Any]:
    match = re.search(r'class\s+(\w+)\s*<\s*ApplicationRecord', code)
    if not match:
        return {}

    name = match.group(1)
    attributes = re.findall(r'attr_accessor\s+:([\w_]+)', code)
    associations = re.findall(r'(has_many|belongs_to|has_one|has_rich_text|has_one_attached)\s+:([\w_]+)', code)

    return {
        "name": name,
        "attributes": attributes,
        "associations": [f"{a[0]} :{a[1]}" for a in associations],
    }


# --------------------------
# CONTROLLERS
# --------------------------
def parse_controllers(ctrl_dir: Path) -> List[Dict[str, Any]]:
    controllers = []
    for file in list_files(str(ctrl_dir), [".rb"]):
        code = read_file(file)
        ctrl = extract_controller_info(code)
        if ctrl:
            controllers.append(ctrl)
    return controllers


def extract_controller_info(code: str) -> Dict[str, Any]:
    match = re.search(r'class\s+(\w+Controller)\s*<\s*ApplicationController', code)
    if not match:
        return {}

    name = match.group(1)
    actions = re.findall(r'def\s+([\w_]+)', code)
    filters = re.findall(r'before_action\s+:([\w_!]+)', code)
    model_match = re.search(r'@(\w+)\s*=\s*(\w+)\.find', code)

    model = model_match.group(2) if model_match else None

    return {
        "name": name,
        "actions": actions,
        "before_filters": filters,
        "model": model,
    }


# --------------------------
# ROUTES
# --------------------------
def parse_routes(routes_file: Path) -> List[Dict[str, Any]]:
    if not routes_file.exists():
        logging.warning(f"⚠️ Файл маршрутів не знайдено: {routes_file}")
        return []

    content = read_file(str(routes_file))
    routes = []

    # Простий парсер resource і get
    for m in re.finditer(r'resources\s+:([\w_]+)', content):
        ctrl = m.group(1)
        routes.append({
            "path": f"/{ctrl}",
            "controller": ctrl,
            "actions": ["index", "show", "new", "edit", "create", "update", "destroy"],
        })

    for m in re.finditer(r'get\s+[\'"]([^\'"]+)[\'"]\s*,\s*to:\s*[\'"]([^\'"]+)[\'"]', content):
        path, mapping = m.groups()
        parts = mapping.split("#")
        if len(parts) == 2:
            routes.append({
                "path": f"/{path}",
                "controller": parts[0],
                "action": parts[1],
            })

    return routes


# --------------------------
# TEMPLATES
# --------------------------
def parse_templates(views_dir: Path) -> List[Dict[str, Any]]:
    templates = []
    for file in list_files(str(views_dir), [".erb", ".html.erb"]):
        rel_path = file.split("views/")[-1]
        name = rel_path.replace(".html.erb", "").replace(".erb", "")
        variables = re.findall(r'@(\w+)', read_file(file))
        templates.append({
            "name": name,
            "variables": list(sorted(set(variables))),
        })
    return templates
