from datetime import datetime
from flask import Blueprint, jsonify, request
from app import db
from app.models.task import Task
from app.models.goal import Goal
from app.helpers import *

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

# POST /tasks Create a new task to the db and return the task body.
@tasks_bp.route("", methods = ["POST"])
def post_new_task():

    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return {"details": "Invalid data"}, 400
    
    new_task = Task(title=request_body["title"], description=request_body["description"], completed_at=request_body["completed_at"])
    db.session.add(new_task)
    db.session.commit()

    return new_task.create_task_response(), 201

# GET /tasks Get a list of all tasks. Handle sort requests via query params.
@tasks_bp.route("", methods = ["GET"])
def get_tasks():
    sort_query = request.args.get("sort")
    title_query = request.args.get("title")

    if sort_query:
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc())

        if sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc())

    elif title_query:
        tasks = Task.query.filter_by(title=title_query)

    else:
        tasks = Task.query.all()

    return jsonify(list_of_tasks(tasks)), 200

# GET /tasks/<task_id>  Get a specific task.
@tasks_bp.route("/<task_id>", methods = ["GET"])
@require_valid_task_id
def get_one_task(task):

    return task.create_task_response(), 200

# PUT /tasks/<task_id> Update a specific task in the db and return the updated task body.
@tasks_bp.route("/<task_id>", methods = ["PUT"])
@require_valid_task_id
def update_one_task(task):

    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body:
        return {"details": "Invalid data"}, 400

    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()

    return task.create_task_response(), 200

# DELETE /tasks/<task_id>  Delete a specific task and return details of deletion.
@tasks_bp.route("/<task_id>", methods = ["DELETE"])
@require_valid_task_id
def delete_one_task(task):

    db.session.delete(task)
    db.session.commit()

    response_body = create_details_response(f"Task {task.task_id} \"{task.title}\" successfully deleted")
    return response_body, 200 

# PATCH /tasks/<task_id>/<completion_status> Update completed at date if marked complete; change to None if marked incomplete.
@tasks_bp.route("/<task_id>/<completion_status>", methods = ["PATCH"])
@require_valid_task_id
def mark_completion_status(task, completion_status):

    if completion_status == "mark_complete":
        task.completed_at = datetime.utcnow()
        send_slack_notification_of_task_completion(task)
    
    elif completion_status == "mark_incomplete":
        task.completed_at = None

    db.session.commit()

    return task.create_task_response(), 200
