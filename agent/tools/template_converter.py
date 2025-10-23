import re
import logging
from pathlib import Path
from agent.tools.file_tools import list_files, read_file, write_file, ensure_dir


def convert_erb_to_django(erb_content: str) -> str:
    """
    Перетворює ERB-шаблон з Rails у HTML-шаблон у стилі Django.
    Основна ідея — конвертація Ruby-синтаксису <%= %> у {{ }},
    а <% %> у {% %}.
    """
    # <%= expression %> → {{ expression }}
    html = re.sub(r"<%=\s*(.*?)\s*%>", r"{{ \1 }}", erb_content)

    # <% code %> → {% code %}
    html = re.sub(r"<%\s*(.*?)\s*%>", r"{% \1 %}", html)

    # Ruby коментарі → HTML коментарі
    html = re.sub(r"<%#\s*(.*?)\s*%>", r"<!-- \1 -->", html)

    # Замінюємо Ruby змінні @var → var
    html = re.sub(r"@(\w+)", r"\1", html)

    # Заміна Ruby умов на Django теги
    html = html.replace("if", "if").replace("elsif", "elif").replace("end", "endif")

    # Часткові рендери <%= render 'partial' %> → {% include 'partial.html' %}
    html = re.sub(r"{%\s*include\s*['\"]([\w\/]+)['\"]\s*%}", r"{% include '\1.html' %}", html)
    html = re.sub(r"{{\s*render\s*['\"]([\w\/]+)['\"]\s*}}", r"{% include '\1.html' %}", html)

    return html


def convert_erb_file(erb_file: str, out_dir: str):
    """
    Конвертує один ERB-файл у HTML-шаблон Django.
    """
    content = read_file(erb_file)
    converted = convert_erb_to_django(content)

    rel_path = Path(erb_file).name.replace(".erb", ".html")
    ensure_dir(out_dir)
    write_file(Path(out_dir) / rel_path, converted)

    logging.debug(f"🧩 Конвертовано шаблон {erb_file} → {rel_path}")


def batch_convert_erb(rails_views_dir: str, django_templates_dir: str):
    """
    Рекурсивно конвертує всі Rails-шаблони (ERB) у Django-шаблони.
    """
    erb_files = list_files(rails_views_dir, [".erb", ".html.erb"])
    logging.info(f"🎨 Знайдено {len(erb_files)} ERB шаблонів для конвертації...")

    for erb_file in erb_files:
        relative = Path(erb_file).relative_to(rails_views_dir)
        out_path = Path(django_templates_dir) / relative.parent
        ensure_dir(out_path)
        convert_erb_file(erb_file, str(out_path))

    logging.info(f"✅ Усі шаблони конвертовано у {django_templates_dir}")
