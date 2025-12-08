from config import DevelopmentConfig
print("Database URI:", DevelopmentConfig.SQLALCHEMY_DATABASE_URI)

# Try to connect using SQLAlchemy
from sqlalchemy import create_engine
try:
    engine = create_engine(DevelopmentConfig.SQLALCHEMY_DATABASE_URI)
    with engine.connect() as conn:
        print("Database connection successful!")
except Exception as e:
    print(f"Database connection failed: {e}")
