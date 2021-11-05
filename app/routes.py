from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, request, abort, make_response
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import requests

tasks_bp = Blueprint("task_list", __name__, url_prefix="/tasks")

def valid_int(number, parameter_type):
    try:
        int(number)
    except:
        abort(make_response({"error": f"{parameter_type} must be an int"})), 400

def get_task_from_id(task_id):
    valid_int(task_id, "task_id")
    return Task.query.get_or_404(task_id, description="{task not found}")

@tasks_bp.route("", methods=["POST"])
def post_new_task():
    
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body\
         or "completed_at" not in request_body:
        return jsonify({"details": "Invalid data"}), 400

    new_task = Task(title=request_body["title"],
    description=request_body["description"],
    completed_at=request_body["completed_at"])
   
    db.session.add(new_task)
    db.session.commit()

    response_body = {
        "task": (new_task.to_dict())
    }
    return jsonify(response_body), 201

@tasks_bp.route("/<task_id>", methods=["GET"])
def getting_one_task(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return jsonify(None), 404
    
    response_body = {
        "task": (task.to_dict())
    }
    return jsonify(response_body), 200

@tasks_bp.route("", methods=["GET"])
def getting_tasks():
    query = Task.query # Base query

    # Query params, adding to query where indicated
    sort = request.args.get("sort")
    if sort == "asc":
        query = query.order_by(Task.title)
    elif sort == "desc":
        query = query.order_by(Task.title.desc())
    
    query = query.all() # Final query
    
    # Returns jsonified list of task dicionaries
    return jsonify([task.to_dict() for task in query])  

@tasks_bp.route("/<task_id>", methods=["PUT"])
def put_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return jsonify(None), 404

    request_body = request.get_json()
    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()

    response_body = {
        "task": (task.to_dict())
    }
    return jsonify(response_body), 200

@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):    
    task = Task.query.get(task_id)
    if task is None:
        return jsonify(None), 404
    
    db.session.delete(task)
    db.session.commit()
    return jsonify({
        'details': f'Task {task.task_id} "{task.title}" successfully deleted'
        }), 200

# Wave 3/new endpoints updates task as complete
@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def update_task_completion(task_id):
    task= get_task_from_id(task_id)
    task.is_complete=True
    task.completed_at = datetime.now()
    db.session.commit()
    
    slack_key = os.environ.get("SLACK_KEY")
    slack_url = os.environ.get("SLACK_URL")
    channel_id = os.environ.get("CHANNEL_ID")
    requests.post(slack_url, headers= {'Authorization': f"Bearer {slack_key}"}, \
        data= {'channel' : f"{channel_id}", 'text' : f"Someone just completed the task My Beautiful Task"})
    return jsonify({"task": task.to_dict()}), 200

# route that will mark item as incomplete
@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def update_task_incomplete(task_id):
    task= get_task_from_id(task_id)
    
    task.is_complete=False
    task.completed_at=None
    # db.session.add(task)
    db.session.commit()
    return jsonify({"task": task.to_dict()}), 200 