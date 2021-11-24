from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os  # module to read environment
from dotenv import load_dotenv  # make .env values visable for OS to see


db = SQLAlchemy()  # connect to database
migrate = Migrate()  # change the structure of the database
load_dotenv() # function gives access to the .env file


def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if not test_config:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
            'SQLALCHEMY_DATABASE_URI')
    else:
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
            'SQLALCHEMY_TEST_DATABASE_URI')

    # Import models here for Alembic setup
    from app.models.task import Task
    from app.models.goal import Goal

    db.init_app(app)  # app I'm going to work with
    migrate.init_app(app, db)  # the way to get to database

    # Register Blueprints here
    from app.routes import tasks_bp
    app.register_blueprint(tasks_bp)

    from app.routes import goals_bp
    app.register_blueprint(goals_bp)

    return app
