from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request
from datetime import datetime
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST", "GET"])
def handle_tasks():
    
    if request.method == "POST":
        request_body = request.get_json()

        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return make_response({"details":"Invalid data"}, 400)

        new_task = Task(
            title=request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"]
        )

        db.session.add(new_task)
        db.session.commit()

        
        # return (f"Task list {new_task.title} created", 201)#####
        return jsonify({"task": new_task.to_dict()}), 201

    elif request.method == "GET":
        # tasks=Task.query.all()
        # tasks_response = []
        # for task in tasks:
        #     tasks_response.append(task.to_dict())
        # return jsonify(tasks_response), 200
        
        task_response= []
        if request.args.get('sort') == 'asc':
            tasks = Task.query.order_by(Task.title.asc()).all()
        elif request.args.get('sort') == 'desc':
            tasks = Task.query.order_by(Task.title.desc()).all()
        
        else:
            tasks = Task.query.all()

        for task in tasks:
            task_response.append(task.to_dict())
        return jsonify(task_response), 200

@tasks_bp.route("/<task_id>", methods= ["GET", "PUT", "DELETE"])
def handle_task(task_id):
    # task_id = int(task_id)
    task = Task.query.get(task_id)
    

    if task is None:
        return make_response(f"Task {task_id} not found"), 404
        # return make_response(
        #     f"Task {task_id} not found"
        # ), 404##############
    if request.method == "GET":
        
        return jsonify({"task": task.to_dict()}), 200
        
    elif request.method == "PUT":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body:
            return make_response("invalid request"), 400

        task.title=request_body["title"]
        task.description=request_body["description"]
        # task.is_complete=request_body["is complete"]
        # task.completed_at=request_body["completed_at"]

        db.session.commit()
        # return (task_id,jsonify({"details": task.title}), 200)
        return jsonify({"task": task.to_dict()}),200
        # return make_response(f"Task {task.title} successfully updated"), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        # return make_response(f"Task {task_id} successfully deleted"), 200
        # return (jsonify({"details": task.title}f"successfully deleted"), 200)
        return ({'details': f'Task {task_id} "{task.title}" successfully deleted'}), 200


@tasks_bp.route("/<id>/<completion_status>", methods=["PATCH"])
def mark_complete(id, completion_status):
    task = Task.query.get(id)
    if task is None:
        return make_response("", 404)
    if completion_status == "mark_complete":
        task.completed_at = datetime.date
    if completion_status == "mark_incomplete":
        task.completed_at = None
    
    return jsonify({"task":task.to_dict()})