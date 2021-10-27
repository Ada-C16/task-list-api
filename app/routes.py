from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request
import datetime

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

# creates a Task
@tasks_bp.route("", methods=["POST"], strict_slashes=False)
def create_task():
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return make_response(
            {"details": f"Invalid data"}, 400
        )

    new_task = Task(
        title = request_body["title"],
        description = request_body["description"],
        completed_at = request_body["completed_at"]
    )

    db.session.add(new_task)
    db.session.commit()

    return make_response(
        {"task":(new_task.to_dict())}, 201
    )
    
# reads all created Tasks
@tasks_bp.route("", methods=["GET"], strict_slashes=False)
def get_tasks():
    tasks_response = []

    if request.args.get("sort") == "asc":
        tasks = Task.query.order_by(Task.title)
    elif request.args.get("sort") == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()

    for task in tasks:
        tasks_response.append(task.to_dict())
    return jsonify(tasks_response), 200

# single Task: read
@tasks_bp.route("/<task_id>", methods=["GET"], strict_slashes=False)
def get_task(task_id):
    task = Task.query.get_or_404(task_id)

    return make_response(
        {"task":(task.to_dict())}, 200
    )

# single Task: update
@tasks_bp.route("/<task_id>", methods=["PUT"], strict_slashes=False)
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body:
        return make_response(
            {"details": f"Invalid data"}, 400
        )

    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()

    return make_response(
        {"task":(task.to_dict())}, 200
    )

# single Task: delete
@tasks_bp.route("/<task_id>", methods=["DELETE"], strict_slashes=False)
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    db.session.delete(task)
    db.session.commit()

    return make_response(
        {"details": f"Task {task.task_id} \"{task.title}\" successfully deleted"}, 200
    )

# single Task: update (patch request to mark Task as complete)
@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"], strict_slashes=False)
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)

    # if task.completed_at is not None:
    task.completed_at = datetime.datetime.now()

    return make_response(
        {"task":(task.to_dict())}, 200
    )

# single Task: update (patch request to mark Task as complete)
@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"], strict_slashes=False)
def incomplete_task(task_id):
    task = Task.query.get_or_404(task_id)

    task.completed_at = None

    # if task.completed_at is not None: # as in it has a date, it's completed
    #     task.completed_at = None

    # elif task.completed_at is None:
    #     task.completed_at = None

    return make_response(
        {"task":(task.to_dict())}, 200
    )