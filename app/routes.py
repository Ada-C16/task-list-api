from app import db
from flask import Blueprint, jsonify, make_response, request, abort
from app.models.task import Task
from app.models.goal import Goal
import datetime


tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
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

# Tasks routes

@tasks_bp.route("", methods=["GET"], strict_slashes=False)
def get_all_tasks():

    sort_query = request.args.get("sort")
    if sort_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    elif sort_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()
    tasks_response = [task.to_dict() for task in tasks]
    return make_response(jsonify(tasks_response), 200)
# should I respond with error code if table is empty?

@tasks_bp.route("", methods=["POST"], strict_slashes=False)
def create_new_task():
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body or \
        "completed_at" not in request_body:
        return make_response({"details": "Invalid data"}, 400)
    new_task = Task(
        title = request_body["title"],
        description = request_body["description"],
        completed_at = request_body["completed_at"]
    )
    db.session.add(new_task)
    db.session.commit()
    return make_response({"task": new_task.to_dict()}, 201)


@tasks_bp.route("/<task_id>", methods=["GET"], strict_slashes=False)
def get_one_task(task_id):
    selected_task = get_task_from_id(task_id)
    return make_response({"task": selected_task.to_dict()}, 200)

@tasks_bp.route("/<task_id>", methods=["PUT"], strict_slashes=False)
def update_task(task_id):
    request_body = request.get_json()
    selected_task = get_task_from_id(task_id)
    if "title" in request_body:
        selected_task.title = request_body["title"]
    if "description" in request_body:
        selected_task.description = request_body["description"]
    return make_response({"task": selected_task.to_dict()}, 200)


@tasks_bp.route("/<task_id>", methods=["DELETE"], strict_slashes=False)
def delete_task(task_id):
    selected_task = get_task_from_id(task_id)
    db.session.delete(selected_task)
    db.session.commit()
    return make_response(
        {"details": f'Task {selected_task.id} "{selected_task.title}" successfully deleted'}, 200)

# Custom Routes: marking tasks complete or incomplete

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"], strict_slashes=False)
def mark_incompleted_task_complete(task_id):
    selected_task = get_task_from_id(task_id)
    selected_task.completed_at = datetime.datetime.now()
    db.session.commit()
    return make_response({"task": selected_task.to_dict()}, 200)

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"], strict_slashes=False)
def mark_completed_task_incomplete(task_id):
    selected_task = get_task_from_id(task_id)
    selected_task.completed_at = None
    db.session.commit()
    return make_response({"task": selected_task.to_dict()}, 200)


# Goals routes
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
