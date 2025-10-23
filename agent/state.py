from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ConversionState(BaseModel):
    """
    Єдина модель стану для всього пайплайну LangGraph.
    Передається між нодами (planner → discovery → converter → builder → integration)
    """

    # Вхідні параметри
    input_dir: str = Field(..., description="Шлях до Rails проєкту")
    output_dir: str = Field(..., description="Шлях для Django виводу")
    log_path: Optional[str] = Field(None, description="Шлях до файлу логів")
    plan: Optional[Dict[str, Any]] = Field(None, description="Згенерований LLM план міграції")


    # Проміжні стани
    files_to_read: Optional[List[str]] = Field(default_factory=list)
    rails_structure: Optional[Dict[str, Any]] = Field(None, description="Парсинг Rails структури")
    django_plan: Optional[Dict[str, Any]] = Field(None, description="План Django проекту")
    generated_app: Optional[str] = Field(None, description="Шлях до згенерованої Django апки")
    project_root: Optional[str] = Field(None, description="Коренева директорія Django проекту")

    # Службова інформація
    current_node: Optional[str] = Field(None, description="Назва поточного вузла графу")
    llm_response: Optional[Any] = Field(None, description="Сира відповідь LLM для дебагу")

    def __repr__(self):
        return f"<ConversionState node={self.current_node} project_root={self.project_root}>"
