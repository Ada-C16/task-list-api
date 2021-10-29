from flask import Blueprint, make_response, request, jsonify
from app.models.task import Task
from app import db

# Blueprints
task_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")


# Helper Functions


# Routes
@task_bp.route("", methods = ["POST"])
def add_books():
    """Add new books to database"""
    request_body = request.json()

    if request_body is None:
        return make_response("You must include task name and description in order to add your task.", 400)

    if "name" not in request_body or "description" not in request_body:
        return make_response("You must include task name and description in order to add your task.", 400)

    new_task = Task(
        name=request_body["name"],
        description=request_body["description"]
    )

    db.session.add(new_task)
    db.session.commit()


@task_bp.route("", methods = ["GET"])
def read_all_tasks():
    """Read all tasks"""

    task_list = []

    tasks = Task.query.all()
    for task in tasks:
        task_list.append(task)
    
    return jsonify(task_list)
