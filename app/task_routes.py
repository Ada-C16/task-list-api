from flask import Blueprint, jsonify, abort, request 
from app import db
from app.models.task import Task
from datetime import datetime
import requests
import os
from dotenv import load_dotenv 

load_dotenv()

tasks_bp = Blueprint("task", __name__, url_prefix="/tasks")

def valid_id(model, id):
    """If ID is an int, returns the model object with that ID.
        If ID is not an int, returns 400.
        If model object with that ID doesn't exist, returns 404."""
    try:
        id = int(id)
    except: 
        abort(400, {"error": "invalid id"})
    return model.query.get_or_404(id)

@tasks_bp.route("", methods=["POST", "GET"])
def handle_tasks(): 
    """Handles post and get requests for tasks at /tasks"""
    request_body = request.get_json()

    if request.method == "POST": 
        if "title" not in request_body or "description" not in request_body \
        or "completed_at" not in request_body: 
            return {"details": "Invalid data"}, 400

        new_task = Task(title=request_body["title"],
                    description=request_body["description"],
                    completed_at=request_body["completed_at"])

        db.session.add(new_task)
        db.session.commit()

        tasks_dict = {}
        tasks_dict["task"] = new_task.to_dict()
        return tasks_dict, 201

    if request.method == "GET":
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

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_one_task(task_id):
    """Handles get, put, and delete requests \
        for one task with a given id at /tasks/<task_id>"""
    task_dict = {}
    task = valid_id(Task, task_id)

    if request.method == "GET":
        task_dict["task"] = task.to_dict()
        return task_dict, 200

    if request.method == "PUT": 
        input_data = request.get_json() 
        task.title = input_data["title"]
        task.description = input_data["description"]
        if task.completed_at:
            task.completed_at = input_data["completed_at"]
        task_dict["task"] = task.to_dict()
        db.session.commit()
        return task_dict, 200

    if request.method == "DELETE": 
        if task:
            db.session.delete(task)
            db.session.commit()
            return {'details': f'Task {task.task_id} "{task.title}" successfully deleted'}, 200

def post_task_completion_to_slack(task):
    """Posts a message to slack stating that someone completed a task with the task title"""
    SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
    SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL")
    url = "https://slack.com/api/chat.postMessage"
    message = f"Somone just completed task {task.title}"
    query_params = {
        "channel": SLACK_CHANNEL,
        "text": message
        }
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}"
    }
    # response variable left for debugging purposes
    response = requests.post(url, data=query_params, headers=headers)


@tasks_bp.route("/<task_id>/<completion_status>", methods=["PATCH"])
def mark_completion_status(task_id, completion_status): 
    """Returns task_dict and changes value of task.completed_at. \
        If user goes to /tasks/<task_id>/mark_complete, \
            task.completed_at has a value of current date and time \
            and a message is posted to slack.
        If user goes to /tasks/<task_id>/mark_incomplete, \
            task.completed_at has a value of None"""
    task_dict = {}
    task = valid_id(Task, task_id)

    if completion_status == "mark_complete":
        task.completed_at = datetime.date
        post_task_completion_to_slack(task)
    elif completion_status == "mark_incomplete":
        task.completed_at = None

    task_dict["task"] = task.to_dict()
    return task_dict, 200
