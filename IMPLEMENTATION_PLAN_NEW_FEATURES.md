# Implementation Plan for New Features

## Information Gathered

### Current System Architecture:

1. **Models** (app/models.py):

   - `Project`: Has `custom_columns` (JSON field) for dynamic columns
   - `Requirement`: Logical requirement with `is_deleted` flag for soft delete
   - `RequirementVersion`: Versioned data with `custom_data` (JSON field) for dynamic column values
   - Versioning system: A, B, C labels based on `version_index`

2. **Routes** (app/routes.py):

   - Project management with dynamic columns (add/remove)
   - Requirement CRUD operations
   - Version switching via AJAX
   - Soft delete with `is_deleted` flag
   - Single requirement regeneration

3. **AI Agent** (app/agent.py):

   - Generates requirements using OpenAI
   - Creates versioned entries
   - Currently uses fixed columns: ["title", "description", "category", "status"]

4. **AI Client** (app/services/ai_client.py):

   - Calls OpenAI API
   - Supports dynamic columns in prompt generation
   - Parses JSON responses

5. **Templates**:
   - create.html: Project page with requirements table
   - agent/agent.html: AI generation page
   - Dynamic column display and editing already implemented

### Current Issues to Fix:

1. **Dynamic Columns NOT in AI Generation**:

   - Agent passes fixed columns to AI client
   - Custom column values not saved during AI generation
   - Single regeneration doesn't use project columns

2. **Display ID shows DB ID**:

   - Table shows `req.id` instead of sequential 1, 2, 3...

3. **Delete removes ALL versions**:

   - Current delete marks entire Requirement as deleted
   - Should only delete the displayed version

4. **Missing Navigation**:

   - No button from project page to AI agent page
   - No button from AI agent page back to project

5. **No Excel Export**:
   - Feature completely missing

## Detailed Implementation Plan

### Task 1: Dynamic Columns in AI Generation

**Files to modify:**

- `app/agent.py`: Pass project's custom columns to AI
- `app/routes.py`: Update regenerate_requirement to use custom columns
- `app/services/ai_client.py`: Already supports dynamic columns (verify)

**Changes:**

1.1. **app/agent.py - generate() function**:

- Get project's custom columns: `custom_columns = project.get_custom_columns()`
- Build complete columns list: `columns = ["title", "description"] + custom_columns + ["category", "status"]`
- Pass to `generate_requirements()`
- Parse returned data including custom fields
- Save custom fields to `RequirementVersion.custom_data`

1.2. **app/routes.py - regenerate_requirement() function**:

- Get project's custom columns
- Build columns list same as above
- Pass to AI generation
- Save custom fields to new version

1.3. **Verify ai_client.py**:

- Already supports dynamic columns via `columns` parameter
- System prompt generation includes custom columns
- JSON parsing handles dynamic fields

### Task 2: Display ID (Sequential 1, 2, 3...)

**Files to modify:**

- `app/templates/create.html`: Change ID display from `req.id` to `loop.index`

**Changes:**

2.1. **Template change**:

- Replace `<td>{{ req.id }}</td>` with `<td>{{ loop.index }}</td>`
- Keep `data-req-id="{{ req.id }}"` for internal operations
- All buttons/forms continue using `req.id` for backend operations

### Task 3: Delete Only Displayed Version

**Files to modify:**

- `app/routes.py`: New route `delete_requirement_version()`
- `app/templates/create.html`: Update delete button to pass version_id

**Changes:**

3.1. **New route: delete_requirement_version(version_id)**:

- Get RequirementVersion by ID
- Authorization check
- Delete this specific version
- Check if requirement has other versions:
  - If yes: Keep requirement active
  - If no: Mark requirement as deleted (`is_deleted = True`)
- Return success

3.2. **Update delete button in template**:

- Change form action to use version_id instead of req_id
- Pass currently displayed version_id
- Update JavaScript to track current version_id

3.3. **JavaScript updates**:

- Track currently displayed version_id per row
- Update delete button's version_id when version changes

### Task 4: Navigation Buttons

**Files to modify:**

- `app/templates/create.html`: Add button to AI agent page
- `app/templates/agent/agent.html`: Add button back to project

**Changes:**

4.1. **Project page (create.html)**:

- Add button near "Zurück zur Startseite"
- Link to: `url_for('agent.agent_page', project_id=project.id)`
- Text: "KI-Agent öffnen" with icon

4.2. **AI agent page (agent.html)**:

- Add button at top
- Link to: `url_for('main.manage_project', project_id=project.id)`
- Text: "Zurück zum Projekt" with icon

### Task 5: Excel Export

**Files to modify:**

- `app/routes.py`: New route `export_excel(project_id)`
- `app/templates/create.html`: Add export button

**Changes:**

5.1. **New route: export_excel(project_id)**:

- Get project and verify ownership
- Get custom columns
- Get all non-deleted requirements with latest versions
- Create Excel workbook with openpyxl:
  - Headers: Version, ID, Title, Beschreibung, [custom columns], Kategorie, Status
  - Data rows with sequential IDs (1, 2, 3...)
  - Format: wrap_text for description, column widths, bold headers
- Return as download with filename: `requirements_{project.name}.xlsx`

5.2. **Add export button in template**:

- Place near column configuration section
- Link to export route
- Icon + "Export als Excel"

## Dependencies

- openpyxl: Already in requirements.txt ✓
- All other dependencies already present ✓

## Testing Plan

After each task:

1. Start Flask app: `flask run`
2. Create/open a project
3. Add dynamic columns (e.g., "Farbe", "Priorität", "Material")
4. Test AI generation - verify custom columns are filled
5. Test version switching
6. Test delete (only version, not all)
7. Test navigation buttons
8. Test Excel export
9. Check for errors in console/logs

## Rollback Strategy

- Keep backups of modified files
- Test each change incrementally
- If issues arise, revert specific file changes
- Database schema unchanged (no migrations needed)

## Implementation Order

1. Task 2 (Display ID) - Simplest, no backend changes
2. Task 4 (Navigation) - Simple template changes
3. Task 1 (Dynamic Columns in AI) - Core functionality
4. Task 3 (Delete Version) - Requires careful logic
5. Task 5 (Excel Export) - Independent feature

This order minimizes risk and allows testing incrementally.
