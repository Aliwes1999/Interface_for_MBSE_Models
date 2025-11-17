# Requirements Versioning System - Testing Guide

**Purpose**: Step-by-step guide to test the versioning functionality  
**Status**: Ready for Testing  
**Estimated Time**: 15-20 minutes

---

## Prerequisites

1. ✅ Flask application is running
2. ✅ Database has been migrated (if upgrading from old version)
3. ✅ AI service is configured (OpenAI API key in `.env`)
4. ✅ User account exists (or can register)

---

## Test Scenario 1: First Generation (Version A)

### Steps

1. **Login to the application**

   - Navigate to `http://localhost:5000`
   - Login with your credentials

2. **Create a new project**

   - Click "Neues Projekt erstellen"
   - Enter project name: "Test Versioning System"
   - Click "Projekt erstellen"

3. **Navigate to AI Agent**

   - Click on the project "Test Versioning System"
   - You should see an empty requirements table
   - Click the link to the KI-Agent (or navigate to `/agent/<project_id>`)

4. **Generate requirements**

   - In the "User-Beschreibung" field, enter:
     ```
     Create requirements for a simple e-commerce website with user authentication, product catalog, and shopping cart.
     ```
   - Click "Generieren"
   - Wait for the AI to generate requirements

5. **Verify Version A**
   - You should be redirected to the project page
   - Check the requirements table
   - **Expected Result**:
     - ✅ "Version" column appears BEFORE "ID" column
     - ✅ All requirements show badge with "A"
     - ✅ Each requirement has a "Historie" button

### Screenshot Checklist

- [ ] Version column is visible and positioned correctly
- [ ] All version badges show "A"
- [ ] Table displays: Version | ID | Title | Beschreibung | Kategorie | Status | Aktionen

---

## Test Scenario 2: Second Generation (Version B)

### Steps

1. **Return to AI Agent**

   - From the project page, navigate back to the AI Agent
   - Or use the URL: `/agent/<project_id>`

2. **Generate requirements again**

   - Use a slightly different description:
     ```
     Create requirements for an e-commerce website with user authentication, advanced product catalog with search, shopping cart, and payment integration.
     ```
   - Click "Generieren"
   - Wait for generation to complete

3. **Verify Version B**
   - Return to project page
   - **Expected Result**:
     - ✅ Existing requirements (matching titles) now show "B"
     - ✅ New requirements (e.g., "Payment Integration") show "A"
     - ✅ Total number of requirements may have increased

### Example Expected Results

| Version | ID  | Title               | Status               |
| ------- | --- | ------------------- | -------------------- |
| **B**   | 1   | User Authentication | Updated to Version B |
| **B**   | 2   | Product Catalog     | Updated to Version B |
| **B**   | 3   | Shopping Cart       | Updated to Version B |
| **A**   | 4   | Payment Integration | New requirement      |

---

## Test Scenario 3: Version History

### Steps

1. **Click "Historie" button**

   - On the project page, click "Historie" for any requirement
   - Example: Click "Historie" for "User Authentication"

2. **Verify history page**

   - **Expected Result**:
     - ✅ Page title shows "History for Requirement #X"
     - ✅ Table displays all versions (A, B, etc.)
     - ✅ Each version shows: Version | Title | Description | Category | Created At
     - ✅ Versions are ordered chronologically (A first, then B, etc.)
     - ✅ "Back to Project" button is visible

3. **Check version details**
   - Compare Version A and Version B
   - **Expected Result**:
     - ✅ Titles may be similar or identical
     - ✅ Descriptions may differ (showing evolution)
     - ✅ Timestamps show different creation times

---

## Test Scenario 4: Third Generation (Version C)

### Steps

1. **Generate requirements a third time**

   - Navigate to AI Agent again
   - Use another variation:
     ```
     E-commerce platform with OAuth authentication, AI-powered product recommendations, shopping cart with wishlist, secure payment gateway, and order tracking.
     ```
   - Click "Generieren"

2. **Verify Version C**
   - **Expected Result**:
     - ✅ Matching requirements now show "C"
     - ✅ New requirements show "A"
     - ✅ Version history shows A → B → C progression

---

## Test Scenario 5: Edge Cases

### Test 5.1: Similar Titles

**Purpose**: Verify that similar titles are matched correctly

1. Generate requirements with titles:

   - "User Login"
   - "User login" (different case)
   - "User Login" (extra space)

2. **Expected Result**:
   - ✅ All three should be treated as the same requirement
   - ✅ Should create versions A, B, C (not separate requirements)

### Test 5.2: Empty Project

**Purpose**: Verify first generation on empty project

1. Create a new empty project
2. Generate requirements
3. **Expected Result**:
   - ✅ All requirements get Version A
   - ✅ No errors occur

### Test 5.3: Many Versions

**Purpose**: Test version label generation beyond Z

1. Generate requirements 27+ times (if feasible)
2. **Expected Result**:
   - ✅ Versions A-Z work correctly
   - ⚠️ Version 27+ may show unexpected characters (limitation)

---

## Test Scenario 6: Migration (If Upgrading)

### Prerequisites

- Old database with existing requirements

### Steps

1. **Backup database**

   ```bash
   cp instance/db.db instance/db.db.backup
   ```

