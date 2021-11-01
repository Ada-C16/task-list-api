from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, request, make_response
from sqlalchemy import asc, desc


tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


# client wants to make a POST request to /tasks
@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        task_sort_order = request.args.get("sort")
        if task_sort_order is None:
            tasks = Task.query.all()
        elif task_sort_order == "asc":
            tasks = Task.query.order_by(asc(Task.title))
        elif task_sort_order == "desc":
            tasks = Task.query.order_by(desc(Task.title))

        tasks_response = []
        for task in tasks:
            task_status = True if task.completed_at else False
            tasks_response.append({
                "id": task.task_id,
                "title": task.title, 
                "description": task.description, 
                "is_complete": task_status
            })
        return jsonify(tasks_response), 200
        
        
    if request.method == "POST":
        request_body = request.get_json()

        if "title" not in request_body or "description" not in request_body \
            or "completed_at" not in request_body:
            return jsonify({ "details" : "Invalid data"}), 400
        
        
        new_task = Task(
            title=request_body["title"], 
            description=request_body["description"], 
            completed_at=request_body["completed_at"])
        
        if "completed_at" in request_body:
            new_task.completed_at = request_body["completed_at"]

        task_status = True if new_task.completed_at else False

        db.session.add(new_task)
        db.session.commit()

        return jsonify({
            "task": {
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": task_status,
            },
        }), 201

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_one_task(task_id):
    task_id = int(task_id)
    task = Task.query.get(task_id)

    if task is None:
        return make_response("Not Found", 404)

    if request.method == "GET":
        task_status = True if task.completed_at else False

        return jsonify({
            "task": {
                "id": task.task_id,
                "title": task.title, 
                "description": task.description, 
                "is_complete": task_status
            },
        }), 200

    if request.method == "PUT":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body:
            return jsonify("Not Found"), 404

        task_status = True if task.completed_at else False

        task.title = request_body["title"]
        task.description = request_body["description"]

        db. session.commit()

        return jsonify({
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": task_status
            },
        }), 200

    if request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()

        return jsonify({
            "details": f'Task {task.task_id} "{task.title}" successfully deleted'
            }), 200


