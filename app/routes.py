from flask import Blueprint, jsonify, request, make_response
from app import db
from app.models.task import Task

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods = ["POST", "GET"])
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        new_task = Task(
            title = request_body["title"],
            description = request_body["description"],
            completed_at = request_body["completed_at"]
        )
        db.session.add(new_task)
        db.session.commit()

        return make_response({"task": new_task.to_dict()}, 201)
    elif request.method == "GET":
        task_response = []
        tasks = Task.query.all()
        for task in tasks:
            task_response.append(task.to_dict())
        return jsonify(task_response), 200

@tasks_bp.route("/<task_id>", methods = ["GET", "PUT"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if request.method == "GET":
        if task: 
            return make_response({"task": (task.to_dict())}, 200)
        return make_response("", 404)
    



    