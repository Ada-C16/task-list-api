import datetime
from app import db
from app.models.task import Task
from flask import request, Blueprint, make_response, jsonify
from datetime import datetime
from tests.conftest import completed_task

task_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")

@task_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    task_response = []
    if request.method == "GET":
        if request.args.get("sort") == "asc":
            tasks = Task.query.order_by(Task.title.asc())
        elif request.args.get("sort") == "desc":
            tasks = Task.query.order_by(Task.title.desc())
        else:
            tasks = Task.query.all()
        task_response = [task.to_dict() for task in tasks]
        return jsonify(task_response), 200
    elif request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return make_response({"details": "Invalid data"}, 400) 
        new_task = Task(title=request_body["title"],
                        description=request_body["description"], 
                        completed_at=request_body["completed_at"])
        db.session.add(new_task)
        db.session.commit()
        return make_response({"task": new_task.to_dict()}, 201)

@task_bp.route("/<task_id>", methods=["GET", "DELETE", "PUT", "PATCH"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if request.method == "GET":
        if not task:
            return make_response(f"Book {task_id} not found", 404)
        return {"task": task.to_dict()}
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
        task.title = request_body["title"] if "title" in request_body else task.title
        task.description = request_body["description"] if "description" in request_body else task.description
        task.completed_at = request_body["completed_at"] if "completed_at" in request_body else task.completed_at
        return make_response({"task": task.to_dict()}, 200)

@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_task_complete(task_id):
        task = Task.query.get(task_id)
        if not task:
            return make_response(f"Book {task_id} not found", 404)
        task.completed_at = datetime.utcnow()
        return make_response({"task": task.to_dict()}, 200)

@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def handle_task_incomplete(task_id):
        task = Task.query.get(task_id)
        if not task:
            return make_response(f"Book {task_id} not found", 404)
        task.completed_at = None
        return make_response({"task": task.to_dict()}, 200)





