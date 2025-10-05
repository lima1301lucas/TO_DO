from flask import Flask
from .routes.tasks import tasks_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')

    return app
