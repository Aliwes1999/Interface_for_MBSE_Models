import os
import json
import re
import sys
from pathlib import Path
from openai import OpenAI

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import config

def generate_requirements(user_description: str | None, inputs: dict) -> list[dict]:
    """
    Calls OpenAI API to generate requirements based on user description and inputs.

    Args:
        user_description (str | None): Optional user description of requirements.
        inputs (dict): Key-value pairs for additional context.

    Returns:
        list[dict]: List of requirement dicts with 'title', 'description', 'category', 'status'.
    
    Raises:
        ValueError: If OPENAI_API_KEY is not set.
        RuntimeError: If OpenAI API call fails or response is invalid.
    """
    # Get configuration
    api_key = config.OPENAI_API_KEY
    model = config.OPENAI_MODEL or "gpt-4o-mini"
    system_prompt = config.get_system_prompt()

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

    # Developer message with JSON schema
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
        requirements = _parse_json_response(response_text)
        
        return requirements

    except Exception as e:
        raise RuntimeError(f"OpenAI request failed: {str(e)}")


def _parse_json_response(response_text: str) -> list[dict]:
    """
    Robustly parse JSON response from OpenAI, with fallback to regex extraction.

    Args:
        response_text (str): Raw response text from OpenAI.

    Returns:
        list[dict]: List of validated and normalized requirement dicts.
    
    Raises:
        RuntimeError: If JSON cannot be parsed or is invalid.
    """
    # Try direct JSON parsing first
    try:
        data = json.loads(response_text)
        if isinstance(data, dict) and "requirements" in data:
            return _validate_and_normalize_requirements(data["requirements"])
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
                return _validate_and_normalize_requirements(data["requirements"])
        except json.JSONDecodeError:
            continue

    # If still no valid JSON found, try to extract just the array
    array_pattern = r'\[\s*\{[^\]]+\}\s*\]'
    array_matches = re.findall(array_pattern, response_text, re.DOTALL)
    
    for match in array_matches:
        try:
            data = json.loads(match)
            if isinstance(data, list):
                return _validate_and_normalize_requirements(data)
        except json.JSONDecodeError:
            continue

    raise RuntimeError("Invalid JSON response from model: Could not parse requirements structure.")


def _validate_and_normalize_requirements(requirements: list) -> list[dict]:
    """
    Validate and normalize requirements list.

    Args:
        requirements (list): Raw requirements list from parsed JSON.

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
        
        # Extract and validate required fields
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
