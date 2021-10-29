from flask import Blueprint
from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST", "GET"])
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body:
            return make_response("Invalid request"), 400

        
        new_task = Task(
            title=request_body["title"],
            description=request_body["description"],
            completed_at = request_body["completed_at"]
        )
        db.session.add(new_task)
        db.session.commit()

        return make_response(f"Task {new_task.title} has been created"), 201
        
    
    elif request.method == "GET":
        tasks = Task.query.all()
        tasks_response = []
        for task in tasks:
            # list of dictionaries
            tasks_response.append(
                task.to_dict()
            )
        return jsonify(tasks_response), 200

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response ("This task does not exist"), 404
    request_body = request.get_json()
    if request.method == "GET":
        return task.to_dict()
    
    elif request.method == "PUT":
        task.title = request_body["title"]
        task.description = request_body["description"]
        db.session.commit()

        return make_response(f"Task #{task.task_id} successfully updated")

    elif "title" not in request_body or "description" not in request_body:
        return {
            "message": "Request requires both a title and description"
        }, 400
    
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return make_response(f"Task # {task.name} successfully deleted"), 200

    
