from app.routes.route_utils import get_model_and_label
from flask import request, jsonify, abort, Blueprint
from app import db
from sqlalchemy import exc
from datetime import datetime, timezone
from app.models.task import Task
from app.models.goal import Goal

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goals", __name__, url_prefix="/goals")


@goal_bp.errorhandler(400)
@task_bp.errorhandler(400)
def invalid_data(error):
    """This is a function to handle any 400 status code errors"""
    return jsonify({"details": "Invalid data"}), 400


@goal_bp.route("", methods=["GET"])
@task_bp.route("", methods=["GET"])
def read_items():
    """This is a route to get all saved tasks or goals
    Optional query parameter:
        - sort: can be "asc" or "desc" to sort tasks or goals by title
    Returns:
        - JSON array of tasks or goals represented as objects, optionally sorted by title
        - 200 status code
    """
    model = get_model_and_label(request.blueprint, no_label=True)
    sort_query = request.args.get("sort")
    if sort_query == 'asc':
        items = model.query.order_by(model.title).all()
    elif sort_query == 'desc':
        items = model.query.order_by(model.title.desc()).all()
    else:
        items = model.query.all()
    items = [item.to_dict() for item in items]
    return jsonify(items), 200


@goal_bp.route("", methods=["POST"])
@task_bp.route("", methods=["POST"])
def create_item():
    """This is a route to create a new task or goal
    Required request body:
        - For task creation:
            - JSON object with title (string), description (string), and completed_at (datetime or null) keys
        - For goal creation:
            - JSON object with title (string)
    Returns:
        - If valid data provided:
            - JSON object with task or goal data saved to the db
            - 201 status code
        - If invalid data provided:
            - JSON error message
            - 400 status code
    """
    model, label = get_model_and_label(request.blueprint)
    req = request.get_json()

    try:
        new_item = model.new_from_dict(req)
    except KeyError:
        abort(400)

    db.session.add(new_item)

    # catch error if completed_at for tasks is an invalid datetime string
    try:
        db.session.commit()
    except exc.DataError:
        abort(400)

    return jsonify({f"{label}": new_item.to_dict()}), 201


@goal_bp.route("/<id>", methods=["GET"])
@task_bp.route("/<id>", methods=["GET"])
def read_item(id):
    """This is a route to get one task or goal of a specified id
    Returns:
        - If valid id provided but no task or goal found:
            - 404 status code
        - If invalid id provided:
            - 400 status code
        - If valid is is provided and task or goal is found:
            - 200 status code
            - JSON object representing task with requested id
    """
    model, label = get_model_and_label(request.blueprint)
    item = model.get_by_id(id)
    return jsonify({f"{label}": item.to_dict()}), 200


@goal_bp.route("/<id>", methods=["PUT"])
@task_bp.route("/<id>", methods=["PUT"])
def update_item(id):
    """This is a route to update one task or goal of a specified id
    Required request body:
        - For task:
            - JSON object with title (string) and description (string)
        - For goal:
            - JSON object tith title (string)
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
    model, label = get_model_and_label(request.blueprint)
    item = model.get_by_id(id)
    req = request.get_json()

    try:
        item.update(req)
    except KeyError:
        abort(400)

    db.session.commit()
    return jsonify({f"{label}": item.to_dict()}), 200


@goal_bp.route("/<id>", methods=["DELETE"])
@task_bp.route("/<id>", methods=["DELETE"])
def delete_item(id):
    """This is a route to delete a task or goal of a specified id
    Returns:
        - If invalid id is provided:
            - 400 status code
        - If valid id is provided but no task or goal is found:
            - 404 status code
        - If task or goal is found:
            - 200 status code
            - JSON object with a message indicating task or goal was deleted
    """
    model, label = get_model_and_label(request.blueprint)
    item = model.get_by_id(id)
    db.session.delete(item)
    db.session.commit()

    response_body = {
        "details": f'{label.capitalize()} {item.id} "{item.title}" successfully deleted'
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
    task = Task.get_by_id(id)
    task.mark_complete()
    db.session.commit()

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
    task = Task.get_by_id(id)
    task.mark_incomplete()
    db.session.commit()
    return jsonify({"task": task.to_dict()}), 200


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
    goal = Goal.get_by_id(goal_id)
    req = request.get_json()

    try:
        goal.add_tasks(req)
    except KeyError:
        abort(400)

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
    goal = Goal.get_by_id(goal_id)
    return jsonify(goal.to_dict(include_tasks=True)), 200
