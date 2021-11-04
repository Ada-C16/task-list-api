from app import db
from flask import Blueprint, jsonify, make_response, request
from app.models.task import Task
import datetime
from datetime import datetime as d1
from .helpers import get_task_from_id, send_completion_slack_message

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

# Task CRUD routes
@tasks_bp.route("", methods=["GET"], strict_slashes=False)
def get_all_tasks():
    sort_query = request.args.get("sort")
    if sort_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    elif sort_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()
    tasks_response = [task.to_dict() for task in tasks]
    return make_response(jsonify(tasks_response), 200)

@tasks_bp.route("", methods=["POST"], strict_slashes=False)
def create_new_task():
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body or \
        "completed_at" not in request_body:
        return make_response({"details": "Invalid data"}, 400)
    if request_body['completed_at']:
        try:
            d1.strptime(request_body['completed_at'], '%a, %d %b %Y %H:%M:%S %Z')
        except:
            return make_response({"details": "completed_at must be a date formatted as: Thu, 04 Nov 2021 21:53:34 GMT"}, 404)

    new_task = Task(
        title = request_body["title"],
        description = request_body["description"],
        completed_at = request_body["completed_at"]
    )
    db.session.add(new_task)
    db.session.commit()
    return make_response({"task": new_task.to_dict()}, 201)

# Single task CRUD routes
@tasks_bp.route("/<task_id>", methods=["GET"], strict_slashes=False)
def get_one_task(task_id):
    selected_task = get_task_from_id(task_id)
    return make_response({"task": selected_task.to_dict()}, 200)

@tasks_bp.route("/<task_id>", methods=["PUT"], strict_slashes=False)
def update_task(task_id):
    request_body = request.get_json()
    selected_task = get_task_from_id(task_id)
    if "title" in request_body:
        selected_task.title = request_body["title"]
    if "description" in request_body:
        selected_task.description = request_body["description"]
    if "completed_at" in request_body:
        if request_body['completed_at']:
            try:
                d1.strptime(request_body['completed_at'], '%a, %d %b %Y %H:%M:%S %Z')
            except:
                return make_response({"details": "completed_at must be a date formatted as: Thu, 04 Nov 2021 21:53:34 GMT"})
        selected_task.completed_at = request_body["completed_at"]
    db.session.commit()
    return make_response({"task": selected_task.to_dict()}, 200)

@tasks_bp.route("/<task_id>", methods=["DELETE"], strict_slashes=False)
def delete_task(task_id):
    selected_task = get_task_from_id(task_id)
    db.session.delete(selected_task)
    db.session.commit()
    return make_response(
        {"details": f'Task {selected_task.id} "{selected_task.title}" successfully deleted'}, 200)

# Custom Routes: marking tasks complete or incomplete
@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"], strict_slashes=False)
def mark_incompleted_task_complete(task_id):
    selected_task = get_task_from_id(task_id)
    selected_task.completed_at = datetime.datetime.now()
    db.session.commit()
    send_completion_slack_message(selected_task)
    return make_response({"task": selected_task.to_dict()}, 200)

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"], strict_slashes=False)
def mark_completed_task_incomplete(task_id):
    selected_task = get_task_from_id(task_id)
    selected_task.completed_at = None
    db.session.commit()
    return make_response({"task": selected_task.to_dict()}, 200)