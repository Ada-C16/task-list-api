from flask import Blueprint, jsonify, make_response, request
from app.models.task import Task
from app.models.goal import Goal
from app import db

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        tasks = Task.query.all()
        tasks_response = []

        for task in tasks:
            tasks_response.append(
                {
                    "id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": False if task.completed_at == None else True
                }
            )
        return jsonify(tasks_response), 200

    elif request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            # return jsonify("Bad Request"), 400
            return {
                "details": "Invalid data"
            }, 400

        new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        completed_at=request_body["completed_at"])

        db.session.add(new_task)
        db.session.commit()

        new_task_response = {
            "task": {
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": False if new_task.completed_at == None else True
            }
        }
        return jsonify(new_task_response), 201


@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        # return jsonify(f"Task {task_id} not found"), 404
        return make_response("", 404)

    if request.method == "GET":
        return {
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else True
            }
        }

    elif request.method == "PUT":
        form_data = request.get_json()

        task.title = form_data["title"]
        task.description = form_data["description"]

        db.session.commit()

        return {
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else True
            }
        }

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()

        return {
            "details": f'Task {task.task_id} "{task.title}" successfully deleted'
        }
