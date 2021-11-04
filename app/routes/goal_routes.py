from flask import Blueprint, jsonify, request, abort, make_response
from app import db
from app.models.goal import Goal
import requests, os
TOKEN = os.environ.get('TOKEN')

goal_bp = Blueprint("goal", __name__, url_prefix="/goals")


# Helper Functions
def valid_int(number, parameter_type):
    try:
        int(number)
    except:
        abort(jsonify({"error": f"{parameter_type} must be an int"}), 400)


def get_goal_from_id(goal_id):
    valid_int(goal_id, "goal_id")
    return Goal.query.get_or_404(goal_id, description="{goal not found}")


# Routes
@goal_bp.route("", methods=['POST'])
def create_goal():
    """CREATES new goal in database"""
    request_body = request.get_json()

    if "title" not in request_body:
        return make_response({"details": "Invalid data"}, 400)

    new_goal = Goal(
        title=request_body["title"]
    )

    db.session.add(new_goal)
    db.session.commit()

    return jsonify({"goal": new_goal.to_dict()}), 201


@goal_bp.route("/<goal_id>", methods=["GET"])
def get_goal(goal_id):
    """READS goal with given id"""
    goal = get_goal_from_id(goal_id)

    return jsonify({"goal": goal.to_dict()}), 200


@goal_bp.route("", methods=["GET"])
def get_goals():
    """READS all goals"""
    sort_query = request.args.get("sort")

    if sort_query == "asc":
        goals = Goal.query.order_by(Goal.title)
    elif sort_query == "desc":
        goals = Goal.query.order_by(Goal.title.desc())
    else:
        goals = Goal.query.all()

    goals_response = []
    for goal in goals:
        goals_response.append(
            goal.to_dict()
        )
    return jsonify(goals_response), 200


@goal_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    """UPDATES goal with given id"""
    if goal_id == None:
        return make_response(404)

    else:
        goal = get_goal_from_id(goal_id)
        request_body = request.get_json()

        if "title" in request_body:
            goal.title = request_body["title"]
        if "goal" in request_body:
            goal.goal = request_body["goal"]
 
        goal_response = goal.to_dict()

        db.session.commit()
        return jsonify({"goal": goal_response}), 200


@goal_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    """DELETES goal with given id"""
    goal = get_goal_from_id(goal_id)

    db.session.delete(goal)
    db.session.commit()
    return jsonify({"details": f'Goal {goal_id} "{goal.title}" successfully deleted'}), 200


