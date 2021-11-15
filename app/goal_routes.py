from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify, request

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@goals_bp.route("", methods=["GET"])
def read_goals():
    goals = Goal.query.all()
    goals_response = [goal.to_dict() for goal in goals]

    return jsonify(goals_response), 200


@goals_bp.route("", methods=["POST"])
def add_goal():
    request_body = request.get_json()

    try:
        new_goal = Goal(title=request_body["title"])

        db.session.add(new_goal)
        db.session.commit()

        response = {"goal": new_goal.to_dict()}
        
        return jsonify(response), 201

    except KeyError:
        return jsonify({"details": "Invalid data"}), 400


@goals_bp.route("/<id>", methods=["GET"])
def read_one_goal(id):
    goal = Goal.query.get(id)
    if goal is None:
        return jsonify(None), 404

    return {"goal": goal.to_dict()}


@goals_bp.route("/<id>", methods=["DELETE"])
def delete_one_goal(id):
    goal = Goal.query.get(id)
    if goal is None:
        return jsonify(None), 404

    db.session.delete(goal)
    db.session.commit()

    response = {
        'details': f'Goal {goal.id} "{goal.title}" successfully deleted'
    }
    return jsonify(response), 200


@goals_bp.route("/<id>", methods=["PUT"])
def update_a_goal(id):
    goal = Goal.query.get(id)
    if goal is None:
        return jsonify(None), 404

    request_body = request.get_json()
    goal.title = request_body["title"]

    db.session.commit()

    response = {"goal": goal.to_dict()}
    return jsonify(response), 200


@goals_bp.route("/<id>/tasks", methods=["POST"])
def link_task_to_goal(id):
    request_body = request.get_json()

    task_ids = request_body["task_ids"]
    tasks = [Task.query.get(task_id) for task_id in task_ids]

    goal = Goal.query.get(id)
    goal.tasks = tasks

    db.session.commit()

    response = {
        "id": goal.id,
        "task_ids": task_ids
    }
    return jsonify(response)


@goals_bp.route("/<id>/tasks", methods=["GET"])
def read_tasks_from_goal(id):
    goal = Goal.query.get(id)
    if goal is None:
        return jsonify(None), 404

    tasks_response = [task.to_dict() for task in goal.tasks]

    response = goal.to_dict()
    response["tasks"] = tasks_response

    return jsonify(response)
