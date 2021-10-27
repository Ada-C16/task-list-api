from flask import Blueprint, jsonify, make_response
from app import db
from app.models.task import Task

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@task_bp.route("", methods=["GET"])
def read_tasks():
    tasks = Task.query.all()
    tasks = [task.to_dict() for task in tasks]
    return jsonify(tasks), 200
