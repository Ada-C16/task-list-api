from flask import Blueprint, json, jsonify, request
from app.models.task import Task
from app import db
from datetime import datetime
from dotenv import load_dotenv
import os
import requests

load_dotenv()
SLACK_API_KEY = os.environ.get('SLACK_API_KEY')

main_bp = Blueprint("index", __name__)
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@main_bp.route("/", methods=["GET"])
def show_main_page():
    return "<h1 style='font-family: sans-serif'>Please visit /tasks or /goals to see Tasks and Goals.</h1>"

@tasks_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()

    if 'title' not in request_body or 'description' not in request_body \
    or 'completed_at' not in request_body:
        return {"details": "Invalid data"}, 400

    new_task = Task(
        title=request_body['title'],
        description=request_body['description']
    )

    if request_body['completed_at']:
        new_task.completed_at = request_body['completed_at']
        new_task.is_complete = True

    db.session.add(new_task)
    db.session.commit()

    return jsonify({"task": new_task.to_dict()}), 201

@tasks_bp.route("", methods=["GET"])
def read_tasks():
    tasks = Task.query.all()
    tasks_response = []

    sort_by = request.args.get("sort")
    if not sort_by:
        for task in tasks:
            task = task.to_dict()
            tasks_response.append(task)
    if sort_by == "asc":
        sorted_tasks = Task.query.order_by(Task.title.asc())
        for task in sorted_tasks:
            task = task.to_dict()
            tasks_response.append(task)
    elif sort_by == "desc":
        sorted_tasks = Task.query.order_by(Task.title.desc())
        for task in sorted_tasks:
            task = task.to_dict()
            tasks_response.append(task)

    return jsonify(tasks_response), 200

@tasks_bp.route("/<task_id>", methods=["GET"])
def read_one_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return "", 404

    return {"task": task.to_dict()}, 200

@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_one_task(task_id):
    task = Task.query.get(task_id)
    request_body = request.get_json()

    if not task:
        return "", 404

    if 'title' in request_body:
        task.title = request_body['title']
        
    if 'description' in request_body:
        task.description = request_body['description']

    if 'completed_at' in request_body:
        task.completed_at = request_body['completed_at']
        task.is_complete = True
        
    db.session.commit()

    return {"task": task.to_dict()}, 200


@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def update_task_complete(task_id):
    task = Task.query.get(task_id)

    if not task:
        return "", 404

    task.is_complete = True
    task.completed_at = datetime.now()
    
    db.session.commit()

    requests.post(
        'https://slack.com/api/chat.postMessage',
        params={
            'channel': 'task-notifications',
            'text': f"Someone just completed the task {task.title}"},
        headers={'Authorization': f'Bearer {SLACK_API_KEY}'}
    )

    return {"task": task.to_dict()}, 200

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["POST", "PATCH"])
def update_task_incomplete(task_id):
    task = Task.query.get(task_id)

    if not task:
        return "", 404

    task.is_complete = False
    task.completed_at = None
    
    db.session.commit()

    task_response = task.to_dict()

    return {"task": task_response}, 200

@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return "", 404

    request_body = request.get_json()

    if "title" in request_body:
        task.title = request_body['title']
    if "description" in request_body:
        task.description = request_body['description']

    db.session.commit()
    
    return {"task": task.to_dict()}, 200

@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return "", 404

    db.session.delete(task)
    db.session.commit()

    return {"details": f'Task {task_id} "{task.title}" successfully deleted'}, 200