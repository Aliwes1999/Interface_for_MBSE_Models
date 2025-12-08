from app import create_app
from app.models import User, Project, ProjectFile

app = create_app()
with app.app_context():
    with app.test_client() as client:
        user = User.query.filter_by(email='test@example.com').first()
        project = Project.query.filter_by(name='Test Project', user_id=user.id).first()
        file = ProjectFile.query.filter_by(project_id=project.id).first()
        # login
        client.post('/auth/login', data={'email':'test@example.com','password':'test123'}, follow_redirects=True)
        url = f'/project/{project.id}/overview?file_id={file.id}'
        resp = client.get(url)
        print('status', resp.status_code)
        html = resp.data.decode('utf-8')
        # Check requirements tab contains 'show active'
        idx = html.find('id="requirements"')
        snippet = html[idx:idx+200]
        print('snippet:')
        print(snippet)
        print('requirements active class present?:', 'show active' in snippet)
