from flask import Blueprint, jsonify, request, abort
from app import db
from app.models.task import Task
from app.models.goal import Goal
from datetime import datetime, timezone
import requests
import os

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

goal_bp = Blueprint("goals", __name__, url_prefix="/goals")


def is_valid_int(number):
    """Check for valid int and abort request with 400 if invalid"""
    try:
        int(number)
    except:
        abort(400)


def get_task_by_id(id):
    """Grab one task from the database by id and return it"""
    is_valid_int(id)
    return Task.query.get_or_404(id)


def get_goal_by_id(id):
    """Grab one goal from the database by id and return it"""
    is_valid_int(id)
    return Goal.query.get_or_404(id)


def notify_slack_bot(task):
    """Send a post request to the slack api with the name of a specified task"""
    SLACK_API_KEY = os.environ.get("SLACK_API_KEY")

    req_body = {
        "channel": "task-notifications",
        "text": f"Someone just completed the task {task.title}"
    }

    headers = {
        "Authorization": f"Bearer {SLACK_API_KEY}"
    }

    path = "https://slack.com/api/chat.postMessage"

    requests.post(path, json=req_body, headers=headers)


@task_bp.route("", methods=["GET"])
def read_tasks():
    """This is a route to get all saved tasks
    Optional query parameter:
        - sort: can be "asc" or "desc" to sort tasks by title
    Returns:
        - JSON array of tasks represented as objects, optionally sorted by title
        - 200 status code
    """
    sort_query = request.args.get("sort")
    if sort_query == 'asc':
        tasks = Task.query.order_by(Task.title).all()
    elif sort_query == 'desc':
        tasks = Task.query.order_by(Task.title.desc()).all()
    else:
        tasks = Task.query.all()
    tasks = [task.to_dict() for task in tasks]
    return jsonify(tasks), 200


@task_bp.route("", methods=["POST"])
def create_task():
    """This is a route to create a new task
    Required request body:
        - JSON object with title (string), description (string), and completed_at (datetime or null) keys
    Returns:
        - If valid data provided:
            - JSON object with task data saved to the db
            - 201 status code
        - If invalid data provided:
            - JSON error message
            - 400 status code
    """
    req = request.get_json()

    try:
        new_task = Task(
            title=req["title"], description=req["description"], completed_at=req["completed_at"])
    except:
        return jsonify({"details": "Invalid data"}), 400

    db.session.add(new_task)
    db.session.commit()

    return jsonify({"task": new_task.to_dict()}), 201


@task_bp.route("/<id>", methods=["GET"])
def read_task(id):
    """This is a route to get one task of a specified id
    Returns:
        - If valid id provided but no task found:
            - 404 status code
        - If invalid id provided:
            - 400 status code
        - If valid is is provided and task is found:
            - 200 status code
            - JSON object representing task with requested id
    """
    task = get_task_by_id(id)
    return jsonify({"task": task.to_dict()}), 200


@task_bp.route("/<id>", methods=["PUT"])
def update_task(id):
    """This is a route to update one task of a specified id
    Required request body:
        - JSON object with title (string) and description (string)
    Returns:
        - If invalid data is provided:
            - 400 status code
            - JSON error message
        - If task id is not found:
            - 404 status code
        - If task id is found and valid data is provided:
            - 200 status code
            - JSON object representing updated task data
    """
    task = get_task_by_id(id)
    req = request.get_json()

    try:
        task.title = req["title"]
        task.description = req["description"]
    except:
        return jsonify({"details": "Invalid data"}), 400

    db.session.commit()
    return jsonify({"task": task.to_dict()}), 200


@task_bp.route("/<id>", methods=["DELETE"])
def delete_task(id):
    """This is a route to delete a task of a specified id
    Returns:
        - If invalid id is provided:
            - 400 status code
        - If valid id is provided but not task is found:
            - 404 status code
        - If task is found:
            - 200 status code
            - JSON object with a message indicating task was deleted
    """
    task = get_task_by_id(id)
    db.session.delete(task)
    db.session.commit()

    response_body = {
        "details": f'Task {task.id} "{task.title}" successfully deleted'
    }
    return jsonify(response_body), 200


@task_bp.route("/<id>/mark_complete", methods=["PATCH"])
def mark_complete(id):
    """This is a route to mark a task (specified by id) complete
    Returns:
        - If invalid id:
            - 400 status code
        - If valid id but no task found:
            - 404 status code
        - If task found:
            - JSON object representing updated task
            - Task's completed_at attribute is changed to the current UTC time in the db
            - 200 status code
    """
    task = get_task_by_id(id)
    task.completed_at = datetime.now(timezone.utc)
    db.session.commit()

    notify_slack_bot(task)

    return jsonify({"task": task.to_dict()}), 200


