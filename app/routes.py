from flask import Blueprint, jsonify, request, abort
from app import db
from app.models.task import Task

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


def is_valid_int(number):
    try:
        int(number)
    except:
        abort(400)


def get_task_by_id(id):
    is_valid_int(id)
    return Task.query.get_or_404(id)


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
    task = get_task_by_id(id)
    return jsonify({"task": task.to_dict()}), 200
