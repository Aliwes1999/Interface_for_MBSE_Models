import os

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
SYSTEM_PROMPT_PATH = os.getenv('SYSTEM_PROMPT_PATH')
SYSTEM_PROMPT = os.getenv('SYSTEM_PROMPT')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///instance/db.db')

class ProductionConfig(Config):
    DEBUG = False
    # Fix for Render's PostgreSQL URL format
    # Render provides postgres:// but SQLAlchemy 1.4+ requires postgresql://
    database_url = os.getenv('DATABASE_URL', 'sqlite:///instance/db.db')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = database_url

# Default System Prompt if none provided
DEFAULT_SYSTEM_PROMPT = """
Du bist ein erfahrener Requirements Engineer.
Erzeuge klare, testbare, präzise Software-Anforderungen im JSON-Format.
Antworte ausschließlich mit gültigem JSON in folgender Struktur:
{
  "requirements": [
    {"title": "...", "description": "...", "category": "...", "status": "Offen"}
  ]
}
Regeln:
- Maximiere Klarheit und Testbarkeit (Akzeptanzkriterien implizit in description).
- Verwende kurze, prägnante Titel.
- 'status' ist immer 'Offen'.
- Wenn Informationen fehlen, triff sinnvolle, konservative Annahmen.
"""

def get_system_prompt(columns=None):
    """
    Get system prompt, optionally customized for dynamic columns.
    
    Args:
        columns (list): Optional list of column names for the project
    
    Returns:
        str: System prompt text
    """
    if SYSTEM_PROMPT_PATH and os.path.exists(SYSTEM_PROMPT_PATH):
        with open(SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
            base_prompt = f.read().strip()
    elif SYSTEM_PROMPT:
        base_prompt = SYSTEM_PROMPT
    else:
        base_prompt = DEFAULT_SYSTEM_PROMPT
    
    # If columns are provided, customize the prompt
    if columns and isinstance(columns, list):
        # Build JSON structure based on columns
        json_fields = []
        for col in columns:
            col_lower = col.lower()
            if col_lower in ['titel', 'title']:
                json_fields.append(f'"{col}": "Kurzer, prägnanter Titel"')
            elif col_lower in ['beschreibung', 'description']:
                json_fields.append(f'"{col}": "Detaillierte Beschreibung mit Akzeptanzkriterien"')
            elif col_lower in ['kategorie', 'category']:
                json_fields.append(f'"{col}": "Kategorie (z.B. Funktional, Nicht-Funktional, etc.)"')
            elif col_lower in ['status']:
                json_fields.append(f'"{col}": "Offen"')
            else:
                json_fields.append(f'"{col}": "Passender Wert für {col}"')
        
        json_structure = "{\n      " + ",\n      ".join(json_fields) + "\n    }"
        
        custom_prompt = f"""
Du bist ein erfahrener Requirements Engineer.
Erzeuge klare, testbare, präzise Software-Anforderungen im JSON-Format.

Das Projekt verwendet folgende Spalten: {', '.join(columns)}

Antworte ausschließlich mit gültigem JSON in folgender Struktur:
{{
  "requirements": [
    {json_structure}
  ]
}}

Regeln:
- Maximiere Klarheit und Testbarkeit (Akzeptanzkriterien implizit in Beschreibung).
- Verwende kurze, prägnante Titel.
- Fülle ALLE angegebenen Spalten mit sinnvollen Werten.
- Wenn Informationen fehlen, triff sinnvolle, konservative Annahmen.
- Generiere mindestens 3 und maximal 10 Requirements.
"""
        return custom_prompt
    
    return base_prompt
