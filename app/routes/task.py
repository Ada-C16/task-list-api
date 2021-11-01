from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.task import Task
from sqlalchemy import desc
from datetime import date

tasks_bp = Blueprint("task", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET"])
def tasks():
    sort_query = request.args.get("sort")
    if sort_query:
        if sort_query == "asc":
            tasks = Task.query.order_by("title") 
        elif sort_query == "desc": 
            tasks = Task.query.order_by(desc("title")) 
        else:
            tasks = Task.query.all()
    else: 
        tasks = Task.query.all()

    tasks_response = [task.to_json() for task in tasks]     
    return jsonify(tasks_response), 200


@tasks_bp.route("", methods=["POST"])
def add_task():
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body\
    or "completed_at" not in request_body:
        return { "details" : "Invalid data" }, 400

    new_task = Task(
        title=request_body["title"],
        description=request_body["description"],
        completed_at=request_body["completed_at"]
    )

    db.session.add(new_task)
    db.session.commit()
    return jsonify({ "task" : new_task.to_json() }), 201


@tasks_bp.route("/<task_id>", methods=["GET"])
def task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    return jsonify({ "task" : task.to_json() }), 200


@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    request_data = request.get_json()
    task.title = request_data["title"]
    task.description = request_data["description"]
    db.session.commit()

    task_dict = task.to_json(
        title=request_data["title"], 
        description=request_data["description"])

    return jsonify({ "task" : task_dict }), 200


@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)
    
    db.session.delete(task)
    db.session.commit()
    
    id, title = task.task_id, task.title 
    return jsonify(
        { "details" : f"Task {id} \"{title}\" successfully deleted" }), 200


@tasks_bp.route("/<task_id>/<completion_mark>", methods=["PATCH"])
def mark_task_complete_or_incomplete(task_id, completion_mark):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    if completion_mark == "mark_complete":
        task.completed_at = date.today()
        task.post_to_slack()
    elif completion_mark == "mark_incomplete":
        task.completed_at = None 

    return jsonify({ "task" : task.to_json() }), 200 

