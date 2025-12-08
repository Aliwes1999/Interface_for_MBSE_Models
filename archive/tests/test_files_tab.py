from app import create_app
from app.models import User,Project,ProjectFile

app = create_app()
with app.app_context():
    with app.test_client() as client:
        client.post('/auth/login', data={'email':'test@example.com','password':'test123'}, follow_redirects=True)
        project=Project.query.filter_by(name='Test Project').first()
        resp=client.get(f'/project/{project.id}/overview?active_tab=files')
        html=resp.data.decode('utf-8')
        idx=html.find('id="files"')
        snippet=html[idx-60:idx+120]
        print('status', resp.status_code)
        print('files tab snippet:')
        print(snippet)
        print('files tab active?', 'show active' in snippet)
