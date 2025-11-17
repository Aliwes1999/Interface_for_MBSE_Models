# Additional Features Implementation Plan

## Overview

6 new features/fixes to implement while maintaining all existing functionality.

## Feature List

### 1. Bug Fix: Edit After Adding Columns

**Priority:** HIGH (Bug Fix)
**Complexity:** Medium

**Problem:** After adding dynamic columns and running AI generation, editing doesn't work.

**Solution:**

- Investigate edit modal JavaScript
- Ensure dynamic column fields are properly generated in edit form
- Fix field mapping between custom_data and form inputs
- Test: Add column → Generate → Edit → Save

### 2. Excel Export: Only "Fertig" Status

**Priority:** Medium
**Complexity:** Low

**Changes:**

- Modify `export_excel()` route
- Filter: `latest_version.status == "Fertig"`
- Keep all other functionality

### 3. Excel Import

**Priority:** High
**Complexity:** High

**Requirements:**

- Upload .xlsx file
- Parse with openpyxl
- Create Requirements + RequirementVersion (Version A)
- Map columns to fields + custom_data
- Validation and error handling

**Components:**

- UI: Upload button + form
- Route: POST /project/<id>/import_excel
- Parser: Read Excel, validate, create records

### 4. Project Sharing

**Priority:** High
**Complexity:** High

**Requirements:**

- Many-to-Many: Project ↔ User
- Owner can share via email
- Shared users can view/edit
- Authorization checks updated

**Components:**

- Model: ProjectUserAssociation table
- UI: Share button + form
- Routes: Add/remove shared users
- Permissions: Update all routes

### 5. User Tracking (Author/Editor)

**Priority:** Medium
**Complexity:** Medium

**Requirements:**

- Track who created/modified each version
- Display in UI

**Components:**

- Model: created_by_id, last_modified_by_id on RequirementVersion
- Update: All create/edit operations
- Display: Show user info in table

### 6. Requirement Blocking/Locking

**Priority:** Medium
**Complexity:** Medium

**Requirements:**

- User can block a version
- Blocked versions can't be edited by others
- Only blocker or owner can unblock

**Components:**

- Model: is_blocked, blocked_by_id on RequirementVersion
- UI: Block/Unblock button
- Routes: Toggle block
- Permissions: Check block status before edit

## Implementation Order

### Phase 1: Database Schema (Features 4, 5, 6)

1. Update models.py
2. Create migration script
3. Apply migrations

### Phase 2: Bug Fix (Feature 1)

4. Fix edit functionality with dynamic columns

### Phase 3: Simple Features (Features 2)

5. Update Excel export filter

### Phase 4: Complex Features (Features 3, 4, 5, 6)

6. Excel import
7. Project sharing
8. User tracking display
9. Blocking functionality

## Database Changes Required

### New Tables

```python
# Many-to-Many for project sharing
project_user_association = db.Table('project_user_association',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)
```

### Model Updates

```python
# Project model
class Project(db.Model):
    # Add relationship
    shared_with = db.relationship('User', secondary=project_user_association, backref='shared_projects')

# RequirementVersion model
class RequirementVersion(db.Model):
    # Add fields
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    last_modified_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_blocked = db.Column(db.Boolean, default=False)
    blocked_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # Add relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    last_modified_by = db.relationship('User', foreign_keys=[last_modified_by_id])
    blocked_by = db.relationship('User', foreign_keys=[blocked_by_id])
```

## Testing Strategy

After each feature:

1. Test the new feature
2. Regression test existing features
3. Fix any issues before moving to next feature

## Risk Assessment

**High Risk:**

- Database migrations (backup required)
- Authorization changes (could break access)
- Edit functionality fix (core feature)

**Medium Risk:**

- Excel import (data validation)
- Project sharing (complex permissions)

**Low Risk:**

- Excel export filter (simple change)
- User tracking display (additive)
- Blocking (isolated feature)
