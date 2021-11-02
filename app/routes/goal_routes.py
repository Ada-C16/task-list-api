from flask import Blueprint, jsonify, make_response, request, abort
from flask.helpers import make_response
from flask.json import tojson_filter
from flask.signals import request_tearing_down
from werkzeug.utils import header_property
from app.models.goal import Goal
from app import db
from datetime import datetime


goal_bp = Blueprint("goal", __name__,url_prefix ="/goals")

# Helper Functions
def valid_int(number, parameter_type):
    try:
        int(number)
    except:
        abort(make_response({"error": f"{parameter_type} must be an int"}, 400))

def get_goal_from_id(goal_id):
    valid_int(goal_id, "goal_id")
    return Goal.query.get_or_404(goal_id, description="{goal not found}")


# Routes
@goal_bp.route("", methods=["POST"])
def create_goal():
    request_body = request.get_json()
    if "title" not in request_body:
        return make_response({"details": "Invalid data"}, 400)

    new_goal = Goal(
        title=request_body["title"]
    )

    db.session.add(new_goal)
    db.session.commit()

    return make_response({"goal": new_goal.to_dict()}, 201)

@goal_bp.route("", methods=["GET"])
def read_all_goals():

    sort_query = request.args.get("sort")

    if sort_query == "asc":
        goals = Goal.query.order_by(Goal.title.asc())
    elif sort_query == "desc":
        goals = Goal.query.order_by(Goal.title.desc())
    else:
        goals = Goal.query.all()

    goal_response = []
    for goal in goals:
        goal_response.append(
            goal.to_dict()
        )
    return make_response(jsonify(goal_response), 200)

@goal_bp.route("/<goal_id>", methods=["GET"])
def read_one_goal(goal_id):
    goal = get_goal_from_id(goal_id)
    return make_response({"goal": goal.to_dict()}, 200)

# @task_bp.route("/<task_id>", methods=["PUT"])
# def update_task(task_id):
#     task = get_task_from_id(task_id)
#     request_body = request.get_json()
#     task.title=request_body["title"]
#     task.description=request_body["description"]
#     db.session.commit()
#     return make_response({"task": task.to_dict()}, 200)

# @task_bp.route("/<task_id>", methods=["DELETE"])
# def delete_task(task_id):
#     task = get_task_from_id(task_id)
    
#     db.session.delete(task)
#     db.session.commit()

#     return make_response({"details": f"Task {task.task_id} \"{task.title}\" successfully deleted"}, 200)

# @task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
# def mark_task_complete(task_id):
#     task = get_task_from_id(task_id)
#     task.completed_at = datetime.utcnow()
    
#     db.session.commit()
#     message = f"Someone just completed the task {task.title}"
#     post_slack_message(message)

#     return make_response({"task": task.to_dict()}, 200)

# @task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
# def mark_task_incomplete(task_id):
#     task = get_task_from_id(task_id)
#     task.completed_at = None
#     db.session.commit()

#     return make_response({"task": task.to_dict()}, 200)

