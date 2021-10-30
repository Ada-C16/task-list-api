from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify, make_response, request
from datetime import datetime, timezone

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@tasks_bp.route("", methods=["GET"])
def get_tasks():
    sort_query = request.args.get("sort")
    if sort_query == "asc":
        tasks = Task.query.order_by(Task.title).all()
    elif sort_query == "desc":
        tasks = Task.query.order_by(Task.title.desc()).all()
    else:
        tasks = Task.query.all()

    tasks_response = [task.to_dict() for task in tasks]
    return jsonify(tasks_response), 200

@goals_bp.route("", methods=["GET"])
def get_goals():
    sort_query = request.args.get("sort")
    if sort_query == "asc":
        goals = Goal.query.order_by(Goal.title).all()
    elif sort_query == "desc":
        goals = Goal.query.order_by(Goal.title.desc()).all()
    else:
        goals = Goal.query.all()

    goals_response = [goal.to_dict() for goal in goals]
    return jsonify(goals_response), 200

@tasks_bp.route("", methods=["POST"])
def post_new_task():
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body\
        or "completed_at" not in request_body:
        return jsonify({
            "details": "Invalid data"
        }), 400

    new_task = Task(title=request_body["title"],
    description=request_body["description"],
    completed_at=request_body["completed_at"])

    
    db.session.add(new_task)
    db.session.commit()

    response_body = {
        "task": (new_task.to_dict())
    }
    return jsonify(response_body), 201

@goals_bp.route("", methods=["POST"])
def post_new_goal():
    request_body = request.get_json()

    if "title" not in request_body:
        return jsonify({
            "details": "Invalid data"
        }), 400

    new_goal = Goal(title=request_body["title"])

    db.session.add(new_goal)
    db.session.commit()

    response_body = {
        "goal": (new_goal.to_dict())
    }
    return jsonify(response_body), 201

@tasks_bp.route("/<task_id>", methods=["GET"])
def get_single_task(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return jsonify(None), 404

    response_body = {
        "task": (task.to_dict())
    }
    return jsonify(response_body), 200


@goals_bp.route("/<goal_id>", methods=["GET"])
def get_single_goal(goal_id):
    goal = Goal.query.get(goal_id)

    if goal is None:
        return jsonify(None), 404

    response_body = {
        "goal": (goal.to_dict())
    }
    return jsonify(response_body), 200


@tasks_bp.route("/<task_id>", methods=["PUT"])
def put_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return jsonify(None), 404

    form_data = request.get_json()
    task.title = form_data["title"]
    task.description = form_data["description"]

    db.session.commit()

    response_body = {
        "task": (task.to_dict())
    }
    return jsonify(response_body), 200


@goals_bp.route("/<goal_id>", methods=["PUT"])
def put_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return jsonify(None), 404

    form_data = request.get_json()
    goal.title = form_data["title"]

    db.session.commit()

    response_body = {
        "goal": (goal.to_dict())
    }
    return jsonify(response_body), 200  


@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return jsonify(None), 404
    
    db.session.delete(task)
    db.session.commit()
    return jsonify({
        'details': f'Task {task.task_id} "{task.title}" successfully deleted'
        }), 200

@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return jsonify(None), 404
    
    db.session.delete(goal)
    db.session.commit()
    return jsonify({
        'details': f'Goal {goal.goal_id} "{goal.title}" successfully deleted'
        }), 200

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_task_as_completed(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return jsonify(None), 404

    task.completed_at = datetime.now(timezone.utc)

    db.session.commit()
    response_body = {
        "task": (task.to_dict())
    }

    task.post_slack_message()

    return jsonify(response_body), 200 

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_task_as_not_completed(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return jsonify(None), 404

    task.completed_at = None
    db.session.commit()

    response_body = {
        "task": (task.to_dict())
    }
    return jsonify(response_body), 200 