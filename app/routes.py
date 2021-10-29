from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.task import Task
from app.models.goal import Goal
from sqlalchemy import desc, asc, func
from datetime import datetime

task_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goal_bp", __name__, url_prefix="/goals")

@task_bp.route("", methods = ["POST", "GET"])
def handle_tasks():
    if request.method=="POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
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
            return jsonify({"task": new_task.task_dict()}), 201

    elif request.method == "GET":
        sort_query = request.args.get("sort")
        if sort_query == "desc":
            tasks = Task.query.order_by(desc("title"))
            task_list = [task.task_dict() for task in tasks]
        elif sort_query == "asc":
            tasks = Task.query.order_by(asc("title"))
            task_list = [task.task_dict() for task in tasks]
        else:
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

@task_bp.route("/<task_id>/mark_complete", methods= ["PATCH"])
def mark_complete_task(task_id):
    one_task= Task.query.get(task_id)
    if one_task is None:
        return jsonify(one_task), 404
    current_time = datetime.now()
    one_task.completed_at = current_time
    db.session.commit()
    return jsonify({"task": one_task.task_dict()}), 200

@task_bp.route("/<task_id>/mark_incomplete", methods= ["PATCH"])
def mark_incomplete_task(task_id):
    one_task = Task.query.get(task_id)
    if one_task is None:
        return jsonify(one_task), 404
    one_task.completed_at = None
    db.session.commit()
    return jsonify({"task": one_task.task_dict()}), 200
