import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    projects = db.relationship('Project', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Requirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Requirement {self.title}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    columns = db.Column(db.Text, nullable=False)  # JSON string for list of columns
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_requirements = db.Column(db.Text, nullable=False, default='[]')  # JSON string for list of dicts
    intermediate_requirements = db.Column(db.Text, nullable=False, default='[]')
    saved_requirements = db.Column(db.Text, nullable=False, default='[]')
    deleted_requirements = db.Column(db.Text, nullable=False, default='[]')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    requirements = db.relationship('Requirement', backref='project', lazy=True)

    def __repr__(self):
        return f'<Project {self.name}>'

    def get_columns(self):
        return json.loads(self.columns)

    def set_columns(self, cols):
        self.columns = json.dumps(cols)

    def get_created_requirements(self):
        return json.loads(self.created_requirements)

    def set_created_requirements(self, reqs):
        self.created_requirements = json.dumps(reqs)

    def get_intermediate_requirements(self):
        return json.loads(self.intermediate_requirements)

    def set_intermediate_requirements(self, reqs):
        self.intermediate_requirements = json.dumps(reqs)

    def get_saved_requirements(self):
        return json.loads(self.saved_requirements)

    def set_saved_requirements(self, reqs):
        self.saved_requirements = json.dumps(reqs)

    def get_deleted_requirements(self):
        return json.loads(self.deleted_requirements)

    def set_deleted_requirements(self, reqs):
        self.deleted_requirements = json.dumps(reqs)
