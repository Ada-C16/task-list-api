from flask import Blueprint, json, jsonify, request
from .models.task import Task
from app import db

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

def task_success_message(task, code):
    return jsonify({
            "task": task.to_dict()
        }), code

def invalid_data_message():
    return jsonify({ "details" : "Invalid data" }), 400


@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():

    if request.method == "POST":
        request_body = request.get_json()

        print(request_body)

        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return invalid_data_message()

        new_task = Task(
            title=request_body["title"],
            description=request_body["description"], 
            completed_at = request_body["completed_at"]
            )
        
        db.session.add(new_task)
        db.session.commit()

        return task_success_message(new_task, 201)

    elif request.method == "GET":

        sort_order = request.args.get("sort")

        if not sort_order:

            tasks = Task.query.all()

        elif sort_order == 'asc':

            tasks = Task.query.order_by(Task.title)

        elif sort_order == 'desc':

            tasks = Task.query.order_by(Task.title.desc())

        return jsonify([task.to_dict() for task in tasks])

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    
    # check if id is an integer
    try:
        int(task_id) == task_id

    except ValueError:
        return invalid_data_message()

    task = Task.query.get(task_id)

    if not task:
        return "", 404

    if request.method == "GET":

        return task_success_message(task, 200)

    elif request.method == "DELETE":

        db.session.delete(task)

        db.session.commit()

        return jsonify({
            "details": f'Task {task_id} "{task.title}" successfully deleted'
        }), 200

    elif request.method == "PUT":
        
        request_body = request.get_json()

        if "title" not in request_body or "description" not in request_body:
            return invalid_data_message()

        task.title = request_body["title"]
        task.description = request_body["description"]

        db.session.commit()

        return task_success_message(task, 200)