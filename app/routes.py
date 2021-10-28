from app import db
from app.models.task import Task
from flask import request, Blueprint, make_response, jsonify

from tests.conftest import completed_task

task_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")

@task_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    task_response = []
    if request.method == "GET":
        tasks = Task.query.all()
        for task in tasks:
            task_response.append(to_dict(task))
        print(task_response)
        return jsonify(task_response), 200
    elif request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return make_response({"details": "Invalid data"}, 400) 
        if request_body["completed_at"] == None:
            completion_status = None
        new_task = Task(title=request_body["title"],
                        description=request_body["description"], 
                        completed_at=completion_status)
        db.session.add(new_task)
        db.session.commit()
        return make_response({"task": to_dict(new_task)}, 201)

@task_bp.route("/<task_id>", methods=["GET", "DELETE", "PUT"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if request.method == "GET":
        if not task:
            return make_response(f"Book {task_id} not found", 404)
        return {"task": to_dict(task)}
    elif request.method == "DELETE":
        if not task:
            return make_response("", 404)
        db.session.delete(task)
        db.session.commit()
        return {"details": f'Task {task.task_id} "{task.title}" successfully deleted'}
    elif request.method == "PUT":
        if not task:
            return make_response("", 404)
        request_body = request.get_json()
        if "title" in request_body:
            task.title = request_body["title"]
        if "description" in request_body:
            task.description = request_body["description"]
        if "completed_at" in request_body:
            task.completed_at = request_body["completed_at"]
        return make_response({"task": to_dict(task)}, 200)
def to_dict(task):
    return {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.completed_at
    }
