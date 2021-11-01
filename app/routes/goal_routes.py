from flask import Blueprint, jsonify, request, abort
from app.models.goal import Goal
from app.models.task import Task
from app import db
from app.routes.route_utils import handle_invalid_data

goal_bp = Blueprint("goals", __name__, url_prefix="/goals")


@goal_bp.errorhandler(400)
def invalid_data(error):
    return handle_invalid_data()


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
        new_goal = Goal.new_from_dict(req)
    except KeyError:
        abort(400)

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
    goal = Goal.get_goal_by_id(id)
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

    goal = Goal.get_goal_by_id(id)
    req = request.get_json()
    try:
        goal.update(req)
    except KeyError:
        abort(400)

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
    goal = Goal.get_goal_by_id(id)
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
    goal = Goal.get_goal_by_id(goal_id)
    req = request.get_json()

    try:
        goal.tasks = [Task.get_task_by_id(task_id)
                      for task_id in req["task_ids"]]
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
    goal = Goal.get_goal_by_id(goal_id)
    return jsonify(goal.to_dict(include_tasks=True)), 200
