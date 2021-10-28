from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.task import Task

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST", "GET"], strict_slashes=False)
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        new_task = Task(title=request_body["title"], \
        description=request_body["description"], is_complete=False)

        db.session.add(new_task)
        db.session.commit()

        return {"task": new_task.to_dict()}, 201

    elif request.method == "GET":
        response = []
        tasks = Task.query.all()
        for task in tasks:
            response.append(task.to_dict())
        return jsonify(response), 200


