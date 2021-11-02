from flask import Blueprint, make_response, request, jsonify
from app.models.task import Task
from app import db
from datetime import date
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

# Blueprints
task_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")

# Helper Functions
def get_task_with_task_id(task_id):
    return Task.query.get_or_404(task_id, description={"details": "Invalid data"})


# Routes
@task_bp.route("", methods = ["POST"])
def add_books():
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
    sort_query = request.args.get("sort")

    if sort_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    elif sort_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
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

def post_slack_message(task):
    slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

    try:
        response = slack_client.chat_postMessage(channel="#task-notifications",
                                text=f"Someone just completed the task {task.title}")

    except SlackApiError as e:
        assert e.response["error"]

@task_bp.route("<task_id>/mark_complete", methods = ["PATCH"])
def update_as_completion(task_id):
    task = get_task_with_task_id(task_id)
    if task.completed_at == None:
        task.completed_at = date.today()

    db.session.commit()

    post_slack_message(task)

    return make_response({"task": task.to_dict()}, 200)


@task_bp.route("<task_id>/mark_incomplete", methods = ["PATCH"])
def update_as_incompletion(task_id):
    task = get_task_with_task_id(task_id)
    if task.completed_at != None:
        task.completed_at = None

    db.session.commit()
    return make_response({"task": task.to_dict()}, 200)

