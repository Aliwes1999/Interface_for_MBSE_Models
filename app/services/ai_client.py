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

def generate_new_requirements(user_description: str | None, inputs: dict, columns: list = None) -> list[dict]:
    """
    Generate COMPLETELY NEW requirements from scratch using AI.
    Used for: "Neue Anforderungen generieren" button

    Args:
        user_description (str | None): Optional user description of requirements.
        inputs (dict): Key-value pairs for additional context.
        columns (list): Optional list of column names for the project.

    Returns:
        list[dict]: List of requirement dicts with dynamic columns based on project.
    """
    api_key = config.OPENAI_API_KEY
    model = config.OPENAI_MODEL or "gpt-4o-mini"

    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable must be set.")

    # System prompt for NEW generation
    system_prompt = """Du bist ein erfahrener Requirements Engineer. Arbeite nach dem 4-Phasen-Modell:

PHASE 1 & 2 (Analyse/Struktur): Verstehe den Kontext und strukturiere die Anforderungen logisch.

PHASE 3 (Erstellung): Formuliere NEUE Anforderungen nach der Satzschablone "Das System muss...". 
Stelle sicher, dass sie SMART, normenkonform und präzise sind.

PHASE 4 (Review): Qualitätscheck - jede Anforderung muss messbar, akzeptabel und testbar sein.

WICHTIG: Antworte nur mit den generierten Anforderungen im geforderten JSON-Format. Kein zusätzlicher Text."""

    client = OpenAI(api_key=api_key)

    # Build user message
    user_message_parts = []
    if user_description and user_description.strip():
        user_message_parts.append(f"Beschreibung: {user_description.strip()}")
    
    if inputs:
        user_message_parts.append("\nZusätzliche Informationen:")
        for key, value in inputs.items():
            if key and value:
                user_message_parts.append(f"- {key}: {value}")
    
    user_message = "\n".join(user_message_parts) if user_message_parts else "Bitte generiere allgemeine Software-Anforderungen."

    # Build developer message
    if columns and isinstance(columns, list):
        json_fields = [f'      "{col}": "Passender Wert für {col}"' for col in columns]
        json_example = "{\n" + ",\n".join(json_fields) + "\n    }"
        
        developer_message = f"""Du musst ausschließlich mit gültigem JSON antworten.
Das JSON-Format muss exakt dieser Struktur folgen:
{{
  "requirements": [
    {json_example}
  ]
}}

WICHTIG: 
- Verwende EXAKT diese Spaltennamen: {', '.join(columns)}
- Fülle ALLE Spalten mit sinnvollen Werten
- Behalte die Struktur und Spaltennamen EXAKT bei
- Generiere MINDESTENS 5 verschiedene Anforderungen
- Antworte NUR mit diesem JSON, ohne zusätzlichen Text davor oder danach."""
    else:
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

WICHTIG:
- Generiere MINDESTENS 5 verschiedene Anforderungen
- Antworte NUR mit diesem JSON, ohne zusätzlichen Text davor oder danach."""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "developer", "content": developer_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2,
            max_tokens=2000
        )

        response_text = response.choices[0].message.content.strip()
        requirements = _parse_json_response(response_text, columns)
        return requirements

    except Exception as e:
        raise RuntimeError(f"OpenAI request failed: {str(e)}")


def optimize_excel_requirements(existing_requirements: list[dict], columns: list, user_description: str | None = None) -> list[dict]:
    """
    Optimize and improve EXISTING requirements from Excel file using AI.
    Used for: Excel file upload with AI optimization

    Args:
        existing_requirements (list[dict]): Existing requirements from Excel
        columns (list): Column names from the Excel file
        user_description (str | None): Optional additional context

    Returns:
        list[dict]: Optimized requirements maintaining Excel structure
    """
    api_key = config.OPENAI_API_KEY
    model = config.OPENAI_MODEL or "gpt-4o-mini"

    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable must be set.")

    # System prompt for OPTIMIZATION
    system_prompt = """Du bist ein erfahrener Requirements Engineer. Arbeite nach dem 4-Phasen-Modell:

