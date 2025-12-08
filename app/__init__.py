import os
from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import DevelopmentConfig, ProductionConfig

bp = Blueprint("main", __name__)
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Load configuration based on environment
    if os.getenv("FLASK_ENV") == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Ensure the instance folder exists for SQLite in development
    if os.getenv("FLASK_ENV") != "production":
        os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from . import models
    with app.app_context():
        db.create_all()

    from .routes import bp
    from .auth import auth_bp
    from .agent import agent_bp
    app.register_blueprint(bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(agent_bp)

    from .migration import migration_bp
    app.register_blueprint(migration_bp)

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))
