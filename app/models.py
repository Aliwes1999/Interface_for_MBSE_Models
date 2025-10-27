import json

from . import db

class Requirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nummer = db.Column(db.String(50), nullable=False)
    beschreibung = db.Column(db.String(500), nullable=False)
    kategorie = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Requirement {self.nummer}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    columns = db.Column(db.Text, nullable=False)  # JSON string for list of columns
    created_requirements = db.Column(db.Text, nullable=False, default='[]')  # JSON string for list of dicts
    intermediate_requirements = db.Column(db.Text, nullable=False, default='[]')
    saved_requirements = db.Column(db.Text, nullable=False, default='[]')
    deleted_requirements = db.Column(db.Text, nullable=False, default='[]')

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
