from flask import Blueprint, jsonify, request, make_response, abort
from app.models.task import Task
from app import db

task_bp = Blueprint("task", __name__, url_prefix="/tasks")

# Make a Task, Get all Tasks
@task_bp.route("", methods = ["POST", "GET"])
def create_tasks():
    if request.method == "POST":
    # Get data from the request
        request_body = request.get_json()

        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return jsonify({"details": "Invalid data"}), 400
    
        new_task = Task(
        title = request_body["title"], 
        description = request_body["description"], 
        completed_at = request_body["completed_at"]) 
        #difficulty = request_body["difficulty"])

        db.session.add(new_task)
        db.session.commit()

        return jsonify({"task": new_task.to_dict()}), 201

    elif request.method == "GET":
        tasks = Task.query.all()
        task_response = []
        for task in tasks:
            task_response.append(task.to_dict())
    return jsonify(task_response), 200

# Get one Task, update one Task, delete one Task
@task_bp.route("/<task_id>", methods = ["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task_id = int(task_id)
    task = Task.query.get(task_id)
    if not task:
        abort(404)
        # return make_response("", 404)
    
    if request.method == "GET":
        return jsonify({"task": task.to_dict()}), 200

    elif request.method == "PUT":
        input_data = request.get_json()
        task.title = input_data["title"]
        task.description = input_data["description"]
        #task.completed_at = input_data["completed_at"]
        db.session.commit()
        return ({"task": task.to_dict()}), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return jsonify({"details": f'Task {task.task_id} "{task.title}" successfully deleted'}), 200