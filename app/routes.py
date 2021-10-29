from flask import Blueprint, make_response, request, jsonify
from app.models.task import Task
from app import db

# Blueprints
task_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")


# Helper Functions
def get_task_with_task_id(task_id):
    return Task.query.get_or_404(task_id, description={"details": "Invalid data"})

# Routes
@task_bp.route("", methods = ["POST"])
def add_books():
    """Add new books to database"""
    request_body = request.get_json()

    if request_body is None:
        return make_response({"details": "Invalid data"}, 400)

    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return make_response({"details": "Invalid data"}, 400)

    new_task = Task(
        title=request_body["title"],
        description=request_body["description"],
        completed_at=request_body['completed_at']
    )

    db.session.add(new_task)
    db.session.commit()

    return jsonify({"task": new_task.to_dict()}), 201


@task_bp.route("", methods = ["GET"])
def read_all_tasks():
    """Read all tasks"""

    # title_query = request.args.get("title")
    tasks = Task.query.all()

    task_response = []
    for task in tasks:
        task_response.append(task.to_dict())
    
    return jsonify(task_response), 200

@task_bp.route("/<task_id>", methods = ["GET"])
def read_one_task(task_id):
    task = get_task_with_task_id(task_id)
    return jsonify({"task": task.to_dict()})

@task_bp.route("/<task_id>", methods = ["PUT"])
def update_all_task_info(task_id):
    task = get_task_with_task_id(task_id)
    request_body = request.get_json()

    if "id" in request_body:
        task.id = request_body["id"]
    if "completed_at" in request_body:
        task.completed_at = request_body["completed_at"]

    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()

    return make_response({"task": task.to_dict()}, 200)


@task_bp.route("/<task_id>", methods = ["PATCH"])
def update_some_task_info(task_id):
    request_body = request.get_json()
    task = get_task_with_task_id(task_id)

    if "id" in request_body:
        task.id = request_body["id"]
    if "title" in request_body:
        task.title = request_body["title"]
    if "description" in request_body:
        task.description = request_body["description"]
    if "completed_at" in request_body:
        task.completed_at = request_body["completed_at"]

    db.session.commit()
    return make_response(f"Task {task.title} has been updated.", 201)

@task_bp.route("/<task_id>", methods = ["DELETE"])
def delete_task(task_id):
    task = get_task_with_task_id(task_id)

    db.session.delete(task)
    db.session.commit()

    return jsonify({'details': f'Task {task.id} "{task.title}" successfully deleted'})