@task_bp.route("/<id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(id):
    """This is a route to mark a task (specified by id) incomplete
    Returns:
        - if invalid id:
            - 400 status code
        - if valid id but no task found:
            - 404 status code
        - If task found:
            - 200 status code
            - JSON object representing updated task
            - Task's completed_at attribute is changed to None
    """
    task = get_task_by_id(id)
    task.completed_at = None
    db.session.commit()
    return jsonify({"task": task.to_dict()}), 200


@goal_bp.route("", methods=["POST"])
def create_goal():
    """This is a route to create a new goal
    Required request body:
        - JSON object containing a title (string)
    Returns:
        - if invalid data:
            - 400 status code
            - JSON error message
        - if valid data:
            - 200 status code
            - JSON object representing the new goal added to the db
    """
    req = request.get_json()

    try:
        new_goal = Goal(title=req["title"])
    except:
        return jsonify({"details": "Invalid data"}), 400

    db.session.add(new_goal)
    db.session.commit()

    return jsonify({"goal": new_goal.to_dict()}), 201


@goal_bp.route("", methods=["GET"])
def read_goals():
    """This is a route to get all of the saved goals
    Returns:
        - JSON array of objects representing saved goals
        - 200 status code
    """
    goals = Goal.query.all()
    goals = [goal.to_dict() for goal in goals]
    return jsonify(goals), 200


@goal_bp.route("/<id>", methods=["GET"])
def read_goal(id):
    """This is a route to get one goal of a specified id
    Returns:
        - If invalid id:
            - 400 status code
        - If valid id but no goal found:
            - 404 status code
        - If goal found:
            - 200 status code
            - JSON object representing goal with specified id
    """
    goal = get_goal_by_id(id)
    return jsonify({"goal": goal.to_dict()}), 200


@goal_bp.route("/<id>", methods=["PUT"])
def update_goal(id):
    """This is a route to update one goal of a specified id
    Required request body:
        - JSON object containing a title (string)
    Returns:
        - If invalid id:
            - 400 status code
        - If valid id but no goal found:
            - 404 status code
        - If goal found:
            - 200 status code
            - JSON object representing updated goal
    """

    goal = get_goal_by_id(id)
    req = request.get_json()
    try:
        goal.title = req["title"]
    except:
        return jsonify({"details": "Invalid data"}), 400

    db.session.commit()
    return jsonify({"goal": goal.to_dict()}), 200


@goal_bp.route("/<id>", methods=["DELETE"])
def delete_goal(id):
    """This is a route to delete a goal of a specified id
    Returns:
        - If invalid id is provided:
            - 400 status code
        - If valid id is provided but no goal is found:
            - 404 status code
        - If goal is found:
            - 200 status code
            - JSON object with a message indicating goal was deleted
    """
    goal = get_goal_by_id(id)
    db.session.delete(goal)
    db.session.commit()
    response_body = {
        "details": f'Goal {goal.id} "{goal.title}" successfully deleted'
    }
    return jsonify(response_body), 200


@goal_bp.route("/<goal_id>/tasks", methods=["POST"])
def set_goal_tasks(goal_id):
    """This is a route to associate tasks with a goal of a specific id
    Required request body:
        - JSON object with a task_ids key containing an array of valid task id integers
    Returns:
        - If invalid goal id or any invalid task ids:
            - 400 status code
        - If valid goal id provided but no goal is found (or valid task id but no task is found):
            - 404 status code
        - If goal and all tasks found:
            - 200 status code
            - JSON obejct representing the id of the goal and the tasks associated with it
    """
    goal = get_goal_by_id(goal_id)
    req = request.get_json()

    try:
        goal.tasks = [get_task_by_id(task_id) for task_id in req["task_ids"]]
    except:
        return jsonify({"details": "Invalid data"}), 400

    db.session.commit()
    return jsonify(goal.to_basic_dict()), 200


@goal_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_by_goal(goal_id):
    """This is a route to get all tasks associated with a goal
    Returns:
        - If invalid goal id:
            - 400 status code
        - If valid goal id but not goal found:
            - 404 status code
        - If goal found:
            - 200 status code
            - JSON object representing the goal and all of its specified tasks
    """
    goal = get_goal_by_id(goal_id)
    return jsonify(goal.to_dict(include_tasks=True)), 200
