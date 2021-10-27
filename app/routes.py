from app import db
from flask import Blueprint, jsonify, make_response
from app.models.task import Task

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET"], strict_slashes=False)
def get_all_tasks():
    all_tasks = Task.query.all()
    tasks_response = [task.to_dict for task in all_tasks]
    return make_response(jsonify(tasks_response), 200)