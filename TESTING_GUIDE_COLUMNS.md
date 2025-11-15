# Testing Guide - Column Management & AI Integration

## Quick Start Testing

### Prerequisites
- Application running locally
- User account created and logged in
- At least one project created
- OpenAI API key configured in `.env`

## Test Scenarios

### Scenario 1: Basic Column Management

#### Test 1.1: View Current Columns
1. Navigate to a project
2. Look for "Aktuelle Spalten:" section
3. **Expected**: See all columns with badges
   - Blue badges with 🔒 for fixed columns (ID, Titel, Beschreibung)
   - Gray badges with × for custom columns

#### Test 1.2: Add Custom Column
1. Enter "Priority" in "Neue Spaltenname" field
2. Click "Spalte hinzufügen"
3. **Expected**: 
   - Page refreshes
   - "Priority" appears in column list (gray badge with ×)
   - "Priority" appears as header in all tables
   - New requirement form includes "Priority" field

#### Test 1.3: Try to Delete Fixed Column
1. Look at fixed columns (ID, Titel, Beschreibung)
2. **Expected**: No × button, only 🔒 icon
3. Verify hint text: "Feste Spalten (ID, Titel, Beschreibung) können nicht gelöscht werden"

#### Test 1.4: Delete Custom Column
1. Click × on a custom column (e.g., "Priority")
2. **Expected**: Confirmation dialog appears
3. Click "OK" to confirm
4. **Expected**:
   - Success message: "Spalte 'Priority' wurde erfolgreich gelöscht"
   - Column removed from column list
   - Column removed from all table headers
   - Data in that column removed from all requirements

### Scenario 2: AI Integration with Custom Columns

#### Test 2.1: AI Generation with Default Columns
1. Create new project (has default columns: Title, Beschreibung, Kategorie, Status)
2. Click "KI-Agent" button
3. Enter description: "Create a login system"
4. Click "Generieren"
5. **Expected**:
   - Success message with count
   - Requirements appear in "Erstellt" table
   - All default columns filled with appropriate content

#### Test 2.2: AI Generation with Custom Columns
1. Add custom columns: "Priority", "Effort", "Risk"
2. Navigate to KI-Agent
3. Enter description: "Create a user management system"
4. Add key-value pair: "Type" → "Web Application"
5. Click "Generieren"
6. **Expected**:
   - Requirements generated successfully
   - ALL columns filled (including Priority, Effort, Risk)
   - Custom columns have appropriate values

#### Test 2.3: AI with Many Custom Columns
1. Add 5+ custom columns with various names
2. Use KI-Agent to generate requirements
3. **Expected**:
   - AI recognizes all columns
   - All columns filled with relevant content
   - No errors or missing data

### Scenario 3: Data Consistency

#### Test 3.1: Column Deletion with Existing Data
1. Add custom column "TestColumn"
2. Create several requirements with data in "TestColumn"
3. Move some requirements to different tables (intermediate, saved)
4. Delete "TestColumn"
5. **Expected**:
   - Column deleted successfully
   - Data removed from ALL tables (created, intermediate, saved, deleted)
   - No orphaned data

#### Test 3.2: AI After Column Changes
1. Generate requirements with AI
2. Add new custom column
3. Generate more requirements with AI
4. **Expected**:
   - New requirements include the new column
   - Old requirements don't have the new column (expected behavior)
   - No errors

### Scenario 4: Edge Cases

#### Test 4.1: Empty Column Name
1. Leave column name field empty
2. Click "Spalte hinzufügen"
3. **Expected**: Form validation prevents submission

#### Test 4.2: Duplicate Column Name
1. Add column "Test"
2. Try to add "Test" again
3. **Expected**: Column not added (already exists check)

#### Test 4.3: Special Characters in Column Name
1. Add column with special characters: "Test-Column_123"
2. **Expected**: Column added successfully
3. Use in AI generation
4. **Expected**: Works correctly

#### Test 4.4: AI with No Description
1. Navigate to KI-Agent
2. Leave description empty
3. Add only key-value pairs
4. Click "Generieren"
5. **Expected**: AI generates requirements based on key-value pairs

#### Test 4.5: AI with No Input
1. Navigate to KI-Agent
2. Leave everything empty
3. Click "Generieren"
4. **Expected**: AI generates general requirements

## Expected Results Summary

### Column Management
✅ Fixed columns cannot be deleted
✅ Custom columns can be deleted with confirmation
✅ Column deletion removes data from all tables
✅ Visual distinction between fixed and custom columns
✅ User feedback for all operations

### AI Integration
✅ AI recognizes all project columns
✅ AI generates content for custom columns
✅ Dynamic prompts based on columns
✅ All columns filled in generated requirements
✅ Works with any number of custom columns

## Common Issues & Solutions

### Issue: Column not appearing after adding
**Solution**: Refresh the page or check for error messages

### Issue: AI not filling custom columns
**Solution**: 
- Verify OpenAI API key is set
- Check column names are valid
- Review server logs for errors

### Issue: Cannot delete column
**Solution**: 
- Check if it's a fixed column (ID, Titel, Beschreibung)
- Verify you're the project owner
- Check for error messages

### Issue: AI generation fails
**Solution**:
- Verify OpenAI API key in `.env`
- Check internet connection
- Review error message for details
- Check server logs

## Performance Testing

### Load Testing
1. Create project with 20+ custom columns
2. Add 50+ requirements
3. Delete multiple columns
4. Generate requirements with AI
5. **Expected**: All operations complete without timeout

### Stress Testing
1. Rapidly add/delete columns
2. Generate multiple AI requests
3. **Expected**: System remains stable

## Browser Compatibility

Test in:
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari

## Reporting Issues

When reporting issues, include:
1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Browser and version
5. Error messages (if any)
6. Screenshots (if applicable)

## Success Criteria

All tests pass if:
- ✅ Fixed columns are protected
- ✅ Custom columns can be added and deleted
- ✅ AI recognizes and fills all columns
- ✅ Data consistency maintained
- ✅ No errors in console or logs
- ✅ User feedback is clear and helpful

---

**Testing Status**: Ready for Testing
**Last Updated**: Today
**Version**: 1.0
