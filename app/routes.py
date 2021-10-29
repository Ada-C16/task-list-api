from flask import Blueprint, make_response, request, jsonify
from app.models.task import Task
from app import db

# Blueprints
task_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")


# Helper Functions
def get_task_with_task_id(task_id):
    return Task.query.get_or_404(task_id, description="")

# Routes
@task_bp.route("", methods = ["POST"])
def add_books():
    """Add new books to database"""
    request_body = request.get_json()

    if request_body is None:
        return make_response("You must include a task title and description in order to add your task.", 400)

    if "title" not in request_body or "description" not in request_body:
        return make_response("You must include a task title and description in order to add your task.", 400)

    new_task = Task(
        title=request_body["title"],
        description=request_body["description"]
    )

    db.session.add(new_task)
    db.session.commit()

    return make_response(f"Your task, {new_task.title}, has been created!", 201)


@task_bp.route("", methods = ["GET"])
def read_all_tasks():
    """Read all tasks"""

    # title_query = request.args.get("title")
    tasks = Task.query.all()

    task_response = []
    for task in tasks:
        task_response.append(task.to_dict())
    
    return jsonify(task_response)

# @task_bp.route("<task_id>", methods = ["GET"])
# def read_one_task(task_id):
#     pass