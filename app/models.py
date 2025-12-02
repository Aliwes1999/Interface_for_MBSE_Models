from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db

def version_label(n: int) -> str:
    """Generates a letter-based version label (1 -> A, 2 -> B, ...)."""
    if n <= 0:
        return ""
    return chr(ord('A') + (n - 1))

# Association table for project sharing (many-to-many)
project_user_association = db.Table('project_user_association',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    projects = db.relationship('Project', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # JSON field to store dynamic column configuration
    custom_columns = db.Column(db.Text, default='[]')  # Stores list of column names as JSON
    
    requirements = db.relationship("Requirement", backref="project", lazy=True, cascade="all, delete-orphan")
    
    # Many-to-many relationship for shared users
    shared_with = db.relationship('User', secondary=project_user_association, 
                                   backref=db.backref('shared_projects', lazy='dynamic'))

    def __repr__(self):
        return f'<Project {self.name}>'
    
    def get_custom_columns(self):
        """Get list of custom column names."""
        import json
        try:
            return json.loads(self.custom_columns) if self.custom_columns else []
        except:
            return []
    
    def set_custom_columns(self, columns):
        """Set custom column names."""
        import json
        self.custom_columns = json.dumps(columns)
    
    def is_accessible_by(self, user):
        """Check if user can access this project (owner or shared)."""
        return self.user_id == user.id or user in self.shared_with

class Requirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    # A stable key to match requirements across different generation runs
    key = db.Column(db.String(200), index=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Soft delete flag
    is_deleted = db.Column(db.Boolean, default=False)

    versions = db.relationship(
        "RequirementVersion",
        backref="requirement",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="RequirementVersion.version_index.asc()"
    )

    def __repr__(self):
        return f'<Requirement {self.id} (Key: {self.key})>'
    
    def get_latest_version(self):
        """Get the latest version of this requirement."""
        if not self.versions:
            return None
        return self.versions[-1]

class RequirementVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requirement_id = db.Column(db.Integer, db.ForeignKey('requirement.id'), nullable=False)
    version_index = db.Column(db.Integer, nullable=False)     # 1, 2, 3, ...
    version_label = db.Column(db.String(4), nullable=False)   # A, B, C, ...

    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.String(2000), nullable=False)
    category = db.Column(db.String(80))
    status = db.Column(db.String(30), nullable=False, default="Offen")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # JSON field to store dynamic column values
    custom_data = db.Column(db.Text, default='{}')  # Stores {column_name: value} as JSON
    
    # User tracking fields
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    last_modified_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Blocking/locking fields
    is_blocked = db.Column(db.Boolean, default=False)
    blocked_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    blocked_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships for user tracking
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_versions')
    last_modified_by = db.relationship('User', foreign_keys=[last_modified_by_id], backref='modified_versions')
    blocked_by = db.relationship('User', foreign_keys=[blocked_by_id], backref='blocked_versions')

    __table_args__ = (
        db.UniqueConstraint('requirement_id', 'version_index', name='uq_req_version'),
    )

    def __repr__(self):
        return f'<RequirementVersion {self.id} ({self.version_label}) for Req {self.requirement_id}>'
    
    def get_custom_data(self):
        """Get custom column data as dictionary."""
        import json
        try:
            return json.loads(self.custom_data) if self.custom_data else {}
        except:
            return {}
    
    def get_custom_data_json(self):
        """Get custom column data as properly escaped JSON string for HTML attributes."""
        import json
        import html
        data = self.get_custom_data()
        json_str = json.dumps(data)
        # Escape for HTML attribute - replace quotes with HTML entities
        return html.escape(json_str, quote=True)
    
    def set_custom_data(self, data):
        """Set custom column data."""
        import json
        self.custom_data = json.dumps(data)
    
    def get_status_color(self):
        """Get Bootstrap color class for status."""
        status_colors = {
            'Offen': 'danger',      # Red
            'In Arbeit': 'warning', # Yellow
            'Fertig': 'success'     # Green
        }
        return status_colors.get(self.status, 'secondary')
    
    def can_be_edited_by(self, user):
        """Check if user can edit this version (not blocked or blocked by this user or project owner)."""
        if not self.is_blocked:
            return True
        # If blocked, only the blocker or project owner can edit
        return self.blocked_by_id == user.id or self.requirement.project.user_id == user.id
    
    def can_be_blocked_by(self, user):
        """Check if user can block/unblock this version."""
        # Owner can always block/unblock
        if self.requirement.project.user_id == user.id:
            return True
        # If not blocked, any shared user can block
        if not self.is_blocked:
            return self.requirement.project.is_accessible_by(user)
        # If blocked, only the blocker can unblock
        return self.blocked_by_id == user.id