PHASE 1 & 2 (Analyse/Struktur): Analysiere die übergebenen bestehenden Anforderungen aus der Excel-Datei. 
Verstehe den Kontext und die vorhandene Struktur.

PHASE 3 (Optimierung): Verbessere jede einzelne Anforderung inhaltlich:
- Präzisiere die Formulierung
- Stelle SMART-Kriterien sicher
- Verbessere Normenkonformität
- BEHALTE die Anzahl der Anforderungen GLEICH (keine neuen hinzufügen!)
- BEHALTE die Spaltenstruktur EXAKT bei

PHASE 4 (Review): Qualitätscheck - jede Anforderung muss präzise, messbar und normenkonform sein.

WICHTIG: Antworte nur mit den OPTIMIERTEN Anforderungen im gleichen JSON-Format. Kein zusätzlicher Text."""

    client = OpenAI(api_key=api_key)

    # Build user message
    user_message_parts = []
    user_message_parts.append("Bestehende Anforderungen aus Excel-Datei (bitte optimieren und verbessern):")
    user_message_parts.append(json.dumps(existing_requirements, ensure_ascii=False, indent=2))
    
    if user_description and user_description.strip():
        user_message_parts.append(f"\nZusätzliche Hinweise zur Optimierung: {user_description.strip()}")
    
    user_message = "\n".join(user_message_parts)

    # Build developer message
    json_fields = [f'      "{col}": "Optimierter Wert für {col}"' for col in columns]
    json_example = "{\n" + ",\n".join(json_fields) + "\n    }"
    
    developer_message = f"""Du musst ausschließlich mit gültigem JSON antworten.
Das JSON-Format muss exakt dieser Struktur folgen:
{{
  "requirements": [
    {json_example}
  ]
}}

KRITISCH WICHTIG: 
- Verwende EXAKT diese Spaltennamen: {', '.join(columns)}
- KEINE zusätzlichen Spalten hinzufügen
- KEINE Spalten entfernen
- Behalte die GLEICHE ANZAHL an Anforderungen wie im Input
- Optimiere nur den INHALT, nicht die Struktur
- Antworte NUR mit diesem JSON, ohne zusätzlichen Text davor oder danach."""

    try:
        print(f"DEBUG optimize_excel_requirements: columns={columns}")
        print(f"DEBUG optimize_excel_requirements: input count={len(existing_requirements)}")
        if existing_requirements:
            print(f"DEBUG optimize_excel_requirements: first item sample={existing_requirements[0]}")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "developer", "content": developer_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2,
            max_tokens=3000  # Increased for larger Excel files
        )

        response_text = response.choices[0].message.content.strip()
        print(f"DEBUG optimize_excel_requirements: AI response length={len(response_text)}")
        print(f"DEBUG optimize_excel_requirements: AI response preview={response_text[:200] if len(response_text) > 200 else response_text}")
        
        requirements = _parse_json_response(response_text, columns)
        print(f"DEBUG optimize_excel_requirements: output count={len(requirements)}")
        return requirements

    except Exception as e:
        print(f"ERROR in optimize_excel_requirements: {str(e)}")
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"OpenAI request failed: {str(e)}")


def generate_requirements(user_description: str | None, inputs: dict, columns: list = None, existing_requirements: list[dict] = None) -> list[dict]:
    """
    DEPRECATED: Use generate_new_requirements() or optimize_excel_requirements() instead.
    This function is kept for backwards compatibility.
    
    Args:
        user_description (str | None): Optional user description of requirements.
        inputs (dict): Key-value pairs for additional context.
        columns (list): Optional list of column names for the project.
        existing_requirements (list[dict]): Optional list of existing requirements to optimize.

    Returns:
        list[dict]: List of requirement dicts with dynamic columns based on project.
    """
    if existing_requirements:
        return optimize_excel_requirements(existing_requirements, columns, user_description)
    else:
        return generate_new_requirements(user_description, inputs, columns)


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
    
    return normalized
