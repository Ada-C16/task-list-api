from app import db
from flask import Blueprint, request, abort, jsonify
from app.models.task import Task

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()

    task_response = []
    for task in tasks:
        task_response.append(task.to_dict())

    return jsonify(task_response), 200

@tasks_bp.route("/<task_id>", methods=["GET"])
def get_task(task_id):
    task = Task.query.get(task_id)
    return jsonify(task.to_dict()), 200

@tasks_bp.route("", methods=["POST"])
def post_task():
    form_data = request.get_json()

    new_task = Task(
        title=form_data["title"],
        description=form_data["description"]
    )

    db.session.add(new_task)
    db.session.commit()

    return jsonify(f"Task {new_task.title} created successfully."), 201

