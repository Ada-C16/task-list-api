from app import db
from flask import Blueprint, request, abort, jsonify
from app.models.task import Task

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()

    if not tasks:
        return jsonify("No tasks found."), 404

    task_response = []
    for task in tasks:
        task_response.append(task.to_dict())

    return jsonify(task_response), 200