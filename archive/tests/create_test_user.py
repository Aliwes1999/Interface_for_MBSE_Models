from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    # Check if user exists
    user = User.query.filter_by(email='test@example.com').first()
    if user:
        print(f"User exists: {user.email}")
    else:
        # Create a test user
        user = User(email='test@example.com')
        user.set_password('test123')
        db.session.add(user)
        db.session.commit()
        print(f"User created: {user.email}")
