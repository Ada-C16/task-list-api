from flask import Blueprint, make_response, request, jsonify
from app.models.goal import Goal
from app import db

# Blueprint
goal_bp = Blueprint("goal_bp", __name__, url_prefix="/goals")

# Helper functions


# Routes
@goal_bp.route("", methods = ["GET"])
def get_all_goals():
    """Read all goals"""

    sort_query = request.args.get("sort")

    if sort_query == "asc":
        goals = Goal.query.order_by(Goal.title.asc())
    elif sort_query == "desc":
        goals = Goal.query.order_by(Goal.title.desc())
    else:
        goals = Goal.query.all()

    goal_response = []
    for goal in goals:
        goal_response.append(goal.to_dict())
    
    return jsonify(goal_response), 200