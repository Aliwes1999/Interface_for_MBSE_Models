import os
import json
import re
import sys
from pathlib import Path
from openai import OpenAI

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import config


class AIClient:
    """AI Client for requirements analysis and generation"""

    def __init__(self):
        self.api_key = config.OPENAI_API_KEY
        self.model = config.OPENAI_MODEL or "gpt-4o-mini"
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set.")
        self.client = OpenAI(api_key=self.api_key)

    def analyze_requirements(self, requirements_text: str) -> dict:
        """
        Analyze requirements text and provide insights

        Args:
            requirements_text (str): The requirements text to analyze

        Returns:
            dict: Analysis results
        """
        system_prompt = """Du bist ein erfahrener Requirements Engineer. Analysiere die gegebenen Anforderungen und gib eine strukturierte Bewertung.

PHASE 1: Strukturanalyse - Prüfe Vollständigkeit, Klarheit und Konsistenz
PHASE 2: Inhaltsanalyse - Bewerte SMART-Kriterien, Normenkonformität und Testbarkeit
PHASE 3: Risikoanalyse - Identifiziere potenzielle Probleme oder Lücken
PHASE 4: Empfehlungen - Gib konkrete Verbesserungsvorschläge

Antworte im JSON-Format mit den Schlüsseln: struktur, inhalt, risiko, empfehlungen."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analysiere diese Anforderungen:\n\n{requirements_text}"}
                ],
                temperature=0.2,
                max_tokens=800
            )

            response_text = response.choices[0].message.content.strip()

            # Try to parse as JSON, fallback to text
            try:
                analysis = json.loads(response_text)
            except json.JSONDecodeError:
                analysis = {
                    "struktur": "Analyse durchgeführt",
                    "inhalt": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                    "risiko": "Weitere Prüfung empfohlen",
                    "empfehlungen": "Detaillierte Analyse verfügbar"
                }

            return analysis

        except Exception as e:
            return {
                "error": f"Analyse fehlgeschlagen: {str(e)}",
                "struktur": "Nicht analysiert",
                "inhalt": "Nicht analysiert",
                "risiko": "Unbekannt",
                "empfehlungen": "Manuelle Prüfung erforderlich"
            }

    def suggest_improvements(self, requirement) -> list:
        """
        Suggest improvements for a specific requirement

        Args:
            requirement: The requirement object to improve

        Returns:
            list: List of improvement suggestions
        """
        system_prompt = """Du bist ein erfahrener Requirements Engineer. Verbessere die gegebene Anforderung nach folgenden Kriterien:

1. SMART-Prinzip (Spezifisch, Messbar, Erreichbar, Relevant, Terminiert)
2. Normenkonformität (z.B. nach IEEE 830)
3. Präzise Formulierung (eindeutige Sprache)
4. Testbarkeit (klare Akzeptanzkriterien)

Gib 3-5 konkrete Verbesserungsvorschläge als Liste zurück."""

        requirement_text = f"Titel: {requirement.title}\nBeschreibung: {requirement.description}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Verbessere diese Anforderung:\n\n{requirement_text}"}
                ],
                temperature=0.3,
                max_tokens=600
            )

            response_text = response.choices[0].message.content.strip()

            # Try to extract suggestions from response
            suggestions = []
            lines = response_text.split('\n')

            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Clean up the suggestion
                    clean_suggestion = re.sub(r'^[\d\.\-\•]+\s*', '', line)
                    if clean_suggestion and len(clean_suggestion) > 10:
                        suggestions.append(clean_suggestion)

            # If no structured suggestions found, return the whole response as one suggestion
            if not suggestions:
                suggestions = [response_text]

            return suggestions[:5]  # Limit to 5 suggestions

        except Exception as e:
            return [f"Verbesserungsvorschläge konnten nicht generiert werden: {str(e)}"]

def generate_requirements(user_description: str | None, inputs: dict, columns: list = None, existing_requirements: list[dict] = None) -> list[dict]:
    """
    Calls OpenAI API to generate requirements based on user description and inputs.

    Args:
        user_description (str | None): Optional user description of requirements.
        inputs (dict): Key-value pairs for additional context.
        columns (list): Optional list of column names for the project.
        existing_requirements (list[dict]): Optional list of existing requirements to optimize.

    Returns:
        list[dict]: List of requirement dicts with dynamic columns based on project.

    Raises:
        ValueError: If OPENAI_API_KEY is not set.
        RuntimeError: If OpenAI API call fails or response is invalid.
    """
    # Get configuration
    api_key = config.OPENAI_API_KEY
    model = config.OPENAI_MODEL or "gpt-4o-mini"

    # New structured system prompt based on 4-phase methodology
    if existing_requirements:
        system_prompt = """Du bist ein erfahrener Requirements Engineer. Arbeite nach dem 4-Phasen-Modell:

