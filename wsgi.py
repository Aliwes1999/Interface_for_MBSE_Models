import os
from app import create_app

# Set production environment for Render
os.environ.setdefault('FLASK_ENV', 'production')

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    # For local development with waitress
    try:
        from waitress import serve
        serve(app, host='0.0.0.0', port=8000)
    except ImportError:
        # Fallback to Flask's built-in server
        app.run(host='0.0.0.0', port=8000)
