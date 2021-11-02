from flask import Blueprint, jsonify, make_response, request, abort
from flask.helpers import make_response
from flask.json import tojson_filter
from flask.signals import request_tearing_down
from werkzeug.utils import header_property
from app.models.task import Task
from app import db
from datetime import datetime
from dotenv import load_dotenv
import requests, os 

load_dotenv()

task_bp = Blueprint("task", __name__,url_prefix ="/tasks")

# Helper Functions
def valid_int(number, parameter_type):
    try:
        int(number)
    except:
        abort(make_response({"error": f"{parameter_type} must be an int"}, 400))

def get_task_from_id(task_id):
    valid_int(task_id, "task_id")
    return Task.query.get_or_404(task_id, description="{task not found}")

def post_slack_message(message):
    token = os.environ.get('SLACK_TOKEN')
    CHANNEL_ID = "C02KD4B5A07"

    Headers = {"Authorization": "Bearer xoxb-" + token}
    data = {
        "channel": CHANNEL_ID,
        "text": message
    }
    response = requests.post("https://slack.com/api/chat.postMessage", headers=Headers, json=data)
    return response


# Routes
@task_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
    # if "title" not in request_body or "description" not in request_body:
        return make_response({"details": "Invalid data"}, 400)

    new_task = Task(
        title=request_body["title"],
        description=request_body["description"],
        completed_at=request_body["completed_at"]
    )

    db.session.add(new_task)
    db.session.commit()

    return make_response({"task": new_task.to_dict()}, 201)

@task_bp.route("", methods=["GET"])
def read_all_tasks():

    sort_query = request.args.get("sort")

    if sort_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    elif sort_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()

    task_response = []
    for task in tasks:
        task_response.append(
            task.to_dict()
        )
    return make_response(jsonify(task_response), 200)

@task_bp.route("/<task_id>", methods=["GET"])
def read_one_task(task_id):
    task = get_task_from_id(task_id)
    return make_response({"task": task.to_dict()}, 200)

@task_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = get_task_from_id(task_id)
    request_body = request.get_json()
    task.title=request_body["title"]
    task.description=request_body["description"]
    db.session.commit()
    return make_response({"task": task.to_dict()}, 200)

@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = get_task_from_id(task_id)
    
    db.session.delete(task)
    db.session.commit()

    return make_response({"details": f"Task {task.task_id} \"{task.title}\" successfully deleted"}, 200)

@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_task_complete(task_id):
    task = get_task_from_id(task_id)
    task.completed_at = datetime.utcnow()
    
    db.session.commit()
    message = f"Someone just completed the task {task.title}"
    post_slack_message(message)

    return make_response({"task": task.to_dict()}, 200)

@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_task_incomplete(task_id):
    task = get_task_from_id(task_id)
    task.completed_at = None
    db.session.commit()

    return make_response({"task": task.to_dict()}, 200)

