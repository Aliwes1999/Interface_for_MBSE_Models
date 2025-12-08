"""
Database migration script to add project files management:
- Create project_file table for managing files per project
"""

import sqlite3
import os

def migrate_database():
    db_path = os.path.join('instance', 'db.db')

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("Please ensure the database exists before running migration.")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("Starting database migration...")

        # Create project_file table
        print("Creating project_file table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_file (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                filename VARCHAR(255) NOT NULL,
                filepath VARCHAR(500) NOT NULL,
                file_type VARCHAR(50) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by_id INTEGER NOT NULL,
                FOREIGN KEY (project_id) REFERENCES project(id),
                FOREIGN KEY (created_by_id) REFERENCES user(id)
            )
        ''')

        # Commit changes
        conn.commit()
        print("\n✅ Migration completed successfully!")
        print("\nNew features enabled:")
        print("  - Project files management (uploads, generations, exports)")

        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        conn.rollback()
        return False

    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("Database Migration: Add Project Files")
    print("=" * 60)
    print()

    success = migrate_database()

    if success:
        print("\n" + "=" * 60)
        print("Migration completed. You can now manage project files!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Migration failed. Please check the error messages above.")
        print("=" * 60)
