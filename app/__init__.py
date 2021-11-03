from flask import Flask
# Step 1:
# Import and initialize SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

# Initialize SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()
DATABASE_CONNECTION_STRING='postgresql+psycopg2://postgres:postgres@localhost:5432/task_list_api_development'
load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONNECTION_STRING

    # Step 2:
    #Configure SQLAlchemy
    if not test_config:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "SQLALCHEMY_DATABASE_URI")
    else:
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "SQLALCHEMY_TEST_DATABASE_URI")

    # Import models
    from app.models.task import Task
    from app.models.goal import Goal
    # Step 3:
    # Hook up Flask & SQLALchemy
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints here
    from .routes import tasks_bp
    app.register_blueprint(tasks_bp)

    return app