PHASE 1 & 2 (Analyse/Struktur): Analysiere die übergebenen bestehenden Anforderungen. Verstehe den Kontext und die Struktur.

PHASE 3 (Erstellung): Verbessere jede einzelne Anforderung inhaltlich (SMART, Normen, Präzision). Behalte die Struktur bei, aber optimiere den Inhalt.

PHASE 4 (Review): Führe einen Qualitätscheck durch - jede Anforderung muss präzise, messbar und normenkonform sein.

WICHTIG: Antworte nur mit den verbesserten Anforderungen im geforderten JSON-Format. Kein zusätzlicher Text."""
    else:
        system_prompt = """Du bist ein erfahrener Requirements Engineer. Arbeite nach dem 4-Phasen-Modell:

PHASE 1 & 2 (Analyse/Struktur): Verstehe den Kontext und strukturiere die Anforderungen.

PHASE 3 (Erstellung): Formuliere Anforderungen nach der Satzschablone "Das System muss...". Stelle sicher, dass sie SMART, normenkonform und präzise sind.

PHASE 4 (Review): Qualitätscheck - jede Anforderung muss messbar, akzeptabel und testbar sein.

WICHTIG: Antworte nur mit den generierten Anforderungen im geforderten JSON-Format. Kein zusätzlicher Text."""

    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable must be set.")

    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)

    # Build user message from user_description and inputs
    user_message_parts = []
    
    if user_description and user_description.strip():
        user_message_parts.append(f"Beschreibung: {user_description.strip()}")
    
    if inputs:
        user_message_parts.append("\nZusätzliche Informationen:")
        for key, value in inputs.items():
            if key and value:
                user_message_parts.append(f"- {key}: {value}")
    
    if not user_message_parts:
        user_message = "Bitte generiere allgemeine Software-Anforderungen."
    else:
        user_message = "\n".join(user_message_parts)

    # Build developer message with dynamic JSON schema
    if columns and isinstance(columns, list):
        # Build JSON structure based on columns
        json_fields = []
        for col in columns:
            col_lower = col.lower()
            if col_lower in ['titel', 'title']:
                json_fields.append(f'      "{col}": "Kurzer, prägnanter Titel"')
            elif col_lower in ['beschreibung', 'description']:
                json_fields.append(f'      "{col}": "Detaillierte Beschreibung mit Akzeptanzkriterien"')
            elif col_lower in ['kategorie', 'category']:
                json_fields.append(f'      "{col}": "Kategorie (z.B. Funktional, Nicht-Funktional, etc.)"')
            elif col_lower in ['status']:
                json_fields.append(f'      "{col}": "Offen"')
            else:
                json_fields.append(f'      "{col}": "Passender Wert für {col}"')
        
        json_example = "{\n" + ",\n".join(json_fields) + "\n    }"
        
        developer_message = f"""Du musst ausschließlich mit gültigem JSON antworten.
Das JSON-Format muss exakt dieser Struktur folgen:
{{
  "requirements": [
    {json_example}
  ]
}}

Wichtig: Fülle ALLE Spalten ({', '.join(columns)}) mit sinnvollen Werten.
Antworte NUR mit diesem JSON, ohne zusätzlichen Text davor oder danach."""
    else:
        # Fallback to default structure
        developer_message = """Du musst ausschließlich mit gültigem JSON antworten.
Das JSON-Format muss exakt dieser Struktur folgen:
{
  "requirements": [
    {
      "title": "Kurzer, prägnanter Titel",
      "description": "Detaillierte Beschreibung mit Akzeptanzkriterien",
      "category": "Kategorie (z.B. Funktional, Nicht-Funktional, etc.)",
      "status": "Offen"
    }
  ]
}

