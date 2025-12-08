from app import create_app, db
from app.models import User
import traceback

app = create_app()
with app.app_context():
    try:
        user = User.query.filter_by(email='test@example.com').first()
        print(f"User found: {user}")
        if user:
            print(f"Email: {user.email}")
            print(f"Password check: {user.check_password('test123')}")
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
