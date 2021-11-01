from flask import Blueprint, jsonify, request, abort
from sqlalchemy import exc
from app import db
from app.models.task import Task
from datetime import datetime, timezone
from app.routes.route_utils import get_task_by_id, notify_slack_bot, handle_invalid_data

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@task_bp.errorhandler(400)
def invalid_data(error):
    return handle_invalid_data()


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
        new_task = Task.new_from_dict(req)
    except KeyError:
        abort(400)

    db.session.add(new_task)

    # catch error if completed_at is an invalid datetime string
    try:
        db.session.commit()
    except exc.DataError:
        abort(400)

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
    except KeyError:
        abort(400)

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
