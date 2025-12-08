from app import create_app, db
from app.models import Project, ProjectFile, User
import os

app = create_app()
with app.app_context():
    user = User.query.filter_by(email='test@example.com').first()
    if not user:
        print('Test user missing')
    else:
        proj = Project(name='Test Project', user_id=user.id)
        db.session.add(proj)
        db.session.commit()
        print('Created project', proj.id)
        # create dummy file entries
        uploads_dir = os.path.join('uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        filepath = os.path.join(uploads_dir, 'sample.xlsx')
        # create an empty file if not exists
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write('')
        pf1 = ProjectFile(project_id=proj.id, filename='sample.xlsx', filepath=filepath, file_type='upload', created_by_id=user.id)
        pf2 = ProjectFile(project_id=proj.id, filename='exported_1.xlsx', filepath=filepath, file_type='export', created_by_id=user.id)
        db.session.add_all([pf1, pf2])
        db.session.commit()
        print('Added files')
