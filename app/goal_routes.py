from app import db 
from app.models.goal import Goal
from app.models.task import Task
from flask import Blueprint, json, jsonify, make_response, request, abort
import os


goal_bp = Blueprint("goal",__name__, url_prefix="/goals")

#HELPER FUNCTIONS
def check_for_valid_int(number, parameter_type):
    try:
        int(number)
    except:
        abort(make_response({"error": f"{parameter_type} must be an int"}, 400))


def get_goal_from_id(goal_id):
    check_for_valid_int(goal_id, "goal_id")
    return Goal.query.get_or_404(goal_id, description="{goal not found}")


#ROUTES
@goal_bp.route("", methods=["GET"])
def read_all_goals():

    goals = Goal.query.all()

    goal_response = []
    for goal in goals:
        goal_response.append(
            goal.to_dict()
        )

    return jsonify(goal_response)


# CREATE ONE GOAL
@goal_bp.route("", methods=["POST"])
def create_goals():
    request_body = request.get_json()
    if "title" not in request_body:
        return {"details": "Invalid data"}, 400

    new_goal = Goal(
        title=request_body["title"]
    )

    db.session.add(new_goal)
    db.session.commit()

    return make_response({"goal":new_goal.to_dict()}, 201)


#GET ONE GOAL WITH ID 
@goal_bp.route("/<goal_id>", methods=["GET"])
def read_goal(goal_id):
    goal = get_goal_from_id(goal_id)
    return {"goal": goal.to_dict()}


#UPDATE A GOAL
@goal_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    goal = get_goal_from_id(goal_id)
    request_body = request.get_json()

    if "title" in request_body:
        goal.title = request_body["title"]
   
    db.session.commit()
    return make_response({"goal": goal.to_dict()},200)



#DELETE A GOAL
@goal_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = get_goal_from_id(goal_id)

    db.session.delete(goal)
    db.session.commit()
    return ({"details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'})



#GATHERING ALL TASKS ASSOCIATED WITH ONE GOAL
@goal_bp.route("/<goal_id>/tasks", methods=["POST"])
def post_task_ids_to_goal(goal_id):
    goal = Goal.query.get(goal_id)
    request_body = request.get_json()

    if goal is None:
        return make_response("Goal not found", 404)

    if 'task_ids' not in request_body:
        return make_response('Tasks were not given data', 400)

    goal_tasks = request_body["task_ids"]
    for task_id in goal_tasks:
        task = Task.query.get(task_id)
        
        if task not in goal.tasks:
            goal.tasks.append(task)

    db.session.commit()

    response_body = {
        'id': int(goal_id),
        'task_ids': goal_tasks
     }
    return make_response(jsonify(response_body), 200)
        

@goal_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_for_specific_goal(goal_id):  
    goal = Goal.query.get(goal_id)

    if goal is None:
        return make_response("Goal not found", 404)
    return goal.to_dict_with_tasks(),200