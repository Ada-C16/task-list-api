from flask import Blueprint, jsonify, make_response, request
from app.models.task import Task
from app import db

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        new_task = Task(title=request_body["title"],
                            description=request_body["description"],
                            )

        db.session.add(new_task)
        db.session.commit()

        return jsonify(new_task.create_dict()), 201