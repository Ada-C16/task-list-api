from flask import Blueprint, jsonify, request
from app import db
from app.models.task import Task
from sqlalchemy import asc, desc
from datetime import datetime, timezone

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@task_bp.route("", methods=["GET"])
def get_tasks():
    sort_query = request.args.get("sort")
    title_query = request.args.get("title")
    id_sort = request.args.get("idsort")
    if sort_query:
        tasks = Task.query.order_by(eval(sort_query)(Task.title))
    elif title_query:
        tasks = Task.query.filter(Task.title.ilike(('%'+title_query+'%')))
    elif id_sort:
        tasks = Task.query.order_by(eval(id_sort)(Task.task_id))
    else:
        tasks = Task.query.all()
    tasks_response = [Task.to_json(task) for task in tasks]
    return jsonify(tasks_response), 200
    
@task_bp.route("", methods=["POST"])
def post_tasks():
    request_body = request.get_json()
    try:
        new_task = Task.from_json(request_body)
        db.session.add(new_task)
        db.session.commit()
        return {"task": Task.to_json(new_task)}, 201
    except KeyError:
        return {"details": "Invalid data"}, 400 

@task_bp.route("/<task_id>", methods=["GET"])
def get_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return ("", 404)
    response_body = {"task": Task.to_json(task)}
    return (response_body, 200)
    
@task_bp.route("/<task_id>", methods=["PUT"])
def put_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return ("", 404)
    request_body = request.get_json()
    task.title = request_body["title"]
    task.description = request_body["description"]
    db.session.commit()
    task = Task.query.get(task_id)
    return {"task": Task.to_json(task)}, 200

@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return ("", 404)
    db.session.delete(task)
    db.session.commit()
    return {
        "details": f"Task {task.task_id} \"{task.title}\" successfully deleted"
    }, 200

@task_bp.route("/<task_id>/mark_<completion_status>", methods=["PATCH"])
def handle_task_completion(task_id, completion_status):
    task = Task.query.get(task_id)
    if task is None:
        return ("", 404)
    if completion_status == "complete":
        task.completed_at = datetime.now(timezone.utc)
        task.slack_post()        
    elif completion_status == "incomplete":
        task.completed_at = None
    db.session.commit()
    return {"task": Task.to_json(task)}, 200