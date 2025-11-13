# AI-Agent Refactoring Documentation

## Overview

This document describes the refactoring of the Flask AI-Agent application to move the System Prompt from the UI to backend configuration and integrate with OpenAI's API.

## Changes Made

### 1. Backend Configuration (`config.py`)

**Status:** ✅ Already properly configured (no changes needed)

The configuration file already includes:

- `OPENAI_API_KEY`: OpenAI API key from environment
- `OPENAI_MODEL`: Model selection (default: "gpt-4o-mini")
- `SYSTEM_PROMPT_PATH`: Optional path to system prompt file
- `SYSTEM_PROMPT`: Optional system prompt string
- `DEFAULT_SYSTEM_PROMPT`: Fallback system prompt with clear instructions
- `get_system_prompt()`: Function to load system prompt with proper fallback logic

### 2. AI Client Service (`app/services/ai_client.py`)

**Status:** ✅ Completely rewritten

**Key Changes:**

- Replaced generic AI endpoint with OpenAI Chat Completions API
- Function signature: `generate_requirements(user_description: str | None, inputs: dict) -> list[dict]`
- System prompt loaded from backend configuration (never from frontend)
- Messages structure:
  - `system`: Backend-configured system prompt
  - `developer`: JSON schema instructions
  - `user`: Combined user_description + serialized inputs
- API parameters:
  - `temperature=0.2` for consistent, focused responses
  - `max_tokens=1200` for adequate response length
- Robust JSON parsing with multiple fallback strategies:
  1. Direct JSON parsing
  2. Regex extraction of JSON blocks
  3. Array extraction as fallback
- Validation and normalization:
  - Ensures all requirements have title and description
  - Sets default values for category ("") and status ("Offen")
  - Filters out invalid entries
- Comprehensive error handling with clear messages

### 3. Agent Routes (`app/agent.py`)

**Status:** ✅ Updated

**Key Changes:**

- **GET route** (`/agent/<int:project_id>`): No changes, already correct
- **POST route** (`/agent/generate/<int:project_id>`):
  - Changed request body structure:
    ```json
    {
      "user_description": "optional string",
      "inputs": [{"key": "...", "value": "..."}, ...]
    }
    ```
  - Removed `system_prompt` from request handling
  - Made `user_description` optional (no validation error if empty)
  - Converts inputs array to dict for AI client
  - Always sets status to "Offen" when saving requirements
  - Returns structured response:
    - Success: `{"ok": true, "count": N, "redirect": "/manage/<project_id>"}`
    - Error: `{"ok": false, "error": "user-readable message"}`
  - Enhanced error handling for different error types:
    - `ValueError`: Configuration errors (missing API key)
    - `RuntimeError`: AI service errors
    - `Exception`: Unexpected errors with rollback

### 4. Frontend Template (`app/templates/agent/agent.html`)

**Status:** ✅ Updated

**Key Changes:**

- **Removed:** Entire "System Prompt" section
- **Renamed:** "User Prompt" → "User-Beschreibung (optional)"
- **Updated:** Removed `required` attribute from user description field
- **Added:** Helper text explaining the optional nature
- **Kept:** Key-Value pairs section unchanged
- **JavaScript updates:**
  - Changed data structure to match new API format
  - Converts Key-Value pairs to array of objects
  - Handles `ok` field in response
  - On success: Shows alert with count and auto-redirects after 2 seconds
  - On error: Shows user-friendly error message from backend
  - Improved error handling for network issues

### 5. Dependencies (`requirements.txt`)

**Status:** ✅ Updated

**Added:**

- `openai>=1.0.0`: Official OpenAI Python SDK
- `python-dotenv`: For loading environment variables from .env file

### 6. Environment Configuration

**Status:** ✅ Created

**Files Created:**

- `.env.example`: Template with documentation for all environment variables
- `.env`: Actual configuration file with provided API key

**Environment Variables:**

```bash
OPENAI_API_KEY=sk-proj-...  # Required
OPENAI_MODEL=gpt-4o-mini    # Optional (default: gpt-4o-mini)
SYSTEM_PROMPT_PATH=...      # Optional (path to custom prompt file)
SYSTEM_PROMPT=...           # Optional (inline prompt string)
```

### 7. Application Entry Point (`main.py`)

**Status:** ✅ Updated

**Changes:**

- Added `from dotenv import load_dotenv`
- Added `load_dotenv()` call before app creation
- Ensures environment variables are loaded from .env file

## Data Flow

### Request Flow:

1. User fills optional "User-Beschreibung" and Key-Value pairs in UI
2. Frontend sends POST to `/agent/generate/<project_id>`:
   ```json
   {
     "user_description": "optional text",
     "inputs": [{"key": "k1", "value": "v1"}, ...]
   }
   ```
