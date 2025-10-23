import os
import json
import logging
from pathlib import Path


def build_django_project(django_plan: dict, root: Path):
    """
    Генерує Django apps, models, views, urls і templates
    відповідно до структури, створеної LLMConverterNode.
    """

    apps = django_plan.get("apps", [])
    for app in apps:
        app_name = app["name"]
        app_dir = root / app_name
        app_dir.mkdir(parents=True, exist_ok=True)

        # models.py
        models_file = app_dir / "models.py"
        with models_file.open("w", encoding="utf-8") as f:
            f.write("from django.db import models\n\n")
            for model in app.get("models", []):
                f.write(f"class {model['name']}(models.Model):\n")
                for field, ftype in model.get("fields", {}).items():
                    f.write(f"    {field} = models.{ftype}(max_length=255)\n")
                f.write("\n")

        # views.py
        views_file = app_dir / "views.py"
        with views_file.open("w", encoding="utf-8") as f:
            f.write("from django.views import generic\n")
            f.write(f"from .models import *\n\n")
            for view in app.get("views", []):
                f.write(f"class {view['name']}(generic.{view['type']}):\n")
                f.write(f"    model = {view['model']}\n")
                f.write(f"    template_name = '{view.get('template', '')}'\n\n")

        # urls.py
        urls_file = app_dir / "urls.py"
        with urls_file.open("w", encoding="utf-8") as f:
            f.write("from django.urls import path\n")
            f.write("from . import views\n\n")
            f.write("urlpatterns = [\n")
            for url in app.get("urls", []):
                f.write(f"    path('{url['pattern']}', views.{url['view']}.as_view(), name='{url['view'].lower()}'),\n")
            f.write("]\n")

        # templates
        for tmpl in app.get("templates", []):
            tmpl_path = root / app_name / "templates" / tmpl["name"]
            tmpl_path.parent.mkdir(parents=True, exist_ok=True)
            with tmpl_path.open("w", encoding="utf-8") as f:
                f.write("{% extends 'base.html' %}\n{% block content %}\n")
                f.write(f"<!-- Auto-generated template for {tmpl['name']} -->\n")
                f.write("{% endblock %}\n")

        # apps.py
        apps_file = app_dir / "apps.py"
        with apps_file.open("w", encoding="utf-8") as f:
            f.write("from django.apps import AppConfig\n\n")
            f.write(f"class {app_name.capitalize()}Config(AppConfig):\n")
            f.write(f"    default_auto_field = 'django.db.models.BigAutoField'\n")
            f.write(f"    name = '{app_name}'\n")

        # __init__.py
        (app_dir / "__init__.py").touch()

        logging.info(f"✅ Django app '{app_name}' created.")

    logging.info("🎯 Django project build completed.")
