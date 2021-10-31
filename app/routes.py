from flask import Blueprint, jsonify, make_response, request 
from app import db
from app.models.task import Task

tasks_bp = Blueprint("task", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST", "GET"])
def handle_tasks(): 
    request_body = request.get_json()

    if request.method == "POST": 
        if "title" not in request_body or "description" not in request_body \
        or "completed_at" not in request_body: 
            return jsonify({"details": "Invalid data"}), 400

        new_task = Task(title=request_body["title"],
                    description=request_body["description"],
                    completed_at=request_body["completed_at"])

        db.session.add(new_task)
        db.session.commit()

        tasks_dict = {}
        tasks_dict["task"] = new_task.to_dict()
        return jsonify(tasks_dict), 201

    if request.method == "GET":
        tasks_response = []
        if request.args.get("sort") == "asc":
            tasks = Task.query.order_by(Task.title)
        elif request.args.get("sort") == "desc":
            tasks = Task.query.order_by(Task.title.desc())
        else: 
            tasks = Task.query.all()
        for task in tasks: 
            tasks_response.append(task.to_dict())

        return jsonify(tasks_response), 200

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_one_task(task_id):
    task_id = int(task_id)
    task = Task.query.get_or_404(task_id)
    task_dict = {}

    if request.method == "GET":
        task_dict["task"] = task.to_dict()
        return jsonify(task_dict), 200

    if request.method == "PUT": 
        input_data = request.get_json() 
        task.title = input_data["title"]
        task.description = input_data["description"]
        if task.completed_at:
            task.completed_at = input_data["completed_at"]
        task_dict["task"] = task.to_dict()
        db.session.commit()
        return jsonify(task_dict), 200

    if request.method == "DELETE": 
        if task:
            db.session.delete(task)
            db.session.commit()
            return jsonify({'details': f'Task {task.task_id} "{task.title}" successfully deleted'}), 200

