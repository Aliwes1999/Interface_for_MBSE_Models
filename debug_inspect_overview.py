from app import create_app
from app.models import User, Project, ProjectFile

app = create_app()
with app.app_context():
    with app.test_client() as client:
        client.post('/auth/login', data={'email':'test@example.com','password':'test123'}, follow_redirects=True)
        project = Project.query.filter_by(name='Test Project').first()
        file = ProjectFile.query.filter_by(project_id=project.id).first()
        resp = client.get(f'/project/{project.id}/overview?file_id={file.id}')
        html = resp.data.decode('utf-8')
        # Show around the requirements div
        idx = html.find('id="requirements"')
        print('index:', idx)
        print(html[idx-60:idx+200])
        print('--- full nav-tabs block ---')
        i2 = html.find('id="projectTabs"')
        print(html[i2:i2+400])
