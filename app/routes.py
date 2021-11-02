from datetime import datetime
from operator import truediv
from flask import Blueprint, jsonify, request, make_response
from flask_sqlalchemy import _make_table
from app import db
from app.models.task import Task

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods = ["POST", "GET"])
def handle_tasks():
    
    if request.method == "POST":
        request_body = request.get_json()

        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return jsonify(create_details("Invalid data")), 400

        new_task = Task(title = request_body["title"], description = request_body["description"], completed_at = request_body["completed_at"])
        db.session.add(new_task)
        db.session.commit()

        response_body = create_task_body(new_task)

        return jsonify(response_body), 201
    
    elif request.method == "GET":
        sort_query = request.args.get("sort")

        if sort_query:
        
            if sort_query == "asc":
                tasks = Task.query.order_by(Task.title.asc())

            if sort_query == "desc":
                tasks = Task.query.order_by(Task.title.desc())
        else:
            tasks = Task.query.all()

        return jsonify_list_of_tasks(tasks)

@tasks_bp.route("/<task_id>", methods = ["GET", "PUT", "DELETE"])
def handle_one_task(task_id):

    task = Task.query.get(task_id)

    if not task: 
        return make_response("", 404)

    if request.method == "GET":
        response_body = create_task_body(task)
        return jsonify(response_body), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()

        return jsonify(create_details(f"Task {task.task_id} \"{task.title}\" successfully deleted"
        )), 200 

    elif request.method == "PUT":
        updated_task_information = request.get_json()
        task.title = updated_task_information["title"]
        task.description = updated_task_information["description"]

        db.session.commit()

        response_body = create_task_body(task)
        return jsonify(response_body), 200

@tasks_bp.route("/<task_id>/<completion_status>", methods = ["PATCH"])
def mark_completion_status(task_id, completion_status):
    task = Task.query.get(task_id)

    if not task: 
        return make_response("", 404)
    
    if completion_status == "mark_complete":
        task.completed_at = datetime.utcnow()

    elif completion_status == "mark_incomplete":
        task.completed_at = None

    db.session.commit()

    response_body = create_task_body(task)
    return jsonify(response_body), 200

### Helper functions ###

def is_complete(task):
    is_complete = task.completed_at

    if not task.completed_at:
        is_complete = False

    else:
        is_complete = True

    return is_complete

def create_task_body(task):
    task_body = {"task": {
    "id": task.task_id,
    "title": task.title,
    "description": task.description,
    "is_complete": is_complete(task)
    }}
    return task_body

def create_details(details):
    
    response = {"details": details}
    
    return response

def jsonify_list_of_tasks(tasks):
        
    list_of_tasks = []
        
    for task in tasks:
        list_of_tasks.append(dict(id=task.task_id, title=task.title, description=task.description, is_complete=is_complete(task)))

    return jsonify(list_of_tasks)