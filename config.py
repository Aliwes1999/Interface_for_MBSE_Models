import os

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
SYSTEM_PROMPT_PATH = os.getenv('SYSTEM_PROMPT_PATH')
SYSTEM_PROMPT = os.getenv('SYSTEM_PROMPT')

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

def get_system_prompt():
    if SYSTEM_PROMPT_PATH and os.path.exists(SYSTEM_PROMPT_PATH):
        with open(SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
            return f.read().strip()
    elif SYSTEM_PROMPT:
        return SYSTEM_PROMPT
    else:
        return DEFAULT_SYSTEM_PROMPT
