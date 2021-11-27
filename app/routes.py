from sqlalchemy.sql.expression import null
from app import db
from app.models.goal import Goal
from app.models.task import Task
from datetime import datetime
from flask import abort, Blueprint, jsonify, make_response, request
import os
import requests
from sqlalchemy import desc 

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

# Task routes
# Posts new task
@tasks_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return jsonify({"details": "Invalid data"}), 400
    new_task = Task(title=request_body["title"],
                    description=request_body["description"],
                    completed_at=request_body["completed_at"])
    
    db.session.add(new_task)
    db.session.commit()

    #return jsonify(tasks_response), 200
    new_task_response = {"task": new_task.to_dict()}
    return jsonify(new_task_response), 201

# Handles all tasks
@tasks_bp.route("", methods=["GET"])
def handle_tasks():
    tasks_response = []
    sort_by = request.args.get('sort')
    if sort_by == "asc":
        tasks = Task.query.order_by(Task.title).all()
    elif sort_by == "desc":
        tasks = Task.query.order_by(desc(Task.title)).all()
    else:
        tasks = Task.query.all()
    for task in tasks:
        tasks_response.append(task.to_dict())
    return jsonify(tasks_response), 200

# Handles one task
@tasks_bp.route("/<task_id>", methods=["GET", "PUT"])
def handle_task(task_id):
    task_id = validate_id_int(task_id)
    task = Task.query.get(task_id)
    if not task:
        return make_response("", 404)
    if request.method == "GET":
        return jsonify({"task": task.to_dict()}), 200
    elif request.method == "PUT":
        request_body = request.get_json()
        task.title=request_body["title"]
        task.description=request_body["description"]
        if "completed_at" in request_body:
            task.completed_at=request_body["completed_at"]

        db.session.commit()
        return jsonify({"task": task.to_dict()}), 200

@tasks_bp.route("<task_id>/<patch_complete>", methods=["PATCH"])
def patch_task(task_id, patch_complete):
    task_id = validate_id_int(task_id)
    task = Task.query.get(task_id)
    if not task:
        return make_response("", 404)
    if patch_complete == "mark_complete":
        task.completed_at=datetime.now()
        # ID of the channel you want to send the message to
        channel_id = "C02LA52J4AW"
        SLACK_KEY = os.environ.get("SLACK_API_KEY")
        text=f"Someone just completed the task {task.title}"
        data = {
            'channel': channel_id, 
            'as_user': True,
            'text': text
        }
        requests.post("https://slack.com/api/chat.postMessage", headers={"Authorization": f"Bearer {SLACK_KEY}"}, data=data)
    elif patch_complete == "mark_incomplete":
        task.completed_at=None
    db.session.commit()
    return jsonify({"task": task.to_dict()}), 200

@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    print(task_id)
    task_id=validate_id_int(task_id)
    
    task = Task.query.get(task_id)

    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"details": f'Task {task_id} "{task.title}" successfully deleted'}), 200
    else:
        return make_response("", 404)

def validate_id_int(task_id):
    try:
        task_id = int(task_id)
        return task_id
    except:
        abort(400, "Error: Task ID needs to be a number")

# Goal routes
# Posts new goal
@goals_bp.route("", methods=["POST"])
def create_goal():
    request_body = request.get_json()
    if "title" not in request_body:
        return jsonify({"details": "Invalid data"}), 400
    new_goal = Goal(title=request_body["title"])
    
    db.session.add(new_goal)
    db.session.commit()

    #return jsonify(tasks_response), 200
    new_goal_response = {"goal": new_goal.to_dict()}
    return jsonify(new_goal_response), 201

# Handles all goals
@goals_bp.route("", methods=["GET"])
def handle_goals():
    goals_response = []
    sort_by = request.args.get('sort')
    if sort_by == "asc":
        goals = Goal.query.order_by(Goal.title).all()
    elif sort_by == "desc":
        goals = Goal.query.order_by(desc(Goal.title)).all()
    else:
        goals = Goal.query.all()
    for goal in goals:
        goals_response.append(goal.to_dict())
    return jsonify(goals_response), 200

# Handles one goal
@goals_bp.route("/<goal_id>", methods=["GET", "PUT"])
def handle_goal(goal_id):
    goal_id = validate_id_int(goal_id)
    goal = Goal.query.get(goal_id)
    if not goal:
        return make_response("", 404)
    if request.method == "GET":
        return jsonify({"goal": goal.to_dict()}), 200
    elif request.method == "PUT":
        request_body = request.get_json()
        goal.title=request_body["title"]
        # Remove, not needed? - goal.description=request_body["description"]

        db.session.commit()
        return jsonify({"goal": goal.to_dict()}), 200

@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    print(goal_id)
    goal_id=validate_id_int(goal_id)
    
    goal = Goal.query.get(goal_id)

    if goal:
        db.session.delete(goal)
        db.session.commit()
        return jsonify({"details": f'Goal {goal_id} "{goal.title}" successfully deleted'}), 200
    else:
        return make_response("", 404)

@goals_bp.route("/<goal_id>/tasks", methods=["GET", "POST"])
def handle_goals_tasks(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response("Goal not found", 404)
    
    if request.method == "POST":
        request_body = request.get_json()
        goal.tasks = request_body["task_ids"]
        db.session.add()
        db.session.commit()

        return make_response(goal, 200)
    
    elif request.method == "GET":
        tasks_response = []
        for task in goal.tasks:
            tasks_response.append(task.to_dict())
        return jsonify(tasks_response), 200
