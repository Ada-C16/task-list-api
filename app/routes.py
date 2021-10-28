from app import db
from flask import Blueprint, jsonify, request, make_response
from app.models.task import Task

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST", "GET"])
def handle_tasks():
    if request.method == "POST":

        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return 400

        new_task = Task(
            title = request_body["title"],
            description = request_body["description"],
            completed_at = request_body["completed_at"]
        )

        db.session.add(new_task)
        db.session.commit()

        new_task_response = {
            "id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": new_task.is_complete
        }

        return jsonify(new_task_response), 201

    elif request.method == "GET":
        tasks = Task.query.all()

    tasks_response = []
    for task in tasks:
        tasks_response.append(
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.is_complete
            }
        )
    return jsonify(tasks_response)

@tasks_bp.route("/task_id>", methods=["GET", "PUT", "DELETE"])
def handle_one_task_at_a_time(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return jsonify(task_id), 404

    if request.method == "GET":
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete
        }
    
    if request.method == "PUT":
        if task is None:
            return jsonify(task_id), 404
    
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body:
            return make_response("Invald Request", 400)

        task.title = request_body["title"]
        task.description = request_body["description"]

        db.session.commit()

        return jsonify(task_id), 201

    if request.method == "DELETE":
        if task is None:
            return jsonify(task_id), 404

        db.session.delete(task_id)
        db.session.commit()

        return jsonify(task_id), 200

        