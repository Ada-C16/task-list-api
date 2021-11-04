from flask import Blueprint, jsonify, request, abort, make_response
from app.models.task import Task
from app.models.goal import Goal
from app import db
from datetime import date
import requests, os
from dotenv import load_dotenv

task_bp = Blueprint("task", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goal", __name__, url_prefix="/goals")
load_dotenv()

# Make a Task, Get all Tasks
@task_bp.route("", methods = ["POST", "GET"])
def create_tasks():
    if request.method == "POST":
    # Get data from the request
        request_body = request.get_json()

        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return jsonify({"details": "Invalid data"}), 400
    
        new_task = Task(
        title = request_body["title"], 
        description = request_body["description"], 
        completed_at = request_body["completed_at"]) 

        db.session.add(new_task)
        db.session.commit()

        return jsonify({"task": new_task.to_dict()}), 201

    elif request.method == "GET":
        tasks = Task.query.all()
        task_response = []
        if request.args.get("sort") == "asc":
            tasks = Task.query.order_by(Task.title)
        elif request.args.get("sort") == "desc":
            tasks = Task.query.order_by(Task.title.desc())
        
        for task in tasks:
            task_response.append(task.to_dict())
    return jsonify(task_response), 200

# Get one Task, update one Task, delete one Task
@task_bp.route("/<task_id>", methods = ["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task_id = int(task_id)
    task = Task.query.get(task_id)
    if not task:
        abort(404)
        # return make_response("", 404)
    
    if request.method == "GET":
        return jsonify({"task": task.to_dict()}), 200

    elif request.method == "PUT":
        input_data = request.get_json()
        task.title = input_data["title"]
        task.description = input_data["description"]
        db.session.commit()
        return ({"task": task.to_dict()}), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return jsonify({"details": f'Task {task.task_id} "{task.title}" successfully deleted'}), 200

@task_bp.route("/<task_id>/mark_complete", methods = ["PATCH"])
def completed_task(task_id):
    task = Task.query.get(task_id)
    today = date.today()
    if not task:
        abort(404)
    else:
        task.completed_at = today
        db.session.commit()

        PATH = "https://slack.com/api/chat.postMessage"
        params = {
            "token": os.environ.get("IGOR"),
            "channel": "task-notifications",
            "text": f"Someone just completed the task {task.title}"
            }

        requests.post(PATH, data=params)

        return jsonify({"task": task.to_dict()}), 200

@task_bp.route("/<task_id>/mark_incomplete", methods = ["PATCH"])
def incompleted_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        abort(404)
    else:
        task.completed_at = None
        db.session.commit()
        return jsonify({"task": task.to_dict()}), 200

# Make a Goal, get all Goals
@goal_bp.route("", methods = ["POST", "GET"])
def create_goals():
    if request.method == "POST":
    # Get data from the request
        request_body = request.get_json()

        if "title" not in request_body:
            return jsonify({"details": "Invalid data"}), 400
    
        new_goal = Goal(
        title = request_body["title"] )

        db.session.add(new_goal)
        db.session.commit()

        return jsonify({"goal": new_goal.to_dict()}), 201

    elif request.method == "GET":
        goals = Goal.query.all()
        goal_response = []
        for goal in goals:
            goal_response.append(goal.to_dict())
    return jsonify(goal_response), 200

# Get one Goal, update one Goal, delete one Goal
@goal_bp.route("/<goal_id>", methods = ["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal_id = int(goal_id)
    goal = Goal.query.get(goal_id)
    if not goal:
        abort(404)
        # return make_response("", 404)
    
    if request.method == "GET":
        return jsonify({"goal": goal.to_dict()}), 200

    elif request.method == "PUT":
        input_data = request.get_json()
        goal.title = input_data["title"]
        db.session.commit()
        return ({"goal": goal.to_dict()}), 200

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return jsonify({"details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}), 200

# Nested Routes - Associate Goal with Tasks
@goal_bp.route("/<goal_id>/tasks", methods=["GET", "POST"])
def handle_goals_tasks(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        abort(404)
    if request.method == "GET":
        result = {
            "id": goal.goal_id,
            "title": goal.title,
            "tasks": [task.to_dict() for task in goal.tasks]
        }
        return jsonify(result), 200

    elif request.method == "POST":
        request_body = request.get_json()
        task_ids = request_body["task_ids"]
        for task_id in task_ids:
            task = Task.query.get(task_id)
            goal.tasks.append(task)
        
        db.session.commit()
        return jsonify({"id": goal.goal_id, "task_ids": [task.task_id for task in goal.tasks]}), 200