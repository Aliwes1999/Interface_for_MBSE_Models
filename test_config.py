import os

# Set development environment before importing app
os.environ['FLASK_ENV'] = 'development'

from app import create_app

# Test configuration loading
print("=" * 60)
print("TESTING FLASK CONFIGURATION")
print("=" * 60)

# Check environment variables
print(f"\nFLASK_ENV: {os.getenv('FLASK_ENV', 'not set')}")
print(f"FLASK_APP: {os.getenv('FLASK_APP', 'not set')}")
print(f"RENDER: {os.getenv('RENDER', 'not set')}")

# Create app and check configuration
app = create_app()

print(f"\nApp Configuration:")
print(f"DEBUG: {app.config.get('DEBUG')}")
print(f"SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
print(f"Instance Path: {app.instance_path}")

# Check if instance folder exists
if os.path.exists(app.instance_path):
    print(f"✓ Instance folder exists")
else:
    print(f"✗ Instance folder does NOT exist")

# Check if database file exists
db_path = os.path.join(app.instance_path, 'db.db')
if os.path.exists(db_path):
    print(f"✓ Database file exists at: {db_path}")
else:
    print(f"✓ Database will be created at: {db_path}")

print("\n" + "=" * 60)
print("Configuration test completed successfully!")
print("=" * 60)
