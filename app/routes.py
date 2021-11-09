from flask import Blueprint
from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request, abort
import datetime, requests, os
import os

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

def valid_int(number, parameter_type):
    try:
        int(number)
    except:
        abort(make_response({"error": f"{parameter_type} must be an int"})), 400

def get_task_from_id(task_id):
    valid_int(task_id, "task_id")
    return Task.query.get_or_404(task_id, description="{task not found}")


@tasks_bp.route("", methods=["POST"])
def create_tasks():
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return make_response({"details": "Invalid data"}), 400

    new_task = Task(
        title=request_body["title"],
        description=request_body["description"],
        completed_at=request_body["completed_at"]
    )
   
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"task": new_task.to_dict()}), 201


@tasks_bp.route("/<task_id>", methods=["GET"])
def read_task(task_id):
    task = get_task_from_id(task_id)
    return {"task": task.to_dict()}


@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = get_task_from_id(task_id)
    db.session.delete(task)
    db.session.commit()
    return make_response({"details":f'Task {task.task_id} "{task.title}" successfully deleted'}), 200

@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task= get_task_from_id(task_id)
    request_body=request.get_json()

    if "title" in request_body:
        task.title=request_body["title"]
    if "description" in request_body:
        task.description=request_body["description"]
    if "completed_at" in request_body:
        task.completed_at=request_body["completed_at"]

    db.session.commit()
    return make_response({"task":task.to_dict()}), 200


@tasks_bp.route("", methods=["GET"])
def read_all_tasks():

    sort_query = request.args.get("sort")
    
    if sort_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    elif sort_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()

    tasks_response = []
    for task in tasks:
        tasks_response.append(
            task.to_dict()
        )
    return jsonify(tasks_response)

#### marking tasks complete ####
@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete_on_incomplete_task(task_id):

    task = get_task_from_id(task_id)

    task.completed_at = datetime.date.today()
    db.session.commit()

    task.post_message_on_slack()
    ####i do not know what is missing here###

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete_on_complete_task(task_id):
    task = get_task_from_id(task_id)

    task.completed_at = None
    db.session.commit()


    





   
     
    

