from flask import Blueprint, jsonify, request, make_response
from app import db
from app.models.task import Task

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods = ["POST", "GET"])
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return make_response(
                {"details":"Invalid data"}, 400
            )
        new_task = Task(
            title = request_body["title"],
            description = request_body["description"],
            completed_at = request_body["completed_at"]
        )
        db.session.add(new_task)
        db.session.commit()

        return make_response({"task": new_task.to_dict()}, 201)
    elif request.method == "GET":
        if request.args.get("sort") == "asc":
            tasks = Task.query.order_by(Task.title.asc())
        elif request.args.get("sort") == "desc":
            tasks = Task.query.order_by(Task.title.desc())
        else:
            tasks = Task.query.all()
        task_response = []
        for task in tasks:
            task_response.append(task.to_dict())
        return jsonify(task_response), 200

@tasks_bp.route("/<task_id>", methods = ["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if not task: 
        return make_response("", 404)     
    if request.method == "GET":
        return make_response({"task": (task.to_dict())}, 200)    
    elif request.method == "PUT":
        request_body = request.get_json()
        task.title = request_body["title"]
        task.description = request_body["description"]
        if "completed_at" in request_body:
            task.completed_at = request_body["completed_at"]
        else:
            task.completed_at = None
        db.session.commit()
        return make_response({"task": task.to_dict()}, 200)
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return make_response({"details": f'Task {task.task_id} "{task.title}" successfully deleted'})


    



    