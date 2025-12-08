from app import create_app

app = create_app()
with app.test_client() as client:
    # login first
    resp = client.post('/auth/login', data={'email':'test@example.com','password':'test123'})
    print('login status', resp.status_code)
    # open upload page
    resp2 = client.get('/agent/upload/3')
    print('upload page status', resp2.status_code)
    print(resp2.get_data(as_text=True)[:400])
