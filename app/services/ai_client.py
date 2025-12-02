import os
import json
import re
import sys
from pathlib import Path
from openai import OpenAI

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import config

def generate_requirements(machine: str | None = None, user_description: str | None = None, inputs: dict = None, user_columns: dict = None, columns: list = None) -> list[dict]:
    """
    Calls OpenAI API to generate requirements based on machine, user description, inputs, and user-defined columns.

    Args:
        machine (str | None): Optional machine/system identifier.
        user_description (str | None): Optional user description of requirements.
        inputs (dict): Key-value pairs for additional context.
        user_columns (dict): User-defined columns with their values/examples.
        columns (list): Optional list of column names for the project.

    Returns:
        list[dict]: List of requirement dicts with dynamic columns based on project.
    
    Raises:
        ValueError: If OPENAI_API_KEY is not set.
        RuntimeError: If OpenAI API call fails or response is invalid.
    """
    if inputs is None:
        inputs = {}
    if user_columns is None:
        user_columns = {}
    
    # Get configuration
    api_key = config.OPENAI_API_KEY
    model = config.OPENAI_MODEL or "gpt-4o-mini"
    system_prompt = config.get_system_prompt(columns)

    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable must be set.")

    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)

    # Build user message from machine, user_description, user_columns and inputs
    user_message_parts = []
    
    if machine and machine.strip():
        user_message_parts.append(f"Maschine/System: {machine.strip()}")
    
    if user_description and user_description.strip():
        user_message_parts.append(f"Beschreibung: {user_description.strip()}")
    
    if user_columns:
        user_message_parts.append("\nBenutzerdefinierte Spalten:")
        for name, value in user_columns.items():
            if name and name.strip():
                value_str = value.strip() if value else ""
                if value_str:
                    user_message_parts.append(f"- {name.strip()}: {value_str}")
                else:
                    user_message_parts.append(f"- {name.strip()}")
    
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
