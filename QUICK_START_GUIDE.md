# Quick Start Guide - AI Agent Testing

## ✅ Prerequisites (Already Done)

- [x] Dependencies installed (`pip install -r requirements.txt`)
- [x] `.env` file created with OpenAI API key
- [x] All code changes implemented

## 🚀 Start the Application

```bash
python main.py
```

The application should start on `http://127.0.0.1:5000`

## 🧪 Testing Steps

### 1. Login

- Navigate to `http://127.0.0.1:5000`
- Login with your credentials
- If you don't have an account, register first

### 2. Navigate to a Project

- Go to your projects list
- Select any existing project
- Or create a new project if needed

### 3. Open AI Agent

- Click the "KI-Agent" button on the project page
- You should see the new interface with:
  - ✅ "User-Beschreibung (optional)" field (NOT required)
  - ✅ Key-Value pairs section
  - ❌ NO "System Prompt" field (removed)

### 4. Test Scenarios

#### Test 1: Only User Description

1. Enter in "User-Beschreibung":
   ```
   Erstelle Requirements für eine Benutzeranmeldung mit E-Mail und Passwort
   ```
2. Leave Key-Value pairs empty
3. Click "Generieren"
4. Expected: Requirements generated and saved

#### Test 2: Only Key-Value Pairs

1. Leave "User-Beschreibung" empty
2. Add Key-Value pairs:
   - Key: `System`, Value: `Web-Anwendung`
   - Key: `Technologie`, Value: `Flask, Python`
   - Key: `Zielgruppe`, Value: `Entwickler`
3. Click "Generieren"
4. Expected: Requirements generated based on key-value context

#### Test 3: Both Description and Key-Value Pairs

1. Enter in "User-Beschreibung":
   ```
   Erstelle Requirements für ein Dashboard mit Datenvisualisierung
   ```
2. Add Key-Value pairs:
   - Key: `Diagrammtypen`, Value: `Balken, Linien, Kreisdiagramme`
   - Key: `Datenquelle`, Value: `REST API`
3. Click "Generieren"
4. Expected: Comprehensive requirements generated

#### Test 4: Empty Form

1. Leave everything empty
2. Click "Generieren"
3. Expected: General requirements generated (no error)

### 5. Verify Results

After each test, verify:

- ✅ Success message appears: "Erfolg! N Requirement(s) wurden erfolgreich generiert und gespeichert."
- ✅ Auto-redirect to project page after 2 seconds
- ✅ Requirements appear in the project list
- ✅ Each requirement has:
  - Title (short and clear)
  - Description (detailed with acceptance criteria)
  - Category (e.g., "Funktional", "Nicht-Funktional")
  - Status = "Offen"

### 6. Error Testing

#### Test Invalid API Key (Optional)

1. Stop the application
2. Edit `.env` and change `OPENAI_API_KEY` to an invalid value
3. Restart application
4. Try to generate requirements
5. Expected: User-friendly error message displayed

#### Test Network Issues (Optional)

1. Disconnect internet
2. Try to generate requirements
3. Expected: Error message about connection failure

## 🎯 Expected Behavior Summary

### Success Flow:

```
User Input → Loading Spinner → API Call → Requirements Saved → Success Alert → Auto-Redirect (2s) → Project Page
```

### Error Flow:

```
User Input → Loading Spinner → API Error → Error Alert → User Can Retry
```

## 📊 What to Look For

### ✅ Good Signs:

- No "System Prompt" field in UI
- "User-Beschreibung" is optional (no red asterisk)
- Requirements are generated even with empty form
- Status is always "Offen"
- Clear, testable requirements with good descriptions
- Smooth redirect after success

### ❌ Issues to Report:

- System Prompt field still visible
- User description marked as required
- Error when form is empty
- Requirements not saved to database
- No redirect after success
- Status not set to "Offen"

## 🔍 Debugging

### Check Console Logs

- Open browser Developer Tools (F12)
- Check Console tab for JavaScript errors
- Check Network tab for API calls

### Check Terminal Output

- Look for Python errors in terminal where app is running
- Check for OpenAI API errors
- Verify environment variables are loaded

### Common Issues:

**"OPENAI_API_KEY environment variable must be set"**

- Solution: Verify `.env` file exists and contains the API key
- Restart the application after creating/editing `.env`

**"OpenAI request failed"**

- Solution: Check internet connection
- Verify API key is valid
- Check OpenAI service status

**"Invalid JSON response from model"**

- Solution: This is rare, but if it happens, try again
- The robust parsing should handle most cases

## 📝 Test Results Template

Use this to document your testing:

```
Test Date: ___________
Tester: ___________

Test 1 - Only User Description:
[ ] Success
[ ] Requirements generated: ___ count
[ ] Status = "Offen": Yes/No
[ ] Redirect worked: Yes/No
Notes: ___________

Test 2 - Only Key-Value Pairs:
[ ] Success
[ ] Requirements generated: ___ count
[ ] Status = "Offen": Yes/No
[ ] Redirect worked: Yes/No
Notes: ___________

Test 3 - Both Description and Key-Value:
[ ] Success
[ ] Requirements generated: ___ count
[ ] Status = "Offen": Yes/No
[ ] Redirect worked: Yes/No
Notes: ___________

Test 4 - Empty Form:
[ ] Success
[ ] Requirements generated: ___ count
[ ] Status = "Offen": Yes/No
[ ] Redirect worked: Yes/No
Notes: ___________

Overall Assessment:
[ ] All tests passed
[ ] Some issues found (describe below)
[ ] Major issues (describe below)

Issues/Notes:
___________
```

## 🎉 Success Criteria

The refactoring is successful if:

- ✅ All 4 test scenarios work correctly
- ✅ Requirements are saved with status "Offen"
- ✅ Auto-redirect works after 2 seconds
- ✅ No System Prompt field in UI
- ✅ User description is truly optional
- ✅ Error messages are user-friendly
- ✅ No console errors in browser

## 📞 Support

If you encounter issues:

1. Check the documentation files:
   - `AI_AGENT_REFACTORING_DOCUMENTATION.md`
   - `REFACTORING_SUMMARY.md`
2. Review the code changes in the modified files
3. Check terminal output for error messages
4. Verify `.env` file configuration

Happy Testing! 🚀
