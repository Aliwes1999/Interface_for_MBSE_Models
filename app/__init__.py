import os
from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy

bp = Blueprint("main", __name__)
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Add secret key for sessions
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(app.instance_path, "db.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from . import models
    with app.app_context():
        db.create_all()

    from .routes import bp
    app.register_blueprint(bp)
    return app
