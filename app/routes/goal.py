from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.task import Task
from app.models.goal import Goal

goals_bp = Blueprint("goal", __name__, url_prefix="/goals")

@goals_bp.route("", methods=["GET"])
def goals():
    goals = Goal.query.all()
    goals_response = [goal.to_json() for goal in goals]     
    return jsonify(goals_response), 200


@goals_bp.route("", methods=["POST"])
def add_goal():
    request_body = request.get_json()
    if "title" not in request_body:
        return { "details" : "Invalid data" }, 400

    new_goal = Goal(title=request_body["title"])
    db.session.add(new_goal)
    db.session.commit()
    return jsonify({ "goal" : new_goal.to_json() }), 201


@goals_bp.route("/<goal_id>", methods=["GET"])
def goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response("", 404)
    
    return jsonify({ "goal" : goal.to_json() }), 200


@goals_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response("", 404)
    
    request_data = request.get_json()
    goal.title = request_data["title"]
    db.session.commit()

    return jsonify({ "goal" : goal.to_json(request_data["title"]) }), 200


@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response("", 404)
    
    db.session.delete(goal)
    db.session.commit()

    id, title = goal.goal_id, goal.title
    return { "details" : f"Goal {id} \"{title}\" successfully deleted" }, 200


@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def goal_tasks(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response("", 404)

    tasks = Task.query.filter_by(goal_id=goal.goal_id)
    tasks_response = [task.to_json() for task in tasks]
    return jsonify({
        "id": goal.goal_id,
        "title": goal.title,
        "tasks": tasks_response
        }), 200  


@goals_bp.route("/<goal_id>/tasks", methods=["POST"])
def add_goal_tasks(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response("", 404)

    request_body = request.get_json() # i.e. "task_ids": [1, 2, 3]
    for task_id in request_body["task_ids"]:
        task = Task.query.get(task_id)
        task.goal_id = goal.goal_id
    return jsonify({
        "id": goal.goal_id,
        "task_ids": request_body["task_ids"]
        }), 200