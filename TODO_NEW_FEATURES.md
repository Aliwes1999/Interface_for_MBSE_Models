# TODO: New Features Implementation

## Completed ✅

### Task 1: Display ID (Sequential 1, 2, 3...)

- ✅ Updated create.html to show `loop.index` instead of `req.id`
- ✅ Internal operations still use `req.id`

### Task 2: Navigation Buttons

- ✅ Added "KI-Agent öffnen" button on project page
- ✅ Added "Zurück zum Projekt" button on AI agent page

### Task 3: Dynamic Columns in AI Generation

- ✅ Updated agent.py to get project's custom columns
- ✅ Pass custom columns to AI client
- ✅ Save custom column data in RequirementVersion
- ✅ Updated regenerate_requirement to use custom columns
- ✅ Save custom data from AI response in regeneration

## In Progress 🔄

### Task 4: Delete Only Displayed Version

- ⏳ Need to create new route: `delete_requirement_version(version_id)`
- ⏳ Update delete button in template to pass version_id
- ⏳ Update JavaScript to track current version_id

### Task 5: Excel Export

- ⏳ Create new route: `export_excel(project_id)`
- ⏳ Add export button in template
- ⏳ Implement Excel generation with openpyxl

## Next Steps

1. Implement version-specific delete functionality
2. Implement Excel export feature
3. Test all features thoroughly
4. Document changes
