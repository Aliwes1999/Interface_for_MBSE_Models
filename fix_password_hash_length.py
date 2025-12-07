#!/usr/bin/env python3
"""
Fix password hash field length in database.
This script increases the password_hash field from 128 to 256 characters.
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config, DevelopmentConfig, ProductionConfig

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app_for_migration():
    """Create app for migration purposes."""
    app = Flask(__name__)

    # Use production config if DATABASE_URL is set, otherwise development
    if os.getenv('DATABASE_URL'):
        config_class = ProductionConfig
    else:
        config_class = DevelopmentConfig

    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    return app

def main():
    app = create_app_for_migration()

    with app.app_context():
        # Import models after app context
        from app.models import User

        print("Current password_hash column length:", User.password_hash.type.length)

        # For PostgreSQL, we need to use ALTER TABLE
        # For SQLite, we can recreate the table

        if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']:
            print("PostgreSQL detected - using ALTER TABLE")
            # For PostgreSQL, we need to alter the column
            db.engine.execute('ALTER TABLE "user" ALTER COLUMN password_hash TYPE VARCHAR(256);')
            print("Password hash field length updated to 256 characters in PostgreSQL")
        else:
            print("SQLite detected - recreating table")
            # For SQLite, we need to recreate the table
            # First, backup existing data
            users = User.query.all()
            user_data = []
            for user in users:
                user_data.append({
                    'id': user.id,
                    'email': user.email,
                    'password_hash': user.password_hash,
                    'created_at': user.created_at
                })

            # Drop and recreate table
            db.drop_all()
            db.create_all()

            # Restore data
            for data in user_data:
                user = User(
                    id=data['id'],
                    email=data['email'],
                    password_hash=data['password_hash'],
                    created_at=data['created_at']
                )
                db.session.add(user)

            db.session.commit()
            print("Password hash field length updated to 256 characters in SQLite")

        print("Migration completed successfully!")

if __name__ == '__main__':
    main()
