from flask import Blueprint, jsonify, request
from app import db
from app.models.task import Task
from app.models.goal import Goal

goal_bp = Blueprint("goals", __name__, url_prefix="/goals")

@goal_bp.route("", methods=["GET"])
def get_goals():
    goals = Goal.query.all()
    goals_response = []
    for goal in goals:
        goals_response.append(Goal.to_json(goal))
    return jsonify(goals_response), 200

@goal_bp.route("", methods=["POST"])
def post_goals():
    request_body = request.get_json()
    try:
        new_goal = Goal.from_json(request_body)
        db.session.add(new_goal)
        db.session.commit()

        return {"goal": Goal.to_json(new_goal)}, 201
    except KeyError:
        return {"details": "Invalid data"}, 400

@goal_bp.route("/<goal_id>", methods=["GET"])
def get_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return ("", 404)
    return {"goal": Goal.to_json(goal)}, 200

@goal_bp.route("/<goal_id>", methods=["PUT"])
def put_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return ("", 404)
    request_body = request.get_json()
    goal.title = request_body["title"]
    db.session.commit()
    goal = Goal.query.get(goal_id)
    return {"goal": Goal.to_json(goal)}, 200

@goal_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return ("", 404)
    db.session.delete(goal)
    db.session.commit()
    
    return {
        "details": f"Goal {goal.goal_id} \"{goal.title}\" successfully deleted"
    }, 200

@goal_bp.route("/<goal_id>/tasks", methods=["POST"])
def post_goal_tasks(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return ("", 404)
    request_body = request.get_json()
    tasks_to_update = request_body["task_ids"]
    for task in tasks_to_update:
        task = Task.query.get(task)
        task.goal_id = goal_id
    db.session.commit()

    return { 
        "id": eval(goal_id),
        "task_ids": [task.task_id for task in Task.query.filter_by(goal_id=goal_id)]
    }, 200

@goal_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_goal_tasks(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return ("", 404)
    tasks_response = []
    for task in goal.tasks:
        tasks_response.append(Task.to_json_with_goal(task))
    goal_tasks = Goal.to_json(goal)
    goal_tasks["tasks"] = tasks_response
    return goal_tasks, 200