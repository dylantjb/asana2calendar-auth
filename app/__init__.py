import os

from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()


def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug

    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)
    app.secret_key = os.environ["ASANA_CLIENT"]

    socketio.init_app(app)
    return app

