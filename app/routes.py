from io import DEFAULT_BUFFER_SIZE
from app import db
from flask import Blueprint, request, jsonify
from app.models.task import Task
from sqlalchemy import asc, desc

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST", "GET"])
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        if (
            "title" not in request_body or 
            "description" not in request_body or 
            "completed_at" not in request_body
        ):
            return jsonify({"details": "Invalid data"}), 400

        new_task = Task(
            title=request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"]
        )

        db.session.add(new_task)
        db.session.commit()

        return jsonify({"task": new_task.task_dict()}), 201

    elif request.method == "GET":
        sort_query = request.args.get("sort")
        if sort_query == "asc":
            tasks = Task.query.order_by(asc("title"))
            task_response = [task.task_dict() for task in tasks]
        elif sort_query == "desc":
            tasks = Task.query.order_by(desc("title"))
            task_response = [task.task_dict() for task in tasks]
        else:
            tasks = Task.query.all()
            task_response = [task.task_dict() for task in tasks]
        return jsonify(task_response), 200


@tasks_bp.route("/<task_id>", methods={"GET", "PUT", "DELETE"})
def handle_one_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return jsonify(task), 404

    if request.method == "GET":
        return ({"task": task.task_dict()}), 200

    elif request.method == "PUT":
        request_body = request.get_json()
        task.title=request_body["title"]
        task.description=request_body["description"]

        db.session.commit()
        return jsonify({"task": task.task_dict()}), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        response_body = f'Task {task.task_id} "{task.title}" successfully deleted'
        return jsonify({"details": response_body}), 200