from flask import Blueprint, make_response, request, jsonify
from app.models.task import Goal
from app import db

# Blueprint
goal_bp = Blueprint("goal_bp", __name__, url_prefix="/goals")

# Helper functions


# Routes
@goal_bp("", method = ["GET"])
def get_all_goals():
    """Read all goals"""

    sort_query = request.args.get("sort")

    if sort_query == "asc":
        tasks = Goal.query.order_by(Goal.title.asc())
    elif sort_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()

    task_response = []
    for task in tasks:
        task_response.append(task.to_dict())
    
    return jsonify(task_response), 200