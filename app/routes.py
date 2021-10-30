from flask import Blueprint, json, jsonify, request
from .models.task import Task
from app import db
from datetime import datetime
import requests
from dotenv import load_dotenv
import os
load_dotenv()

slack_url_prefix = "https://slack.com/api/"

task_notifications_channel = "C02K5T92807"

slack_api_key = os.environ.get("SLACK_API_KEY")

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

def task_success_message(task, code):
    return jsonify({
            "task": task.to_dict()
        }), code

def invalid_data_message():
    return jsonify({ "details" : "Invalid data" }), 400

def validate_task_id(task_id):

    try:
        int(task_id) == task_id

    except ValueError:
        return invalid_data_message()

    task = Task.query.get(task_id)

    if not task:
        return "", 404


@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():

    if request.method == "POST":
        request_body = request.get_json()

        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return invalid_data_message()

        new_task = Task(
            title=request_body["title"],
            description=request_body["description"],
            completed_at = datetime.today() if request_body["completed_at"] else None
            )
        
        db.session.add(new_task)
        db.session.commit()

        return task_success_message(new_task, 201)

    elif request.method == "GET":

        sort_order = request.args.get("sort")

        if not sort_order:

            tasks = Task.query.all()

        elif sort_order == 'asc':

            tasks = Task.query.order_by(Task.title)

        elif sort_order == 'desc':

            tasks = Task.query.order_by(Task.title.desc())

        return jsonify([task.to_dict() for task in tasks])

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):

    id_error = validate_task_id(task_id)
    if id_error:
        return id_error

    task = Task.query.get(task_id)

    if request.method == "GET":

        return task_success_message(task, 200)

    elif request.method == "DELETE":

        db.session.delete(task)

        db.session.commit()

        return jsonify({
            "details": f'Task {task_id} "{task.title}" successfully deleted'
        }), 200

    elif request.method == "PUT":
        
        request_body = request.get_json()

        if "title" not in request_body or "description" not in request_body:
            return invalid_data_message()

        task.title = request_body["title"]
        task.description = request_body["description"]

        if "completed_at" in request_body:
            task.completed_at = datetime.today()

        db.session.commit()

        return task_success_message(task, 200)

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_task_complete(task_id):
    
    id_error = validate_task_id(task_id)
    if id_error:
        return id_error

    task = Task.query.get(task_id)

    task.completed_at = datetime.today()

    db.session.commit()

    # notify via slack
    # set headers
    headers = {
        "Authorization" : f"Bearer {slack_api_key}"
    }

    params = {
        "channel" : task_notifications_channel,
        "text" : f"Someone just completed the task {task.title}"
    }

    slack_api_action = "chat.postMessage"

    url = slack_url_prefix + slack_api_action

    try:
        response = requests.post(url, params=params, headers=headers)
        r_json = response.json()
        if not r_json["ok"]:
            return invalid_data_message()
    except requests.exceptions.RequestException as e:
        return "Something went wrong when posting a message to Slack.", 404

    return task_success_message(task, 200)

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def handle_task_incomplete(task_id):
    
    id_error = validate_task_id(task_id)
    if id_error:
        return id_error

    task = Task.query.get(task_id)

    task.completed_at = None

    db.session.commit()

    return task_success_message(task, 200)
