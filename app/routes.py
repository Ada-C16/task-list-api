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
    # return "nope", 404
# should I respond with error code if table is empty?

@tasks_bp.route("", methods=["POST"], strict_slashes=False)
def create_new_task():
    request_body = request.get_json()
    # if not request_body["completed_at"]:
    new_task = Task(
        title = request_body["title"],
        description = request_body["description"],
        completed_at = request_body["completed_at"]
    )
    db.session.add(new_task)
    db.session.commit()
    return make_response(jsonify(f"task: {new_task.to_dict()}"), 201)
    # return "lovely"

@tasks_bp.route("/<task_id>", methods=["DELETE"], strict_slashes=False)
def delete_task(task_id):
    task_id = int(task_id)
    selected_task = Task.query.get_or_404(task_id)
    db.session.delete(selected_task)
    db.session.commit()
    return make_response(
        {"details": f'Task {selected_task.id} "{selected_task.title}" successfully deleted'}, 200)

@tasks_bp.route("/<task_id>", methods=["GET"], strict_slashes=False)
def get_one_task(task_id):
    task_id = int(task_id)
    selected_task = Task.query.get_or_404(task_id)
    return make_response(selected_task.to_dict(), 200)