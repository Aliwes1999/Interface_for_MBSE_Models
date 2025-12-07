# Maintenance Scripts

This directory contains maintenance scripts for the MBSE Models Interface application. These scripts are used for database migrations, schema fixes, and other maintenance tasks.

## Available Scripts

### Database Migration Scripts

- `add_additional_fields.py` - Adds additional fields to database tables
- `add_is_deleted_column.py` - Adds is_deleted column for soft deletes
- `add_new_columns.py` - Adds new columns to existing tables
- `complete_database_reset.py` - Complete database reset script
- `database_migration.py` - General database migration script
- `fix_columns_field.py` - Fixes column field issues
- `fix_database_schema.py` - Fixes database schema issues
- `migrate_database.py` - Migrates database to new schema
- `migrate_versions.py` - Migrates requirement versions
- `remove_old_columns.py` - Removes deprecated columns
- `temp_init.py` - Temporary initialization script
- `fix_template.py` - Fixes template-related issues

## Usage

To run any of these scripts, navigate to the project root directory and execute:

```bash
python scripts/<script_name>.py
```

**Important Notes:**

- Always backup your database before running migration scripts
- Run scripts in a development environment first
- Check the script content for any specific requirements or dependencies
- Some scripts may require environment variables or configuration to be set

## Troubleshooting

If you encounter issues:

1. Check the script's error messages
2. Verify database connectivity
3. Ensure all dependencies are installed
4. Review the application logs for additional details

## Contributing

When adding new maintenance scripts:

1. Place them in this `scripts/` directory
2. Update this README with the new script description
3. Include clear usage instructions in the script comments
4. Test the script thoroughly before committing
