from flask import Blueprint, jsonify, request
from flask.helpers import make_response
from app.models.task import Task
import datetime # datetime is a Python package so no need for "from datetime"
from app import db # Why from app and not app.__init___?

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST"])
def create_tasks():
    request_body = request.get_json()
    
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return jsonify({"details": "Invalid data"}), 400
    
    new_task = Task(
        title=request_body["title"], 
        description=request_body["description"], 
        completed_at=request_body["completed_at"]
        )
    
    # SQLAlachemy has a class named session. Inside that class there is an instane method call add.
    # This is telling SQLAlachemy to add new_task to the database. Think of add as a staging process

    db.session.add(new_task) 
    db.session.commit()
    
    response_body = {
        "task": {
            "id": new_task.task_id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": new_task.completed_at is not None
            }
        }
    
    return jsonify(response_body), 201

@tasks_bp.route("", methods=["GET"])
def read_tasks():
    title_query = request.args.get("sort") 
    # Is "sort" a keyword? Can you replace it with "low" or "high"? Why not pass in "title"?
    # Queries are the records (i.e. rows)
    if title_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    elif title_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all() 
    # Because Task is referring to a table, we are capturing all the records (rows) in the table and holding it in tasks.

    task_responses = []
    for task in tasks:
        task_responses.append({
                {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.completed_at is not None
                }
            })
    
    return jsonify(task_responses), 200

@tasks_bp.route("/<task_id>", methods=["GET"])
def read_task(task_id):
    task_id = int(task_id)
    task = Task.query.get(task_id)