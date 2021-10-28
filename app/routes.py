from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET"])
def get_tasks():
    title_query = request.args.get("title")
    if title_query:
        tasks = Task.query.filter(Task.title.contains(title_query))
    else:
        tasks = Task.query.all()

    tasks_response = [task.to_dict() for task in tasks]
    return jsonify(tasks_response), 200


@tasks_bp.route("", methods=["POST"])
def post_new_task():
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body\
        or "completed_at" not in request_body:
        return jsonify({
            "details": "Invalid data"
        }), 400

    new_task = Task(title=request_body["title"],
    description=request_body["description"],
    completed_at=request_body["completed_at"])

    
    db.session.add(new_task)
    db.session.commit()

    response_body = {
        "task": (new_task.to_dict())
    }
    return jsonify(response_body), 201


@tasks_bp.route("/<task_id>", methods=["GET"])
def get_single_task(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return jsonify(None), 404

    response_body = {
        "task": (task.to_dict())
    }
    return jsonify(response_body), 200    


@tasks_bp.route("/<task_id>", methods=["PUT"])
def put_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return jsonify(None), 404

    form_data = request.get_json()
    task.title = form_data["title"]
    task.description = form_data["description"]

    db.session.commit()

    response_body = {
        "task": (task.to_dict())
    }
    return jsonify(response_body), 200  


@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return jsonify(None), 404
    
    db.session.delete(task)
    db.session.commit()
    return jsonify({
        'details': f'Task {task.task_id} "{task.title}" successfully deleted'
        }), 200