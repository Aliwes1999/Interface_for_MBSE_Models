from app import create_app
from app.models import User, Project

app = create_app()
with app.test_client() as client:
    # login
    resp = client.post('/auth/login', data={'email':'test@example.com','password':'test123'})
    print('Login status:', resp.status_code)
    
    # test entry page
    resp2 = client.get('/project/3')
    print('Entry page status:', resp2.status_code)
    
    # test overview page
    resp3 = client.get('/project/3/overview')
    print('Overview page status:', resp3.status_code)
    
    # check if templates render without errors
    if b'Neue Anforderungen generieren' in resp2.data:
        print('Entry page renders with correct content')
    if b'Aktuelle Anforderungen' in resp3.data:
        print('Overview page renders with correct content')
