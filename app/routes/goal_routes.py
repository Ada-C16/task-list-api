from app import db
from flask import Blueprint, jsonify, make_response, request, abort 
from app.models.task import Task
from app.models.goal import Goal
import datetime, requests, os
from dotenv import load_dotenv

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

# Helper functions
def confirm_valid_id(id, id_type):
    try:
        int(id)
    except:
        abort(make_response({"error": f"{id_type} must be an int"}, 400))

def get_task_from_id(id):
    confirm_valid_id(id, "task_id")
    return Task.query.get_or_404(id)

def get_goal_from_id(id):
    confirm_valid_id(id, "goal_id")
    return Goal.query.get_or_404(id)


# Goals CRUD routes
@goals_bp.route("", methods=["POST"], strict_slashes=False)
def create_goal():
    request_body = request.get_json()
    if "title" not in request_body:
        return make_response({"details": "Invalid data"}, 400)
    new_goal = Goal(title = request_body["title"])
    db.session.add(new_goal)
    db.session.commit()
    return make_response({"goal": new_goal.to_dict()}, 201)

@goals_bp.route("", methods=["GET"], strict_slashes=False)
def get_all_goals():
    goals = Goal.query.all()
    goals_response = [goal.to_dict() for goal in goals]
    return make_response(jsonify(goals_response), 200)

# single goal routes
@goals_bp.route("/<goal_id>", methods=["GET"], strict_slashes=False)
def get_one_goal(goal_id):
    selected_goal = get_goal_from_id(goal_id)
    return make_response({"goal": selected_goal.to_dict()}, 200)


@goals_bp.route("/<goal_id>", methods=["PUT"], strict_slashes=False)
def update_goal(goal_id):
    request_body = request.get_json()
    selected_goal = get_goal_from_id(goal_id)
    if "title" in request_body:
        selected_goal.title = request_body["title"]
    return make_response({"goal": selected_goal.to_dict()}, 200)


@goals_bp.route("/<goal_id>", methods=["DELETE"], strict_slashes=False)
def delete_goal(goal_id):
    selected_goal = get_goal_from_id(goal_id)
    db.session.delete(selected_goal)
    db.session.commit()
    return make_response(
        {"details": f'Goal {selected_goal.id} "{selected_goal.title}" successfully deleted'}, 200)


# Custom routes: Assign and get tasks related to goal
@goals_bp.route("/<goal_id>/tasks", methods=["POST"], strict_slashes=False)
def assign_tasks_to_goal(goal_id):
    selected_goal = get_goal_from_id(goal_id)
    request_body = request.get_json()
    task_ids = request_body["task_ids"]
    for task_id in task_ids:
        selected_task = get_task_from_id(task_id)
        selected_goal.tasks.append(selected_task)
    db.session.add(selected_goal)
    db.session.commit()
    return make_response({
            "id": selected_goal.id,
            "task_ids": task_ids
        }, 200)

@goals_bp.route("/<goal_id>/tasks", methods=["GET"], strict_slashes=False)
def get_tasks_belonging_to_goal(goal_id):
    selected_goal = get_goal_from_id(goal_id)
    tasks = selected_goal.tasks
    response_tasks = []
    for task in tasks:
        response_tasks.append(task.to_dict())             
    response = {
        "id": selected_goal.id,
        "title": selected_goal.title,
        "tasks": response_tasks
    }
    return make_response(response, 200)