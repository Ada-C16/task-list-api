from flask import Blueprint, json, jsonify, request, make_response, abort 
from app.models.goal import Goal 
from app import db 
from datetime import date 
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
    goal_id = valid_int(goal_id, "int")
    return Goal.query.get_or_404(goal_id, description="{Goal not found}")

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
    goal = Goal.query.get(goal_id)

    if goal is None:
        return jsonify(None), 404
    
    if request.method == "GET":
        return {"goal":
        {"id": goal.goal_id,
        "title": goal.title}}, 200 

@goal_bp.route("", methods=["GET"])
def get_goals():
    """READS ALL goals"""
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
        goal = Goal.query.get(goal_id)
        request_body = request.get_json()

        if "title" in request_body:
            goal.title = request_body["title"]
        if "goal" in request_body:
            goal.goal = request_body["goal"]

        db.session.commit()

        return {"goal":
        {"id": goal.goal_id,
        "title": goal.title}}, 200 


@goal_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    """DELETES goal with given id"""
    goal = Goal.query.get(goal_id)
    if goal is None: 
        return jsonify(goal), 404 

        # db.session.delete(goal)
        # db.session.commit()
    else: 
        db.session.delete(goal)
        db.session.commit()

    return jsonify({"details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}), 200


    # db.session.delete(goal)
    # db.session.commit()
    # return jsonify({"details": f'Goal {goal_id} "{goal.title}" successfully deleted'}), 200
