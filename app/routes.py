from app import db
from flask import Blueprint, request, abort, jsonify, make_response
from datetime import datetime
from dotenv import load_dotenv
from functools import wraps
import os
import requests
from app.models.task import Task
from app.models.goal import Goal

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

# Alternate --> util module/helper functions, route_wrappers.py
def require_task_or_404(endpoint):
    """Decorator to validate input data."""
    @wraps(endpoint) # Makes fn look like func to return
    def fn(*args, **kwargs):
        task_id = kwargs.get("task_id", None)
        task = Task.query.get(task_id)

        if not task:
            return jsonify(None), 404             ## null

        kwargs.pop("task_id")
        return endpoint(*args, task=task, **kwargs)

    return fn

@tasks_bp.route("", methods=["GET"])
def get_tasks():
    """
    Retrieve all tasks. Allows for use of query parameters.
    Returns JSON list of task dictionaries. """
    query = Task.query # Base query

    # Query params, adding to query where indicated
    sort = request.args.get("sort")
    if sort == "asc":
        query = query.order_by(Task.title)
    elif sort == "desc":
        query = query.order_by(Task.title.desc())
    
    query = query.all() # Final query
    
    # Returns jsonified list of task dicionaries
    return jsonify([task.to_dict() for task in query]), 200

@tasks_bp.route("/<task_id>", methods=["GET"])
@require_task_or_404
def get_task(task):
    """Retrieve one stored task by id."""
    return jsonify({"task": task.to_dict()}), 200

@tasks_bp.route("", methods=["POST"])
def post_task():
    """Create a new task from JSON data."""
    form_data = request.get_json()

    #TODO: Refactor to validation decorator helper method

    # All fields must be provided
    mandatory_fields = ["title", "description", "completed_at"]
    for field in mandatory_fields:
        if field not in form_data:
            return jsonify({"details": "Invalid data"}), 400 

    new_task = Task(
        title=form_data["title"],
        description=form_data["description"],
        completed_at=form_data["completed_at"]
    )

    db.session.add(new_task)
    db.session.commit()
    return {"task": new_task.to_dict()}, 201

@tasks_bp.route("/<task_id>", methods=["PUT"])
@require_task_or_404
def put_task(task):
    """Updates task by id."""
    form_data = request.get_json()

    # Updates object from form data
    task.update_from_dict(form_data)
    db.session.commit()

    return {"task": task.to_dict()}, 200

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
@require_task_or_404
def update_task_to_complete(task):
    """Updates task at particular id to completed using PATCH."""
    # Make call to Slack API if task newly completed
    if not task.check_if_completed():
        slack_api_url = "https://slack.com/api/chat.postMessage"
        headers = {"Authorization": "Bearer " + os.environ.get("SLACK_API_KEY")}
        param_payload = {
            "channel": "task-notifications", 
            "text": f"Someone has just completed the task {task.title}"
            }
        
        try:
            requests.post(slack_api_url, headers=headers, params=param_payload)
        
        except Exception as e:
            return f"Error posting message to Slack: {e}"

    # Change task to completed in db
    task.completed_at = datetime.now()
    db.session.commit()

    return {"task": task.to_dict()}, 200

@tasks_bp.route("<task_id>/mark_incomplete", methods=["PATCH"])
@require_task_or_404
def update_task_to_incomplete(task):
    """Updates task at particular id to incomplete using PATCH."""
    task.completed_at = None
    db.session.commit()
    return {"task": task.to_dict()}, 200

@tasks_bp.route("/<task_id>", methods=["DELETE"])
@require_task_or_404
def delete_task(task):
    """Deletes task by id."""
    db.session.delete(task)
    db.session.commit()

    return {
        "details": f"Task {task.id} \"{task.title}\" successfully deleted"
    }, 200

@goals_bp.route("", methods=["GET"])
def get_goals():
    """Retrieve all stored goals."""
    goals = Goal.query.all()

    return jsonify([goal.to_dict() for goal in goals]), 200

@goals_bp.route("/<goal_id>", methods=["GET"])
def get_goal(goal_id):
    """Retrieve one stored goal by id."""
    goal = Goal.query.get_or_404(goal_id)

    return jsonify({"goal": goal.to_dict()}), 200

@goals_bp.route("", methods=["POST"])
def create_goal():
    """Create a new goal from JSON data."""
    form_data = request.get_json()

    if "title" not in form_data:
        return jsonify({"details": "Invalid data"}), 400

    new_goal = Goal(
        title=form_data["title"]
    )
    db.session.add(new_goal)
    db.session.commit()

    return jsonify({"goal": new_goal.to_dict()}), 201

@goals_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    """Updates goal by id."""
    form_data = request.get_json()

    goal = Goal.query.get(goal_id)
    goal.update_from_dict(form_data)
    db.session.commit()

    return jsonify({"goal": goal.to_dict()}), 200

@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    """Deletes goal by id."""
    goal = Goal.query.get(goal_id)

    db.session.delete(goal)
    db.session.commit()

    return {
        "details": f"Goal {goal.id} \"{goal.title}\" successfully deleted"
    }, 200