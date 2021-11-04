from flask import Blueprint
from app import db
from app.models.goal import Goal
from flask import Blueprint, jsonify, make_response, request, abort
from datetime import datetime

goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

# Helper Functions
def valid_int(number, parameter_type):
    try:
        int(number)
    except:
        abort(make_response({"error": f"{parameter_type} must be an int"})), 400

def get_goal_from_id(goal_id):
    valid_int(goal_id, "goal_id")
    return Goal.query.get_or_404(goal_id, description="{goal not found}")

#routes
@goals_bp.route("", methods=["POST"])
def create_goals():
    request_body = request.get_json()
    if "title" not in request_body:
        return make_response({"details": "Invalid data"}), 400

    new_goal = Goal(
        title=request_body["title"]
    )
    
    db.session.add(new_goal)
    db.session.commit()
    return jsonify({"goal": new_goal.to_dict()}), 201

@goals_bp.route("", methods=["GET"])
def read_goals():
    goals = Goal.query.all()
    goals_response = []
    for goal in goals:
        goal = goal.to_dict()
        goals_response.append(goal)
    return jsonify(goals_response), 200

@goals_bp.route("/<goal_id>", methods=["GET"])
def read_goal(goal_id):
    goal = get_goal_from_id(goal_id)
    return {"goal": goal.to_dict()}

@goals_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    goal= get_goal_from_id(goal_id)
    request_body=request.get_json()

    if "title" in request_body:
        goal.title=request_body["title"]

    db.session.commit()
    return make_response({"goal":goal.to_dict()}), 200

@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = get_goal_from_id(goal_id)
    db.session.delete(goal)
    db.session.commit()
    return make_response({"details":f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}), 200

