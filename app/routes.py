from flask import Blueprint, jsonify, request, abort
from flask.helpers import make_response
from app.models.task import Task
from app.models.goal import Goal
from app import db
from datetime import date
from dotenv import load_dotenv
import requests
import os

load_dotenv()
task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goals", __name__, url_prefix="/goals")

@task_bp.route("", methods=["POST"])
def create_task():
    request_data = request.get_json()

    if "title" not in request_data or "description" not in request_data or "completed_at" not in request_data:
        return jsonify({"details": "Invalid data"}), 400

    new_task = Task(title = request_data["title"], description = request_data["description"], completed_at = request_data["completed_at"])

#Connecting to the db
    db.session.add(new_task)
    db.session.commit()

    return jsonify({"task": new_task.to_dict()}), 201

@task_bp.route("", methods = ["GET"])
def get_tasks():
    task_response = []
    if request.args.get("sort")=="asc":
        tasks=Task.query.order_by(Task.title.asc())
    elif request.args.get("sort")=="desc":
        tasks=Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()
    for task in tasks:
        task_response.append(task.to_dict())
    return jsonify(task_response), 200

@task_bp.route("/<task_id>", methods = ["GET", "PUT"])
def get_task(task_id):
    task_id = int(task_id)
    task = Task.query.get(task_id)
    if not task:
        return make_response("", 404)
    if request.method == "GET":
        return jsonify({"task": task.to_dict()}), 200
    elif request.method == "PUT":
        request_data = request.get_json()
        task.title = request_data["title"]
        task.description = request_data["description"]
        db.session.commit()
        return jsonify({"task": task.to_dict()}), 200

@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        return {"details": f'Task {task_id} "{task.title}" successfully deleted'}, 200

    else: 
        abort(404)

@task_bp.route("/<task_id>/mark_complete", methods =["PATCH"])
def completed_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        abort(404)
    else:
        task.completed_at = date.today()
        db.session.commit()
        PATH = "https://slack.com/api/chat.postMessage"
        params = {
            "token": os.environ.get("IPABOTBOT"),
            "channel": "task_notifications",
            "text": f"Someone  just completed the task {task.title}"
            }
        
        requests.post(PATH, data=params)
        return jsonify({"task": task.to_dict()}), 200

@task_bp.route("/<task_id>/mark_incomplete", methods =["PATCH"])
def incompleted_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        abort(404)
    else:
        task.completed_at = None
        db.session.commit()
        return jsonify({"task": task.to_dict()}), 200

# GOALS
@goal_bp.route("", methods=["POST"])
def create_goal():
    request_data = request.get_json()

    if "title" not in request_data :
        return jsonify({"details": "Invalid data"}), 400

    new_goal = Goal(title = request_data["title"])
#connecting to the db
    db.session.add(new_goal)
    db.session.commit()

    return jsonify({"goal": new_goal.to_dict()}), 201

@goal_bp.route("", methods = ["GET"])
def get_goals():
    goal_response = []
    if request.args.get("sort")=="asc":
        goals=Goal.query.order_by(Goal.title.asc())
    elif request.args.get("sort")=="desc":
        goal_response=Goal.query.order_by(Goal.title.desc())
    else:
        goals = Goal.query.all()
    for goal in goals:
        goal_response.append(goal.to_dict())
    return jsonify(goal_response), 200

@goal_bp.route("/<goal_id>", methods = ["GET", "PUT"])
def get_goal(goal_id):
    goal_id = int(goal_id)
    goal = Goal.query.get(goal_id)
    if not goal:
        return make_response("", 404)
    if request.method == "GET":
        return jsonify({"goal": goal.to_dict()}), 200
    elif request.method == "PUT":
        request_data = request.get_json()
        goal.title = request_data["title"]
        db.session.commit()
        return jsonify({"goal": goal.to_dict()}), 200

@goal_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal:
        db.session.delete(goal)
        db.session.commit()
        return {"details": f'Goal {goal_id} "{goal.title}" successfully deleted'}, 200

    else: 
        abort(404)

#Appending a task column to the goal table
@goal_bp.route("/<goal_id>/tasks", methods = ["POST"])
def task_ids_to_goal(goal_id):
    #Returning an instance of Goal
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response(""), 404
    
    request_data = request.get_json()
    task_ids = []
    for task_id in request_data["task_ids"]:
        task = Task.query.get(task_id)
        goal.tasks.append(task)
        task_ids.append(task_id)
    db.session.commit()
    return jsonify({"id": goal.goal_id, "task_ids": task_ids}), 200

@goal_bp.route("/<goal_id>/tasks", methods = ["GET"])
def get_tasks_for_specific_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response(""), 404
    return jsonify(goal.to_dict_and_tasks()), 200
    
    