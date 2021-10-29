from flask import Blueprint, make_response, request, jsonify
from app.models.task import Task
from app import db

# Blueprints
task_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")


# Helper Functions


# Routes
@task_bp.route("", methods = ["GET"])
def read_all_tasks():
    task_list = []

    tasks = Task.query.all()
    for task in tasks:
        task_list.append(task)
    
    return jsonify(task_list)

