# Database Migration Guide

## Problem

When upgrading to the new AI Agent version, you may encounter this error:

```
(sqlite3.OperationalError) table requirement has no column named title
```

This occurs because the existing database was created with an older schema that didn't include the `Requirement` table with all necessary fields.

## Solution

Run the database migration script to update the schema:

```bash
python migrate_database.py
```

## What the Migration Does

1. **Backs up existing data** - Saves all users and projects
2. **Drops all tables** - Removes old schema
3. **Creates new tables** - With correct Requirement schema
4. **Restores data** - Puts back users and projects

## Requirement Table Schema

After migration, the `requirement` table has these columns:

- `id` - Primary key
- `title` - Requirement title (String, 100 chars)
- `description` - Detailed description (String, 500 chars)
- `category` - Category (String, 100 chars)
- `status` - Status (String, 50 chars, default: "Offen")
- `project_id` - Foreign key to project
- `created_at` - Timestamp

## Important Notes

⚠️ **Warning:** This migration will delete all existing requirements (if any) because the old schema was incompatible. Users and projects are preserved.

✅ **Safe:** The migration backs up and restores users and projects automatically.

## Verification

After running the migration, you should see:

```
✅ Database migration completed successfully!

The requirement table now has the correct schema:
  - id
  - title
  - description
  - category
  - status
  - project_id
  - created_at

You can now use the AI Agent to generate requirements.
```

## Testing After Migration

1. Start the application:

   ```bash
   python main.py
   ```

2. Login and navigate to a project

3. Click "KI-Agent" button

4. Generate requirements - should work without errors

## Troubleshooting

### If migration fails:

1. **Stop the Flask application** if it's running
2. **Backup the database** (optional):
   ```bash
   copy instance\db.db instance\db.db.backup
   ```
3. **Run migration again**:
   ```bash
   python migrate_database.py
   ```

### If you want to start fresh:

1. Stop the Flask application
2. Delete the database:
   ```bash
   del instance\db.db
   ```
3. Start the application (it will create a new database):
   ```bash
   python main.py
   ```
4. Register a new user and create projects

## Alternative: Manual Migration

If you prefer to keep existing requirements (if any), you can manually migrate:

1. Stop the Flask application

2. Use SQLite command line:

   ```bash
   sqlite3 instance/db.db
   ```

3. Check current schema:

   ```sql
   .schema requirement
   ```

4. If the table exists but has wrong columns, drop and recreate:

   ```sql
   DROP TABLE IF EXISTS requirement;
   CREATE TABLE requirement (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       title VARCHAR(100) NOT NULL,
       description VARCHAR(500) NOT NULL,
       category VARCHAR(100) NOT NULL,
       status VARCHAR(50) NOT NULL,
       project_id INTEGER NOT NULL,
       created_at DATETIME,
       FOREIGN KEY(project_id) REFERENCES project (id)
   );
   ```

5. Exit SQLite:
   ```sql
   .exit
   ```

## Prevention

To avoid this issue in future updates:

1. Always backup your database before updates
2. Use proper database migration tools (like Flask-Migrate/Alembic) for production
3. Test updates in a development environment first

## Status

✅ **Migration Completed Successfully**

The database has been updated and the AI Agent is now fully functional.
