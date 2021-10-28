from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.task import Task
from app.models.goal import Goal

task_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goal_bp", __name__, url_prefix="/goals")

@task_bp.route("", methods = ["POST", "GET"])
def handle_tasks():
    if request.method=="POST":
        request_body = request.get_json()
        if "title" or "description" not in request_body:
            return jsonify({"details": "Invalid data"}), 400
        else:
            new_task = Task(
                title=request_body["title"],
                description=request_body["description"],
                completed_at= request_body["completed_at"]
            )
            db.session.add(new_task)
            db.session.commit()
            print(new_task)
            return jsonify(new_task.task_dict()), 201

    elif request.method == "GET":
        tasks = Task.query.all()
        task_list = [task.task_dict() for task in tasks]
        return jsonify(task_list), 200

@task_bp.route("/<task_id>", methods= ["GET", "PUT", "DELETE"])
def handle_one_task(task_id):
    one_task= Task.query.get(task_id)
    if one_task is None:
        return jsonify(one_task), 404
    
    if request.method== "GET":
        return jsonify({"task": one_task.task_dict()}), 200

    elif request.method == "PUT":
        request_body = request.get_json()
        one_task.title=request_body["title"]
        one_task.description=request_body["description"]
        db.session.commit()
        return jsonify({"task": one_task.task_dict()}), 200

    elif request.method == "DELETE":
        db.session.delete(one_task)
        db.session.commit()
        response_body = f'Task {task_id} "{one_task.title}" successfully deleted'
        return jsonify({"details": response_body}), 200