3. Backend validates project ownership
4. Backend converts inputs array to dict
5. Backend calls `generate_requirements(user_description, inputs_dict)`
6. AI Client:
   - Loads system prompt from config
   - Builds messages with system/developer/user roles
   - Calls OpenAI API
   - Parses and validates JSON response
   - Returns list of requirement dicts
7. Backend saves requirements to database with status="Offen"
8. Backend returns success response with redirect URL
9. Frontend shows success message and redirects to project page

### Response Flow (Success):

```json
{
  "ok": true,
  "count": 5,
  "redirect": "/manage/123"
}
```

### Response Flow (Error):

```json
{
  "ok": false,
  "error": "Konfigurationsfehler: OPENAI_API_KEY environment variable must be set."
}
```

## Security Considerations

1. **API Key Protection:**

   - API key stored in environment variables (never in code)
   - `.env` file in `.gitignore` (not committed to repository)
   - API key never sent to frontend or logged

2. **Access Control:**

   - All agent routes require `@login_required`
   - Project ownership verified before any operations
   - Returns 403 Forbidden for unauthorized access

3. **Input Validation:**

   - JSON parsing with error handling
   - Input sanitization (strip whitespace)
   - Empty/invalid inputs filtered out

4. **Error Handling:**
   - User-friendly error messages (no sensitive details)
   - Database rollback on errors
   - Proper HTTP status codes

## Testing Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify .env file has correct OPENAI_API_KEY
- [ ] Start application: `python main.py`
- [ ] Login to application
- [ ] Navigate to a project
- [ ] Click "KI-Agent" button
- [ ] Verify UI shows only "User-Beschreibung (optional)" and Key-Value pairs
- [ ] Test with only user description
- [ ] Test with only Key-Value pairs
- [ ] Test with both user description and Key-Value pairs
- [ ] Test with empty form (should still work)
- [ ] Verify requirements are generated and saved
- [ ] Verify redirect to project page after success
- [ ] Verify requirements appear in project with status "Offen"
- [ ] Test error handling (e.g., invalid API key)

## Redirect Behavior

After successful requirement generation:

1. Backend returns `redirect` URL in response: `url_for('main.manage_project', project_id=project_id)`
2. Frontend displays success alert with count
3. After 2 seconds, JavaScript executes: `window.location.href = result.redirect`
4. User is automatically redirected to the project management page where they can see the newly generated requirements

## Default System Prompt

The default system prompt (used when no custom prompt is configured):

```
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
```

## Customizing the System Prompt

### Option 1: Using a File

1. Create a text file (e.g., `app/prompts/system_requirements.txt`)
2. Set environment variable: `SYSTEM_PROMPT_PATH=app/prompts/system_requirements.txt`
3. The prompt will be loaded from this file (UTF-8 encoded)

### Option 2: Using Environment Variable

1. Set environment variable with your prompt:
   ```bash
   SYSTEM_PROMPT="Your custom prompt here..."
   ```

### Option 3: Using Default

1. Don't set either `SYSTEM_PROMPT_PATH` or `SYSTEM_PROMPT`
2. The application will use the built-in `DEFAULT_SYSTEM_PROMPT`

## Troubleshooting

### "OPENAI_API_KEY environment variable must be set"

- Ensure `.env` file exists in project root
- Verify `OPENAI_API_KEY` is set in `.env`
- Restart the application after changing `.env`

### "OpenAI request failed"

- Check API key is valid and not expired
- Verify internet connection
- Check OpenAI service status
- Review API usage limits

### "Invalid JSON response from model"

- Model may have returned text instead of JSON
- Check system prompt is properly configured
- Try increasing `max_tokens` in `ai_client.py`
- Review OpenAI model compatibility

### Requirements not appearing in project

- Check database connection
- Verify project ownership
- Check browser console for JavaScript errors
- Verify redirect URL is correct

## Files Modified

1. ✅ `requirements.txt` - Added openai and python-dotenv
2. ✅ `app/services/ai_client.py` - Complete rewrite with OpenAI integration
3. ✅ `app/agent.py` - Updated POST route for new data structure
4. ✅ `app/templates/agent/agent.html` - Removed System Prompt, updated UI
5. ✅ `main.py` - Added dotenv loading
6. ✅ `.env.example` - Created with documentation
7. ✅ `.env` - Created with actual API key
8. ⚠️ `config.py` - No changes needed (already properly configured)
9. ⚠️ `app/models.py` - No changes needed (Requirement model already correct)

## Summary

The refactoring successfully:

- ✅ Moved System Prompt from UI to backend configuration
- ✅ Integrated OpenAI Chat Completions API
- ✅ Made User Description optional
- ✅ Implemented robust JSON parsing with fallbacks
- ✅ Added comprehensive error handling
- ✅ Maintained security best practices
- ✅ Provided clear user feedback and auto-redirect
- ✅ Documented all changes and configuration options

The application is now ready for testing and deployment!
