from flask import Blueprint, json, jsonify, request
from app.models.goal import Goal
from app.models.task import Task
from app import db
from datetime import datetime

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@goals_bp.route("", methods=["POST"])
def create_goal():
    request_body = request.get_json()

    if 'title' not in request_body:
        return {"details": "Invalid data"}, 400

    new_goal = Goal(
        title=request_body['title']
    )

    db.session.add(new_goal)
    db.session.commit()

    return {"goal": new_goal.to_dict()}, 201

@goals_bp.route("/<goal_id>/tasks", methods=["POST"])
def create_tasks_for_goal(goal_id):
    request_body = request.get_json()

    goal = Goal.query.get(goal_id)

    if not goal:
        return "", 404

    for id in request_body['task_ids']:
        goal.tasks.append(Task.query.get(id))

    db.session.commit()

    return {
        "id": goal.goal_id,
        "task_ids": request_body['task_ids']
    }, 200

@goals_bp.route("", methods=["GET"])
def read_goals():
    goals = Goal.query.all()

    goals_response = []

    if not goals:
        return jsonify(goals_response), 200

    for goal in goals:
        goals_response.append(goal.to_dict())
        
    return jsonify(goals_response), 200

@goals_bp.route("/<goal_id>", methods=["GET"])
def read_one_goal(goal_id):
    goal = Goal.query.get(goal_id)

    if not goal:
        return "", 404

    return {"goal": goal.to_dict()}, 200

@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def read_tasks_for_goal(goal_id):
    goal = Goal.query.get(goal_id)

    if not goal:
        return "", 404

    return {
        "id": goal.goal_id,
        "title": goal.title,
        "tasks": goal.task_list()
    }, 200

@goals_bp.route("/<goal_id>", methods=["PUT", "PATCH"])
def update_goal(goal_id):
    goal = Goal.query.get(goal_id)

    if not goal:
        return "", 404

    request_body = request.get_json()

    goal.title = request_body['title']

    db.session.commit()

    return {"goal": goal.to_dict()}, 200

@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = Goal.query.get(goal_id)

    if not goal:
        return "", 404

    db.session.delete(goal)
    db.session.commit()

    return {"details":
            f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}, 200