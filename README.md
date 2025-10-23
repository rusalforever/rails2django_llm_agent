# rails2django_llm_agent

### 🧠 Опис
Цей агент автоматично конвертує Ruby on Rails-проєкти у Django,
використовуючи **LangGraph ≥ 0.6** і **GPT-4o (LLM)**.

### ⚙️ Встановлення
```bash
git clone <repo>
cd rails2django_llm_agent
pip install -r requirements.txt
python main.py --input ./my_rails_app --output ./out_django