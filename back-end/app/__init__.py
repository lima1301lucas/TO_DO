from flask import Flask
from .routes.tasks import tasks_bp
from .routes.users import users_bp
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Pegar a SECRET_KEY do .env
    app.secret_key = os.getenv("SECRET_KEY")

    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(users_bp, url_prefix='/api/users')

    return app