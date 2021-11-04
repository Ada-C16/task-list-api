from flask import Blueprint
from app import db, SLACK_API_KEY
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request, abort
from datetime import datetime
import requests

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

# Helper Functions
def valid_int(number, parameter_type):
    try:
        int(number)
    except:
        abort(make_response({"error": f"{parameter_type} must be an int"})), 400

def get_task_from_id(task_id):
    valid_int(task_id, "task_id")
    return Task.query.get_or_404(task_id, description="{task not found}")

#Wave 2 asc and desc
@tasks_bp.route("", methods=["GET"])
def read_all_tasks():
    tasks = Task.query.all()
    tasks_response = []
    sort_by = request.args.get("sort")

    if sort_by == "asc":
        sorted_tasks = Task.query.order_by(Task.title.asc())
        for task in sorted_tasks:
            task = task.to_dict()
            tasks_response.append(task)
        return jsonify(tasks_response)

    elif sort_by == "desc":
        sorted_tasks = Task.query.order_by(Task.title.desc())
        for task in sorted_tasks:
            task = task.to_dict()
            tasks_response.append(task)

        return jsonify(tasks_response)

    if not tasks:
        return jsonify(tasks_response), 200
    
    if not sort_by:
        for task in tasks:
            task = task.to_dict()
            tasks_response.append(task)
        return jsonify(tasks_response), 200

#routes
@tasks_bp.route("", methods=["POST"])
def create_tasks():
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return make_response({"details": "Invalid data"}), 400

    new_task = Task(
        title=request_body["title"],
        description=request_body["description"],
        completed_at=request_body["completed_at"]
    )
    
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"task": new_task.to_dict()}), 201

@tasks_bp.route("/<task_id>", methods=["GET"])
def read_task(task_id):
    task = get_task_from_id(task_id)
    return {"task": task.to_dict()}

@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task= get_task_from_id(task_id)
    request_body=request.get_json()

    if "title" in request_body:
        task.title=request_body["title"]
    if "description" in request_body:
        task.description=request_body["description"]
    if "completed_at" in request_body:
        task.completed_at=request_body["completed_at"]

    db.session.commit()
    return make_response({"task":task.to_dict()}), 200

@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = get_task_from_id(task_id)
    db.session.delete(task)
    db.session.commit()
    return make_response({"details":f'Task {task.task_id} "{task.title}" successfully deleted'}), 200

def slack_bot(task):
    url = 'https://slack.com/api/chat.postMessage'
    message = f"Someone just completed the task {task.title}"
    query_params = {
        "token": SLACK_API_KEY,
        "channel": 'lizet-bot-practice',
        "text": message
    }
    return requests.post(url, data=query_params).json()

# Wave 3/new endpoints updates task as complete
@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def update_task_completion(task_id):
    task= get_task_from_id(task_id)
    task.is_complete=True
    task.completed_at = datetime.now()
    # db.session.add(task)
    db.session.commit()
    slack_bot(task)
    return jsonify({"task": task.to_dict()}), 200


# Wave 3/new endpoints will mark item as incomplete
@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def update_task_incomplete(task_id):
    task= get_task_from_id(task_id)
    
    task.is_complete=False
    task.completed_at=None
    # db.session.add(task)
    db.session.commit()
    return jsonify({"task": task.to_dict()}), 200