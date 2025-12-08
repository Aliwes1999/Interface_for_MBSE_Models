import os
from app import create_app

# Only set production environment if not already set (for Render deployment)
# This allows local development to use FLASK_ENV from .flaskenv
if 'RENDER' in os.environ:
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
