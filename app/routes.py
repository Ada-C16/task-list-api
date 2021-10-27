from app import db
from flask import Blueprint, jsonify, make_response, request
from app.models.task import Task
import datetime

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET"], strict_slashes=False)
def get_all_tasks():
    all_tasks = Task.query.all()
    tasks_response = [task.to_dict() for task in all_tasks]
    return make_response(jsonify(tasks_response), 200)
# should I respond with error code if table is empty?

@tasks_bp.route("", methods=["POST"], strict_slashes=False)
def create_new_task():
    request_body = request.get_json()
    new_task = Task(
        title = request_body["title"],
        description = request_body["description"],
        completed_at = datetime.datetime.now(),
    )

    db.session.add(new_task)
    db.session.commit()

    return make_response(f"Task {new_task.title} created", 200)
