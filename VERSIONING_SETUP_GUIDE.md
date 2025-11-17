# Versioning System Setup Guide

**Problem**: Database schema needs to be updated to support the new versioning system.

**Error**: `sqlalchemy.exc.OperationalError: no such column: requirement.key`

This guide will help you update your database to support the versioning system.

---

## Quick Fix (Recommended)

### Option 1: Update Existing Database (Preserves Data)

**Use this if you have existing projects and requirements you want to keep.**

1. **Stop the Flask application** (if running)

   - Press `Ctrl+C` in the terminal

2. **Run the schema update script**

   ```bash
   python update_database_schema.py
   ```

3. **Verify the update**

   - The script will:
     - ✅ Create a backup of your database
     - ✅ Add the `key` column to `requirement` table
     - ✅ Create the `requirement_version` table
     - ✅ Create necessary indexes

4. **Migrate existing data** (if you have old requirements)

   ```bash
   python migrate_versions.py
   ```

5. **Restart the application**

   ```bash
   python main.py
   ```

6. **Test**
   - Navigate to a project
   - You should now see the Version column
   - Generate requirements to test versioning

---

### Option 2: Fresh Start (Clean Database)

**Use this if you don't have important data or want to start fresh.**

1. **Stop the Flask application** (if running)

2. **Backup your current database** (optional, but recommended)

   ```bash
   copy instance\db.db instance\db.db.old
   ```

3. **Delete the current database**

   ```bash
   del instance\db.db
   ```

4. **Start the application** (it will create a new database with correct schema)

   ```bash
   python main.py
   ```

5. **Register a new user and test**
   - Go to http://localhost:5000
   - Register/Login
   - Create a project
   - Generate requirements
   - Verify Version column appears

---

## Detailed Steps for Option 1

### Step 1: Backup Current Database

```bash
# Create instance directory if it doesn't exist
mkdir instance

# Backup the database
copy instance\db.db instance\db.db.backup
```

### Step 2: Run Schema Update

```bash
python update_database_schema.py
```

**Expected Output:**

```
============================================================
DATABASE SCHEMA UPDATE FOR VERSIONING SYSTEM
============================================================

Database location: instance\db.db
✅ Database backed up to: instance\db.db.backup_20240115_143022

🔄 Updating database schema...
📝 Creating requirement_version table...
✅ requirement_version table created
📝 Adding 'key' column to requirement table...
✅ 'key' column added and indexed

✅ Schema update completed successfully!

============================================================
✅ MIGRATION COMPLETED SUCCESSFULLY!
============================================================
```

### Step 3: Migrate Existing Data (If Applicable)

If you have existing requirements in your database:

```bash
python migrate_versions.py
```

**Expected Output:**

```
Starting data migration...
Processing project: 'My Project' (ID: 1)
  -> Found 5 unique requirements to migrate.
    -> Migrated 'User Authentication' as Version A.
    -> Migrated 'Product Catalog' as Version A.
    -> Migrated 'Shopping Cart' as Version A.
    -> Migrated 'Payment Gateway' as Version A.
    -> Migrated 'Order Tracking' as Version A.
Committing changes to the database...
Migration complete!
```

### Step 4: Verify the Update

1. **Start the application**

   ```bash
   python main.py
   ```

2. **Login and navigate to a project**

3. **Check the requirements table**

   - ✅ Version column should appear BEFORE ID column
   - ✅ All requirements should show "A" badge
   - ✅ "Historie" button should be visible

4. **Test version creation**
   - Go to AI Agent
   - Generate requirements
   - Matching requirements should get Version B

---

## Troubleshooting

### Issue 1: "Database is locked"

**Solution:**

```bash
# Stop all Flask processes
# Then try again
python update_database_schema.py
```

### Issue 2: "Permission denied"

**Solution:**

```bash
# Run as administrator or check file permissions
# Make sure instance/db.db is not read-only
```

### Issue 3: Schema update fails

**Solution:**

```bash
# Restore from backup
copy instance\db.db.backup instance\db.db

# Try Option 2 (Fresh Start) instead
```

### Issue 4: Migration script fails

**Possible causes:**

- Old database structure is incompatible
- JSON data is corrupted

**Solution:**

```bash
# Check the error message
# You may need to manually inspect the database

# Or start fresh with Option 2
```

### Issue 5: Version column still not showing

**Check:**

1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+F5)
3. Check that schema update completed successfully
4. Verify `requirement` table has `key` column:
   ```bash
   sqlite3 instance/db.db
   .schema requirement
   .exit
   ```

---

## Manual Database Inspection

If you want to manually check the database:

```bash
# Open SQLite database
sqlite3 instance/db.db

# Check requirement table structure
.schema requirement

# Check requirement_version table structure
.schema requirement_version

# List all requirements
SELECT * FROM requirement;

# List all requirement versions
SELECT * FROM requirement_version;

# Exit
.exit
```

---

## Verification Checklist

After running the update, verify:

- [ ] `update_database_schema.py` completed successfully
- [ ] Backup file exists in `instance/` directory
- [ ] Application starts without errors
- [ ] Can login and view projects
- [ ] Requirements table shows Version column
- [ ] Version column is BEFORE ID column
- [ ] Can generate requirements (creates Version A)
- [ ] Can generate again (creates Version B)
- [ ] "Historie" button works
- [ ] Version history page displays correctly

---

## What the Scripts Do

### `update_database_schema.py`

- Creates backup of database
- Adds `key` column to `requirement` table
- Creates `requirement_version` table
- Creates indexes for performance
- Does NOT modify existing data

### `migrate_versions.py`

- Reads old requirement data
- Creates `Requirement` entries with keys
- Creates `RequirementVersion` entries (all as Version A)
- Preserves all existing information
- Safe to run multiple times (skips already migrated data)

---

## Recovery Plan

If something goes wrong:

1. **Stop the application**

   ```bash
   # Press Ctrl+C
   ```

2. **Restore from backup**

   ```bash
   copy instance\db.db.backup instance\db.db
   ```

3. **Restart application**

   ```bash
   python main.py
   ```

4. **Try Option 2 (Fresh Start)** if issues persist

---

## Next Steps After Successful Update

1. **Test basic functionality**

   - Create a project
   - Generate requirements
   - Verify Version A appears

2. **Test versioning**

   - Generate requirements again
   - Verify Version B appears for matching requirements

3. **Test version history**

   - Click "Historie" button
   - Verify all versions are displayed

4. **Read the documentation**
   - VERSIONING_IMPLEMENTATION.md (technical details)
   - VERSIONING_TESTING_GUIDE.md (comprehensive testing)
   - VERSIONING_SUMMARY.md (overview)

---

## Support

If you encounter issues not covered here:

1. Check the error message carefully
2. Look in the Flask console output
3. Check browser console (F12)
4. Verify database file permissions
5. Try the Fresh Start option (Option 2)

---

**Last Updated**: Today  
**Status**: Ready to Use  
**Recommended**: Option 1 (Update Existing Database)
