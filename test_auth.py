from app import create_app
from flask import Flask
import logging

logging.basicConfig(level=logging.DEBUG)

try:
    app = create_app()
    print("App created successfully")
    
    with app.test_client() as client:
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'test123'
        })
        print(f"Status: {response.status_code}")
        print(f"Content: {response.get_data(as_text=True)[:500]}")
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
