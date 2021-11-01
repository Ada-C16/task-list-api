from app import db
from app.models.task import Task
from flask import Blueprint, request, jsonify

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@task_bp.routes("", methods=["POST"])
def handle_tasks():
    if request.methods == "POST":
        request_body = request.get_json()
        new_task = Task(
            name= request_body["name"],
            description= request_body["description"],
            

        )

