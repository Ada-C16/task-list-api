from flask import Blueprint, jsonify, request, abort, make_response
from app.models.task import Task
from app import db
from datetime import date
import requests
import os
TOKEN = os.environ.get('TOKEN')

task_bp = Blueprint("task", __name__, url_prefix="/tasks")

# Helper Functions
def valid_int(number, parameter_type):
    try:
        int(number)
    except:
        abort(jsonify({"error": f"{parameter_type} must be an int"}), 400)


def get_task_from_id(task_id):
    valid_int(task_id, "task_id")
    return Task.query.get_or_404(task_id, description="{Task not found}")


# Routes
@task_bp.route("", methods=['POST'])
def create_task():
    """CREATES new task in database"""
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return make_response({"details": "Invalid data"}, 400)

    new_task = Task(
        title=request_body["title"],
        description=request_body["description"],
        completed_at=request_body["completed_at"]
    )

    db.session.add(new_task)
    db.session.commit()

    return jsonify({"task": new_task.to_dict()}), 201


@task_bp.route("/<task_id>", methods=["GET"])
def get_task(task_id):
    """READS task with given id"""
    task = get_task_from_id(task_id)

    return jsonify({"task": task.to_dict()}), 200


@task_bp.route("", methods=["GET"])
def get_tasks():
    """READS all tasks"""

    sort_query = request.args.get("sort")

    if sort_query == "asc":
        tasks = Task.query.order_by(Task.title)
    elif sort_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()

    tasks_response = []
    for task in tasks:
        tasks_response.append(
            task.to_dict()
        )
    return jsonify(tasks_response), 200


@task_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    """UPDATES task with given id"""
    if task_id == None:
        return make_response(404)

    else:
        task = get_task_from_id(task_id)
        request_body = request.get_json()

        if "title" in request_body:
            task.title = request_body["title"]
        if "description" in request_body:
            task.description = request_body["description"]
        if "completed_at" in request_body:
            task.completed_at = request_body["completed_at"]

        task_response = task.to_dict()

        db.session.commit()
        return jsonify({"task": task_response}), 200


@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    """DELETES task with given id"""
    task = get_task_from_id(task_id)

    db.session.delete(task)
    db.session.commit()
    return jsonify({"details": f'Task {task_id} "{task.title}" successfully deleted'}), 200


@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def completed_task(task_id):
    """UPDATES completeion status of task by given id"""
    task = get_task_from_id(task_id)
    task_dict = {}
    if not task:
        abort(404)
    else:
        task.completed_at = date.today()
        db.session.commit

        PATH = 'https://slack.com/api/chat.postMessage'
        params = {
            "token": TOKEN,
            "channel": "task-notifications",
            "text": f"Someone just completed the task {task.title}"
        }

        task_dict["task"] = task.to_dict()
        requests.post(PATH, data=params)
        return jsonify(task_dict), 200


@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def incompleted_task(task_id):
    """UPDATES completion status of task by given id with incomplete"""
    task = get_task_from_id(task_id)
    task_dict = {}
    if not task:
        abort(404)
    else:
        task.completed_at = None
        db.session.commit
        task_dict["task"] = task.to_dict()
        return jsonify(task_dict), 200

