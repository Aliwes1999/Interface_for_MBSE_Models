from app import create_app
from flask_login import login_user

app = create_app()

with app.test_client() as client:
    # First, try to set a session manually
    with client.session_transaction() as sess:
        print(f"Session before login: {dict(sess)}")
    
    # Try login POST
    print("\nAttempting login...")
    try:
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'test123'
        }, follow_redirects=False)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        # Check session after
        with client.session_transaction() as sess:
            print(f"Session after login: {dict(sess)}")
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()
