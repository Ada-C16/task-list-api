from app import db
from flask import Blueprint, request, abort, jsonify, make_response
from datetime import datetime
from dotenv import load_dotenv
import os
import requests
from app.models.task import Task
from app.models.goal import Goal
from app.utils.route_wrappers import require_instance_or_404

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

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
@require_instance_or_404
def get_task(task):
    """Retrieve one stored task by id."""
    if task.goal_id:
        return jsonify({"task": task.goals_to_dict()}), 200
    else:
        return jsonify({"task": task.to_dict()}), 200

@tasks_bp.route("", methods=["POST"])
def post_task():
    """Create a new task from JSON data."""
    form_data = request.get_json()

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
@require_instance_or_404
def put_task(task):
    """Updates task by id."""
    form_data = request.get_json()

    # Updates object from form data
    task.update_from_dict(form_data)
    db.session.commit()

    return {"task": task.to_dict()}, 200

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
@require_instance_or_404
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
@require_instance_or_404
def update_task_to_incomplete(task):
    """Updates task at particular id to incomplete using PATCH."""
    task.completed_at = None
    db.session.commit()
    return {"task": task.to_dict()}, 200

@tasks_bp.route("/<task_id>", methods=["DELETE"])
@require_instance_or_404
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
@require_instance_or_404
def get_goal(goal):
    """Retrieve one stored goal by id."""
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
@require_instance_or_404
def update_goal(goal):
    """Updates goal by id."""
    form_data = request.get_json()

    goal.update_from_dict(form_data)
    db.session.commit()

    return jsonify({"goal": goal.to_dict()}), 200

@goals_bp.route("/<goal_id>", methods=["DELETE"])
@require_instance_or_404
def delete_goal(goal):
    """Deletes goal by id."""
    db.session.delete(goal)
    db.session.commit()

    return {
        "details": f"Goal {goal.id} \"{goal.title}\" successfully deleted"
    }, 200

@goals_bp.route("/<goal_id>/tasks", methods=["POST"])
@require_instance_or_404
def post_tasks_related_to_goal(goal):
    """Adds tasks to goal wiht id."""
    form_data = request.get_json()

    for task_id in form_data["task_ids"]:
        query = Task.query.get(task_id)
        if not query:
            continue
        goal.tasks.append(query)

    db.session.commit()

    return jsonify({
        "id": goal.id,
        "task_ids": [task.id for task in goal.tasks]
    }), 200

@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
@require_instance_or_404
def get_tasks_related_to_goal(goal):
    """Retrieves all tasks associated with goal id."""
    return jsonify(goal.tasks_to_dict()), 200