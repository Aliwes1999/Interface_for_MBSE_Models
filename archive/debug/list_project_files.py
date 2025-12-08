from app import create_app
from app.models import User, ProjectFile, Project

app = create_app()
with app.app_context():
    user = User.query.filter_by(email='test@example.com').first()
    proj = Project.query.filter_by(name='Test Project').first()
    print('user', user.email if user else None)
    print('proj', proj.id if proj else None)
    files = ProjectFile.query.filter_by(project_id=proj.id).all()
    for f in files:
        print('file', f.id, f.filename, f.file_type, f.created_at)
