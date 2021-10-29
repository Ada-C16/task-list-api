from flask import Blueprint, jsonify, request, make_response
from flask_sqlalchemy import _make_table
from app import db
from app.models.task import Task

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods = ["POST", "GET"])
def handle_tasks():
    
    if request.method == "POST":
        request_body = request.get_json()
        new_task = Task(title = request_body["title"], description = request_body["description"], completed_at = request_body["completed_at"])
        db.session.add(new_task)
        db.session.commit()

        response_body = create_task_body(new_task)

        return jsonify(response_body), 201
    
    elif request.method == "GET":
        tasks = Task.query.all()
        tasks_response = []
        
        for task in tasks:
            tasks_response.append(dict(id=task.task_id, title=task.title, description=task.description, is_complete=is_complete(task)))
        
        return jsonify(tasks_response), 200

@tasks_bp.route("/<task_id>", methods = ["GET"])
def handle_one_task(task_id):

    task = Task.query.get(task_id)

    # if not task: 
    #     return jsonify(response_body), 404
    
    if request.method == "GET":
        response_body = create_task_body(task)
        return jsonify(response_body), 200


def is_complete(task):
    is_complete = task.completed_at

    if not task.completed_at:
        is_complete = False
    
    return is_complete

def create_task_body(task):
    task_body = {"task": {
    "id": task.task_id,
    "title": task.title,
    "description": task.description,
    "is_complete": is_complete(task)
    }}
    return task_body