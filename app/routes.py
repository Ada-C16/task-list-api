from flask import Blueprint, jsonify, request
from app import db
from app.models.task import Task

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@task_bp.route("", methods=["GET"])
def read_tasks():
    tasks = Task.query.all()
    tasks = [task.to_dict() for task in tasks]
    return jsonify(tasks), 200


@task_bp.route("", methods=["POST"])
def create_task():
    req = request.get_json()
    new_task = Task(
        title=req["title"], description=req["description"], completed_at=req["completed_at"])

    db.session.add(new_task)
    db.session.commit()

    return jsonify({"task": new_task.to_dict()}), 201


@task_bp.route("/<id>", methods=["GET"])
def read_task(id):
    task = Task.query.get(id)
    return jsonify({"task": task.to_dict()}), 200
