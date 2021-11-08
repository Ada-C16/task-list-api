from re import T
from flask import Blueprint, json, jsonify, make_response, request, abort
from app import db
from app.models.goal import Goal
from app.models.task import Task
from datetime import datetime

goal_bp = Blueprint("goal", __name__,url_prefix="/goals")

# Helper functions to validate if goal_id is integer
def valid_int(number, parameter_type):
    try:
        return int(number)
    except:
        abort(make_response({"error": f"{parameter_type} must be an int"}, 400))

def get_goal_from_id(goal_id):
    goal_id = valid_int(goal_id, "goal_id")
    return Goal.query.get_or_404(goal_id, description="{goal not found}")

#routes that use GET method
@goal_bp.route("", methods=["GET"])
def get_goals():

    sort_query = request.args.get('sort')
    #sorting sorterer

    if sort_query == 'asc':
            goals = Goal.query.order_by(Goal.title.asc())
    elif sort_query == 'desc':
            goals= Goal.query.order_by(Goal.title.desc())
    else:
        goals = Goal.query.all()
            
    goal_response=[]
    for goal in goals:
        goal_response.append(goal.to_dict())

    return jsonify(goal_response)

@goal_bp.route("/<goal_id>", methods=["GET"])
def get_goal(goal_id):
    goal = get_goal_from_id(goal_id)
    response_body = {"goal":goal.to_dict()}

    return make_response(jsonify(response_body),200)

#routes that use POST method
@goal_bp.route("", methods=["POST"])
def create_goal(): 
    form_data = request.get_json()

    if "title" not in form_data:
        response_body = {"details": "Invalid data"}
        return make_response(jsonify(response_body), 400)

    new_goal = Goal(
        title = form_data["title"],
    )

    db.session.add(new_goal)
    db.session.commit()
    response_body ={"goal":new_goal.to_dict()}
    return make_response(jsonify(response_body), 201)
    
#routes that use PATCH or PUT method
@goal_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    goal = get_goal_from_id(goal_id)
    form_data = request.get_json()

    if "title" in form_data:
        goal.title = form_data["title"]

    db.session.commit()
    response_body = {"goal": goal.to_dict()}

    return make_response(jsonify(response_body), 200)
#routes that use DELETE method

@goal_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = get_goal_from_id(goal_id)

    db.session.delete(goal)
    db.session.commit()

    response_body = {
        "details": f'Goal {goal_id} "{goal.title}" successfully deleted'
    }
    return make_response(jsonify(response_body), 200)

#Nested routes where we are posting a task to our goal

@goal_bp.route("/<goal_id>/tasks", methods=["POST"])
def post_tasks_for_goal(goal_id):
    request_body = request.get_json()
    goal = get_goal_from_id(goal_id)

    for id in request_body["task_ids"]:
        goal.tasks.append(Task.query.get(id))

    db.session.commit()
    response_body={
        "id": goal.goal_id,
        "task_ids": request_body["task_ids"]
    }
    return make_response(jsonify(response_body), 200)

@goal_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_for_goal(goal_id):
    goal = get_goal_from_id(goal_id)

    response_body={
        "id": goal.goal_id,
        "title": goal.title,
        "tasks": goal.task_list()
    }

    
    return make_response(jsonify(response_body), 200)