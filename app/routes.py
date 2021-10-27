from flask import Blueprint, jsonify
from app import db
from app.models.task import Task

# Create tasks blueprint
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET"])
def handle_tasks():
    tasks = Task.query.all()
    tasks_response = []

    for task in tasks:
        tasks_response.append({
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False
        })
    return jsonify(tasks_response)
