from flask import Flask

def create_app():
    app = Flask(__name__)

    # Routen importieren
    from . import routes
    return app
