from flask import Blueprint, request, make_response, jsonify, abort
from flask.wrappers import Response
from app.models.goal import Goal
from app.models.task import Task
from app import db
from datetime import date, datetime

goals_bp = Blueprint('goals', __name__, url_prefix='/goals')

# # Helper functions
def valid_int(id):
    try:
        number = int(id)
        return number
    except:
        response_body = 'Invalid Data'
        abort(make_response(response_body,400))

def get_goal_from_id(goal_id):
    id = valid_int(goal_id)
    selected_goal = Goal.query.filter_by(goal_id=goal_id).one_or_none()
    # Goal not found
    if selected_goal is None:
        abort(make_response("Not Found", 404))
    return selected_goal

def valid_goal(request_body):
    if "title" not in request_body:
        abort(make_response({"details": "Invalid data"}, 400))
# #

# Create a goal
@goals_bp.route("", methods=["POST"], strict_slashes=False)
def create_goal():
    request_body = request.get_json()
    valid_goal(request_body)
    new_goal = Goal(title=request_body["title"])
    db.session.add(new_goal)
    db.session.commit()
    response = {"goal": new_goal.to_dict()}
    return make_response(response, 201)

# Get all goals
@goals_bp.route("", methods=["GET"], strict_slashes=False)
def get_all_goals():
    response_list = []
    goal_objects = Goal.query.all()
    for goal in goal_objects:
        response_list.append(goal.to_dict())
    return make_response(jsonify(response_list), 200)

# Get one goal
@goals_bp.route("/<goal_id>", methods=["GET"], strict_slashes=False)
def get_goal(goal_id):
    selected_goal = get_goal_from_id(goal_id)
    response_body = {"goal": selected_goal.to_dict()}
    return make_response(response_body, 200)

# Update goal
@goals_bp.route("/<goal_id>", methods=["PUT"], strict_slashes=False)
def update_goal(goal_id):
    selected_goal = get_goal_from_id(goal_id)
    request_body = request.get_json()
    if "title" in request_body:
        selected_goal.title = request_body["title"]
    db.session.commit()
    response_body = {"goal": selected_goal.to_dict()}
    return make_response(response_body, 200)

# Delete goal
@goals_bp.route("/<goal_id>", methods=["DELETE"], strict_slashes=False)
def delete_goal(goal_id):
    selected_goal = get_goal_from_id(goal_id)
    db.session.delete(selected_goal)
    db.session.commit()
    response_body = {'details': f'Goal {goal_id} "{selected_goal.title}" successfully deleted'}
    return make_response(response_body, 200)

# Post list of task_ids to a goal
@goals_bp.route("/<goal_id>/tasks", methods=["POST"], strict_slashes=False)
def post_tasks_to_goal(goal_id):
    selected_goal = get_goal_from_id(goal_id)
    selected_goal = Goal.query.get(goal_id)
    request_body = request.get_json()
    task_ids_list = request_body["task_ids"]

    for task_id in task_ids_list:
        task = Task.query.get(task_id)
        selected_goal.tasks.append(task)
    
    db.session.commit()
    response_body = selected_goal.add_tasks_to_goal_dict()
    return make_response(response_body, 200)

# Get tasks from goal
@goals_bp.route("/<goal_id>/tasks", methods=["GET"], strict_slashes=False)
def get_tasks_from_goal(goal_id):
    selected_goal = get_goal_from_id(goal_id)
    selected_goal = Goal.query.get(goal_id)

    

    response_body = selected_goal.get_tasks_from_goal_dict()

    return make_response(response_body, 200)
