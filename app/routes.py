from sqlalchemy.sql.expression import null
from app import db
from app.models.task import Task
from datetime import datetime
from flask import abort, Blueprint, jsonify, make_response, request
from sqlalchemy import desc 

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

# Posts new task
@tasks_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return jsonify({"details": "Invalid data"}), 400
    new_task = Task(title=request_body["title"],
                    description=request_body["description"],
                    completed_at=request_body["completed_at"])
    
    db.session.add(new_task)
    db.session.commit()

    #return jsonify(tasks_response), 200
    new_task_response = {"task": new_task.to_dict()}
    return jsonify(new_task_response), 201

# Handles all tasks
@tasks_bp.route("", methods=["GET"])
def handle_tasks():
    tasks_response = []
    sort_by = request.args.get('sort')
    if sort_by == "asc":
        tasks = Task.query.order_by(Task.title).all()
    elif sort_by == "desc":
        tasks = Task.query.order_by(desc(Task.title)).all()
    else:
        tasks = Task.query.all()
    for task in tasks:
        tasks_response.append(task.to_dict())
    return jsonify(tasks_response), 200

# Handles one task
@tasks_bp.route("/<task_id>", methods=["GET", "PUT"])
def handle_task(task_id):
    task_id = validate_id_int(task_id)
    task = Task.query.get(task_id)
    if not task:
        return make_response("", 404)
    if request.method == "GET":
        return jsonify({"task": task.to_dict()}), 200
    elif request.method == "PUT":
        request_body = request.get_json()
        task.title=request_body["title"]
        task.description=request_body["description"]
        if "completed_at" in request_body:
            task.completed_at=request_body["completed_at"]

        db.session.commit()
        return jsonify({"task": task.to_dict()}), 200

@tasks_bp.route("<task_id>/<patch_complete>", methods=["PATCH"])
def patch_task(task_id, patch_complete):
    task_id = validate_id_int(task_id)
    task = Task.query.get(task_id)
    if not task:
        return make_response("", 404)
    if patch_complete == "mark_complete":
        task.completed_at=datetime.now()
    elif patch_complete == "mark_incomplete":
        task.completed_at=None
    db.session.commit()
    return jsonify({"task": task.to_dict()}), 200

@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    print(task_id)
    task_id=validate_id_int(task_id)
    
    task = Task.query.get(task_id)

    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"details": f'Task {task_id} "{task.title}" successfully deleted'}), 200
    else:
        return make_response("", 404)

def validate_id_int(task_id):
    try:
        task_id = int(task_id)
        return task_id
    except:
        abort(400, "Error: Task ID needs to be a number")