Antworte NUR mit diesem JSON, ohne zusätzlichen Text davor oder danach."""

    try:
        # Call OpenAI Chat Completions API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "developer", "content": developer_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2,
            max_tokens=1200
        )

        # Extract response content
        response_text = response.choices[0].message.content.strip()

        # Parse JSON response
        requirements = _parse_json_response(response_text, columns)
        
        return requirements

    except Exception as e:
        raise RuntimeError(f"OpenAI request failed: {str(e)}")


def _parse_json_response(response_text: str, columns: list = None) -> list[dict]:
    """
    Robustly parse JSON response from OpenAI, with fallback to regex extraction.

    Args:
        response_text (str): Raw response text from OpenAI.
        columns (list): Optional list of column names for validation.

    Returns:
        list[dict]: List of validated and normalized requirement dicts.
    
    Raises:
        RuntimeError: If JSON cannot be parsed or is invalid.
    """
    # Try direct JSON parsing first
    try:
        data = json.loads(response_text)
        if isinstance(data, dict) and "requirements" in data:
            return _validate_and_normalize_requirements(data["requirements"], columns)
    except json.JSONDecodeError:
        pass

    # Fallback: Extract JSON block using regex
    # Look for JSON object that contains "requirements"
    json_pattern = r'\{[^{}]*"requirements"[^{}]*\[[^\]]*\][^{}]*\}'
    # More robust pattern that handles nested structures
    json_pattern = r'\{(?:[^{}]|\{[^{}]*\})*"requirements"(?:[^{}]|\{[^{}]*\})*\[(?:[^\[\]]|\[[^\[\]]*\])*\](?:[^{}]|\{[^{}]*\})*\}'
    
    matches = re.findall(json_pattern, response_text, re.DOTALL)
    
    for match in matches:
        try:
            data = json.loads(match)
            if isinstance(data, dict) and "requirements" in data:
                return _validate_and_normalize_requirements(data["requirements"], columns)
        except json.JSONDecodeError:
            continue

    # If still no valid JSON found, try to extract just the array
    array_pattern = r'\[\s*\{[^\]]+\}\s*\]'
    array_matches = re.findall(array_pattern, response_text, re.DOTALL)
    
    for match in array_matches:
        try:
            data = json.loads(match)
            if isinstance(data, list):
                return _validate_and_normalize_requirements(data, columns)
        except json.JSONDecodeError:
            continue

    raise RuntimeError("Invalid JSON response from model: Could not parse requirements structure.")


def _validate_and_normalize_requirements(requirements: list, columns: list = None) -> list[dict]:
    """
    Validate and normalize requirements list with support for dynamic columns.

    Args:
        requirements (list): Raw requirements list from parsed JSON.
        columns (list): Optional list of column names to validate against.

    Returns:
        list[dict]: Validated and normalized requirements.
    
    Raises:
        RuntimeError: If requirements structure is invalid.
    """
    if not isinstance(requirements, list):
        raise RuntimeError("Requirements must be a list.")

    normalized = []
    
    for req in requirements:
        if not isinstance(req, dict):
            continue
        
        # If columns are provided, use them for validation
        if columns and isinstance(columns, list):
            normalized_req = {}
            has_required_data = False
            
            for col in columns:
                value = req.get(col, "").strip()
                normalized_req[col] = value
                
                # Check if we have at least some meaningful data
                if value:
                    has_required_data = True
            
            # Only add if we have at least some data
            if has_required_data:
                normalized.append(normalized_req)
        else:
            # Fallback to default validation (backward compatibility)
            title = req.get("title", "").strip()
            description = req.get("description", "").strip()
            
            if not title or not description:
                continue  # Skip invalid requirements
            
            # Set defaults for optional fields
            category = req.get("category", "").strip()
            status = req.get("status", "Offen").strip()
            
            # Ensure status is "Offen" as per requirements
            if status != "Offen":
                status = "Offen"
            
            normalized.append({
                "title": title,
                "description": description,
                "category": category,
                "status": status
            })
    
    if not normalized:
        raise RuntimeError("No valid requirements found in response.")
    
    # Limit to maximum 10 requirements
    return normalized[:10]
