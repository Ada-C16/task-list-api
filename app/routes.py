from flask import Blueprint, jsonify, request
from app import db
from app.models.task import Task
from app.models.goal import Goal
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

# Welcome screen
home_bp = Blueprint("home", __name__, url_prefix="/")
fab_4_bp = Blueprint("fab_4", __name__, url_prefix="/fab4")

@home_bp.route("", methods=["GET"], strict_slashes=False)
def home():
    return "Welcome to Michelle's task list", 200

@fab_4_bp.route("", methods=["GET"], strict_slashes=False)
def fab_4():
    return "Fab 4 FOR LYFE", 200

# TASKS

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST", "GET"], strict_slashes=False)
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        if is_post_task_data_valid(request_body):
            new_task = Task(title=request_body["title"], \
            description = request_body["description"], \
            completed_at = request_body["completed_at"])

            db.session.add(new_task)
            db.session.commit()

            return {"task": new_task.to_dict()}, 201
        else:
            return {"details": "Invalid data"}, 400

    elif request.method == "GET":
        sort_direction = request.args.get("sort")
        if sort_direction:
            if sort_direction == "asc":
                tasks = Task.query.order_by(Task.title.asc())
            elif sort_direction == "desc":
                tasks = Task.query.order_by(Task.title.desc())
            else:
                return {"details": "Invalid sort parameter"}, 400
        else:
            tasks = Task.query.all()
        response = []
        for task in tasks:
            response.append(task.to_dict())
        return jsonify(response), 200

@tasks_bp.route('/<id>', methods=["PUT", "GET", "DELETE"], strict_slashes=False)
def handle_task(id):
    if not task_id_exists(id):
        return "", 404
    task = Task.query.get(id)
    if request.method == "GET":
        return {"task": task.to_dict()}, 200

    if request.method == "PUT":
        request_body = request.get_json()
        if is_put_task_data_valid(request_body):
            task.description = request_body['description']
            task.title = request_body['title']
            completed_at = request_body.get("completed_at")
            if completed_at:
                if is_datetime(completed_at):
                    task.completed_at = completed_at
                else:
                    return {"details": "Invalid data"}, 400
            db.session.commit()
            return {"task": task.to_dict()}, 200
        else:
            return {"details": "Invalid data"}, 400
    
    if request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return {"details": f"Task {str(task.task_id)} \"{str(task.title)}\" successfully deleted"}, 200

@tasks_bp.route('/<id>/mark_complete', methods=["PATCH"], strict_slashes=False)
def mark_complete(id):
    if not task_id_exists(id):
        return "", 404
    task = Task.query.get(id)
    task.completed_at = datetime.utcnow()
    db.session.commit()

    # post message to slack
    load_dotenv()
    message = f"Someone just completed the task {task.title}"
    request_params = {'channel': 'task-notifications', 'text': message}
    request_headers = {'Authorization': os.environ.get("API_KEY")}
    url = 'https://slack.com/api/chat.postMessage'
    r = requests.post(url, params=request_params, headers=request_headers)

    return {"task": task.to_dict()}, 200

@tasks_bp.route('/<id>/mark_incomplete', methods=["PATCH"], strict_slashes=False)
def mark_incomplete(id):
    if not task_id_exists(id):
        return "", 404
    task = Task.query.get(id)
    task.completed_at = None
    db.session.commit()

    return {"task": task.to_dict()}, 200

def is_post_task_data_valid(input):
    data_types = {"title":str, "description":str}
    completed_at = input.get("completed_at")
    for name, val_type in data_types.items():
        if type(input.get(name)) != val_type:
            return False
    if ("completed_at" not in input.keys()):
        return False
    else:
        return not completed_at or is_datetime(completed_at)

def is_put_task_data_valid(input):
    data_types = {"title":str, "description":str}
    completed_at = input.get("completed_at")
    for name, val_type in data_types.items():
        if type(input.get(name)) != val_type:
            return False
    return True

def is_datetime(string):
    try:
        x = datetime.strptime(string, '%a, %d %b %Y %H:%M:%S GMT')
    except ValueError:
        return False
    return True

def task_id_exists(id):
    id = int(id)
    if Task.query.get(id):
        return True
    return False

# GOALS

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@goals_bp.route("", methods=["POST", "GET"], strict_slashes=False)
def handle_goals():
    if request.method == "POST":
        request_body = request.get_json()
        if is_goal_data_valid(request_body):
            new_goal = Goal(title=request_body["title"])
            db.session.add(new_goal)
            db.session.commit()
            return {"goal": new_goal.to_dict()}, 201
        else:
            return {"details": "Invalid data"}, 400
    elif request.method == "GET":
        goals = Goal.query.all()
        response = []
        for goal in goals:
            response.append(goal.to_dict())
        return jsonify(response), 200

@goals_bp.route("/<id>", methods=["GET","PUT","DELETE"], strict_slashes=False)
def handle_goal(id):
    if not goal_id_exists(id):
        return "", 404
    goal = Goal.query.get(id)

    if request.method == "GET":
        return {"goal": goal.to_dict()}

    elif request.method == "PUT":
        request_body = request.get_json()
        goal.title = request_body["title"]
        db.session.commit()
        return {"goal": goal.to_dict()}, 200

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return {"details": f"Goal {str(goal.goal_id)} \"{str(goal.title)}\" successfully deleted"}, 200

@goals_bp.route("/<goal_id>/tasks", methods=["POST", "GET"], strict_slashes=False)
def handle_goals_and_tasks(goal_id):
    goal_id = int(goal_id)
    if not goal_id_exists(goal_id):
        return "", 404

    if request.method == "POST":
        request_body = request.get_json()
        task_ids = request_body["task_ids"]
        for task_id in task_ids:
            task = Task.query.get(task_id)
            task.goal_id = goal_id
            db.session.commit()
        all_task_ids = []
        for task in Task.query.filter(Task.goal_id == goal_id):
            all_task_ids.append(task.task_id)
        return {"id": goal_id, "task_ids": all_task_ids}, 200

    elif request.method == "GET":
        tasks = []
        for task in Task.query.filter(Task.goal_id == goal_id):
            tasks.append(task.to_dict())
        goal_dict = Goal.query.get(goal_id).to_dict()
        goal_dict["tasks"] = tasks
        return goal_dict

def goal_id_exists(id):
    id = int(id)
    if Goal.query.get(id):
        return True
    return False

def is_goal_data_valid(input):
    data_types = {"title":str}
    for name, val_type in data_types.items():
        if type(input.get(name)) != val_type:
            return False
    return True

