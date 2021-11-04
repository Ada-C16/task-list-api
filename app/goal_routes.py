from flask import Blueprint
from app import db
from app.models.goal import Goal
from flask import Blueprint, jsonify, make_response, request, abort
from app.models.task import Task


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

# Wave 6 routes
@goals_bp.route("/<goal_id>/tasks", methods=["POST"])
def create_one_to_many(goal_id):
    # task = Task.query.get(task_id)
    goal = Goal.query.get(goal_id)
    request_body = request.get_json()
    task_ids = request_body["task_ids"]

    for task_id in task_ids:
        #tasks is a list and now we are appending 
        # querying to give us back an object
        task=Task.query.get(task_id)
        goal.tasks.append(task)
    db.session.commit()
    return jsonify({"id": goal.goal_id, "task_ids": [task.task_id for task in goal.tasks]}), 200

@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_for_goal():
    