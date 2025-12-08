"""
Add source_file_id column to requirement_version table
"""
from app import create_app, db

app = create_app()

with app.app_context():
    # Add the new column
    with db.engine.connect() as conn:
        try:
            # Check if column already exists
            result = conn.execute(db.text("PRAGMA table_info(requirement_version)"))
            columns = [row[1] for row in result]
            
            if 'source_file_id' not in columns:
                print("Adding source_file_id column to requirement_version table...")
                conn.execute(db.text(
                    "ALTER TABLE requirement_version ADD COLUMN source_file_id INTEGER"
                ))
                conn.commit()
                print("✓ Column added successfully!")
            else:
                print("✓ Column source_file_id already exists")
                
        except Exception as e:
            print(f"Error: {e}")
            conn.rollback()
