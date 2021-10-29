from flask import Blueprint, jsonify, request, abort, make_response
from app import db
from app.models.task import Task

tasks_bp = Blueprint("tasks_bp",__name__, url_prefix="/tasks")

# add task to taks database
@tasks_bp.route('', methods=["POST"])
def new_task():
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return {"details": "Invalid data"}, 400

    new_task = Task(
        title = request_body["title"],
        description = request_body["description"],
        completed_at = request_body["completed_at"]
    )

    db.session.add(new_task)
    db.session.commit()

    return {"task": new_task.to_dict()}, 201

# get tasks
@tasks_bp.route('', methods=["GET"])
def get_all_tasks():
    tasks = Task.query.all()
    response_tasks = []

    for task in tasks:
        response_tasks.append(task.to_dict())

    return jsonify(response_tasks), 200

@tasks_bp.route('/<task_id>', methods=["GET", "PUT", "DELETE"])
def get_one_task(task_id):
    task = Task.query.get(task_id)
    
    if not task:
            return make_response('', 404)
    
    if request.method == "GET":
        return {"task": task.to_dict()}, 200

    elif request.method == "PUT":
        request_body = request.get_json()

        task.title = request_body["title"]
        task.description = request_body["description"]

        #Save Action
        db.session.commit()

        return {"task": task.to_dict()}, 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()

        return {"details": f'Task {task_id} "{task.title}" successfully deleted'}, 200




