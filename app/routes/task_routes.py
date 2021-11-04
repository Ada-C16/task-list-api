from flask import Blueprint, jsonify, make_response, request, abort
from werkzeug.exceptions import RequestEntityTooLarge
from app import db
from app.models.task import Task
from app.models.goal import Goal
import datetime
import requests
from dotenv import load_dotenv
import os

load_dotenv()

task_bp = Blueprint("task", __name__, url_prefix="/tasks")

# HELPER FUNCTION
def valid_int(number, parameter_type):
    try:
        number = int(number)
    except:
        abort(400, {"error":f"{parameter_type} must be an int"})

def get_task_from_id(task_id):
    valid_int(task_id, "task_id")
    return Task.query.get_or_404(task_id, description="{task not found}")

def get_goal_from_id(goal_id):
    valid_int(goal_id, "goal_id")
    return Goal.query.get_or_404(goal_id)

# TASK ROUTES

# Create a task
@task_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return {"details": "Invalid data"}, 400

    new_task = Task(
        title = request_body["title"],
        description = request_body["description"],
        completed_at = request_body["completed_at"],
    )

    db.session.add(new_task)
    db.session.commit()

    response_body = {"task":new_task.to_dict()}

    return jsonify(response_body), 201

# Read all tasks
@task_bp.route("", methods=["GET"])
def read_all_tasks():
    sort_query = request.args.get("sort")

    # sort asc or desc by title
    if sort_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    elif sort_query =="desc":
        tasks = Task.query.order_by(Task.title.desc())
    # sort asc or desc by id
    elif sort_query == "id_asc":
        tasks = Task.query.order_by(Task.task_id.asc())
    elif sort_query =="id_desc":
        tasks = Task.query.order_by(Task.task_id.desc())
    else:
        tasks = Task.query.all()

    tasks_response = []
    for task in tasks:
        tasks_response.append(
            task.to_dict()
        )

    return jsonify(tasks_response)

# Get task by id
@task_bp.route("/<task_id>", methods=["GET"])
def read_one_task(task_id):
    task = get_task_from_id(task_id)
    response_body = {"task":task.to_dict()}
    return jsonify(response_body),200

# Update task with PUT
@task_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = get_task_from_id(task_id)
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body:
        return {"message":"Request requires a title, description and completed_at info"}, 400
    else:
        task.title = request_body["title"]
        task.description = request_body["description"]
       
        db.session.commit()

        response_body = {"task":task.to_dict()}
        return jsonify(response_body), 200

# Delete a task by id
@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = get_task_from_id(task_id)
    db.session.delete(task)
    db.session.commit()
  
    return {'details': f'Task {task.task_id} "{task.title}" successfully deleted'}

# Mark complete on an incomplete task
@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_task_complete(task_id):
    task = get_task_from_id(task_id)
    task.completed_at = datetime.datetime.now()

    db.session.commit()

    # Slack bot
    bot_token = os.environ.get('BOT_API_TOKEN')
    channel_code = os.environ.get('CHANNEL_CODE')
    url= 'https://slack.com/api/chat.postMessage'
    param = {
        "token":bot_token,
        "channel":channel_code,
        "text":"Testing route. Very cool!"
    }
    requests.post(url, data=param)

    response_body = {"task": task.to_dict()}
    return jsonify(response_body), 200

# Mark incomplete on a completed task
@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_task_incomplete(task_id):
    task = get_task_from_id(task_id)
    task.completed_at = None

    db.session.commit()

    response_body = {"task": task.to_dict()}
    return jsonify(response_body), 200