2. **Run migration script**

   ```bash
   python migrate_versions.py
   ```

3. **Verify migration**

   - Login to application
   - Navigate to existing project
   - **Expected Result**:
     - ✅ All old requirements appear in table
     - ✅ All show Version A
     - ✅ "Historie" button works
     - ✅ Version history shows only Version A

4. **Test new generation**
   - Generate new requirements
   - **Expected Result**:
     - ✅ Matching requirements get Version B
     - ✅ New requirements get Version A

---

## Test Scenario 7: Multi-User Testing

### Steps

1. **Create two user accounts**

   - User A: `user_a@test.com`
   - User B: `user_b@test.com`

2. **User A: Create project and generate requirements**

   - Login as User A
   - Create project "User A Project"
   - Generate requirements (Version A)

3. **User B: Create project and generate requirements**

   - Login as User B
   - Create project "User B Project"
   - Generate requirements (Version A)

4. **Verify isolation**
   - **Expected Result**:
     - ✅ User A cannot see User B's projects
     - ✅ User B cannot see User A's projects
     - ✅ Each user's requirements are independent
     - ✅ Version numbering is per-project, not global

---

## Test Scenario 8: UI/UX Testing

### Visual Checks

1. **Version Badge Styling**

   - [ ] Badge is clearly visible
   - [ ] Primary color (blue) is used
   - [ ] Badge text is readable

2. **Table Layout**

   - [ ] Version column width is appropriate (~5%)
   - [ ] Columns are properly aligned
   - [ ] Table is responsive on mobile

3. **History Page**
   - [ ] Table is easy to read
   - [ ] Timestamps are formatted correctly
   - [ ] Navigation is intuitive

### Accessibility

1. **Keyboard Navigation**

   - [ ] Can tab through table rows
   - [ ] "Historie" button is keyboard accessible
   - [ ] Back button works with keyboard

2. **Screen Reader**
   - [ ] Version badges have appropriate labels
   - [ ] Table headers are properly marked up

---

## Test Scenario 9: Performance Testing

### Large Dataset Test

1. **Generate many requirements**

   - Generate 50+ requirements
   - Generate multiple versions (A, B, C)

2. **Measure performance**

   - [ ] Project page loads in < 2 seconds
   - [ ] History page loads in < 1 second
   - [ ] No database timeout errors

3. **Check query efficiency**
   - [ ] Only latest versions are fetched (not all versions)
   - [ ] Subquery is optimized

---

## Test Scenario 10: Error Handling

### Test 10.1: Invalid Data

1. **Generate with empty description**

   - Leave description blank
   - Click "Generieren"
   - **Expected Result**: ✅ Should still work (description is optional)

2. **Generate with very long description**
   - Enter 5000+ characters
   - **Expected Result**: ✅ Should handle gracefully

### Test 10.2: Database Errors

1. **Simulate database lock**
   - (Advanced) Lock database file
   - Try to generate requirements
   - **Expected Result**: ✅ Error message displayed, no crash

### Test 10.3: AI Service Errors

1. **Invalid API key**
   - Temporarily set invalid OpenAI API key
   - Try to generate
   - **Expected Result**: ✅ Clear error message about AI service

---

## Automated Testing (Optional)

### Unit Tests

Create test file `test_versioning.py`:

```python
import pytest
from app import create_app, db
from app.models import Requirement, RequirementVersion, version_label
from app.agent import normalize_key, next_version_info

def test_version_label():
    assert version_label(1) == "A"
    assert version_label(2) == "B"
    assert version_label(26) == "Z"

def test_normalize_key():
    assert normalize_key("User Login") == "user login"
    assert normalize_key("User  Login") == "user login"
    assert normalize_key("USER LOGIN") == "user login"

def test_next_version_info():
    # Create mock requirement with versions
    # Test that next version is calculated correctly
    pass
```

Run tests:

```bash
pytest test_versioning.py -v
```

---

## Success Criteria

### Must Pass ✅

- [ ] Version column appears before ID column
- [ ] First generation creates Version A
- [ ] Second generation creates Version B for matching requirements
- [ ] Version history page displays all versions
- [ ] Migration script works without errors
- [ ] Multi-user isolation works correctly

### Should Pass ⚠️

- [ ] Performance is acceptable with 50+ requirements
- [ ] UI is responsive on mobile devices
- [ ] Error messages are clear and helpful

### Nice to Have 💡

- [ ] Keyboard navigation works smoothly
- [ ] Screen reader compatibility
- [ ] Automated tests pass

---

## Reporting Issues

If you encounter any issues during testing:

1. **Document the issue**

   - What you did (steps to reproduce)
   - What you expected
   - What actually happened
   - Screenshots if applicable

2. **Check logs**

   - Flask console output
   - Browser console (F12)
   - Database state

3. **Provide context**
   - Browser and version
   - Operating system
   - Database state (before/after)

---

## Quick Verification Checklist

Use this for rapid testing:

- [ ] Create project
- [ ] Generate requirements → All show Version A
- [ ] Generate again → Matching show Version B
- [ ] Click "Historie" → See both versions
- [ ] Version column is before ID column
- [ ] No errors in console

**If all checked**: ✅ Versioning system is working correctly!

---

**Last Updated**: Today  
**Version**: 1.0  
**Status**: Ready for Testing ✅
