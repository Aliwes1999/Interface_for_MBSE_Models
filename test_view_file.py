from app import create_app

app = create_app()
with app.test_client() as client:
    # login using test user
    resp = client.post('/auth/login', data={'email':'test@example.com','password':'test123'})
    print('Login status', resp.status_code)
    # attempt to view a file (likely 404 if no files)
    resp2 = client.get('/project/1/file/1')
    print('View file status', resp2.status_code)
    print(resp2.get_data(as_text=True)[:500])
