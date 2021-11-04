from flask import Blueprint, jsonify, request
from app import db
from app.models.task import Task
from app.models.goal import Goal
from sqlalchemy import asc, desc
from datetime import datetime, timezone
import requests
import os

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@task_bp.route("", methods=["GET"])
def get_tasks():
    sort_query = request.args.get("sort")
    if sort_query:
        tasks = Task.query.order_by(eval(sort_query)(Task.title))
    else:
        tasks = Task.query.all()
    tasks_response = []
    for task in tasks:
        tasks_response.append({
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)    
        })
    return jsonify(tasks_response), 200
    
@task_bp.route("", methods=["POST"])
def post_tasks():
    request_body = request.get_json()
    try:
        new_task = Task(title=request_body["title"],
        description=request_body["description"],
        completed_at=request_body["completed_at"])

        db.session.add(new_task)
        db.session.commit()

        return {
            "task": {
            "id": new_task.task_id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": bool(new_task.completed_at)  
            }
        }, 201
    except KeyError:
        return {"details": "Invalid data"}, 400 

@task_bp.route("/<task_id>", methods=["GET"])
def get_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return ("", 404)
    response_body = {
        "task": {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": bool(task.completed_at)    
    }}
    if task.goal_id:
        response_body["task"]["goal_id"] = task.goal_id
    return (response_body, 200)
    
@task_bp.route("/<task_id>", methods=["PUT"])
def put_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return ("", 404)
    request_body = request.get_json()
    task.title = request_body["title"]
    task.description = request_body["description"]
    db.session.commit()
    task = Task.query.get(task_id)
    return {
        "task": {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": bool(task.completed_at)  
        }
    }, 200

@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return ("", 404)
    db.session.delete(task)
    db.session.commit()
    return {
        "details": f"Task {task.task_id} \"{task.title}\" successfully deleted"
    }, 200

@task_bp.route("/<task_id>/mark_<completion_status>", methods=["PATCH"])
def handle_task_completion(task_id, completion_status):
    task = Task.query.get(task_id)
    if task is None:
        return ("", 404)
    if completion_status == "complete":
        task.completed_at = datetime.now(timezone.utc)
        requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {os.environ.get('SLACK_API_KEY')}"},
            params={
                "channel": "task-notifications",
                "text": f"Someone just completed the task {task.title}"
            })        
    elif completion_status == "incomplete":
        task.completed_at = None
    db.session.commit()
    return {
            "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)  
            }
        }, 200