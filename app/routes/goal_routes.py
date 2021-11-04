from flask import Blueprint, jsonify, make_response, request, abort
from flask.helpers import make_response
from flask.json import tojson_filter
from flask.signals import request_tearing_down
from werkzeug.utils import header_property
from app.models.goal import Goal
from app import db
from datetime import datetime
from app.routes.utils import valid_int
from app.models.task import Task


goal_bp = Blueprint("goal", __name__,url_prefix ="/goals")

# Helper Functions
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

@goal_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    goal = get_goal_from_id(goal_id)
    request_body = request.get_json()
    goal.title=request_body["title"]
    db.session.commit()
    return make_response({"goal": goal.to_dict()}, 200)

@goal_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = get_goal_from_id(goal_id)
    
    db.session.delete(goal)
    db.session.commit()

    return make_response({"details": f"Goal {goal.goal_id} \"{goal.title}\" successfully deleted"}, 200)

@goal_bp.route("/<goal_id>/tasks", methods=["POST"])
def link_tasks_to_goals(goal_id):
    request_body = request.get_json()
    task_ids = request_body["task_ids"]
    for t_id in task_ids:
        task = Task.query.get(t_id)
        task.goal_id = goal_id
        db.session.commit()
    response_body = {
        "id": int(goal_id),
        "task_ids": task_ids
        }
    return make_response(response_body, 200)

@goal_bp.route("/<goal_id>/tasks", methods=["GET"])
def read_tasks_for_goal(goal_id):
    goal = get_goal_from_id(goal_id)
    return make_response(goal.to_dict_with_tasks(), 200)

    # Task.query.filter(Task.goal_id == goal_id)
    # sort_query = request.args.get("sort")

    # if sort_query == "asc":
    #     goals = Goal.query.order_by(Goal.title.asc())
    # elif sort_query == "desc":
    #     goals = Goal.query.order_by(Goal.title.desc())
    # else:
    #     goals = Goal.query.all()

    # goal_response = []
    # for goal in goals:
    #     goal_response.append(
    #         goal.to_dict()
    #     )
    # return make_response(jsonify(goal_response), 200)

