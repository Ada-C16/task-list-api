from flask import Blueprint, jsonify, make_response, request, abort
from werkzeug.exceptions import RequestEntityTooLarge
from app import db
from app.models.task import Task
from app.models.goal import Goal
import datetime
import requests
from dotenv import load_dotenv
import os

load_dotenv()

task_bp = Blueprint("task", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goals", __name__,url_prefix="/goals")

# HELPER FUNCTION
def valid_int(number, parameter_type):
    try:
        number = int(number)
    except:
        abort(400, {"error":f"{parameter_type} must be an int"})

def get_task_from_id(task_id):
    valid_int(task_id, "task_id")
    return Task.query.get_or_404(task_id, description="{task not found}")

def get_goal_from_id(goal_id):
    valid_int(goal_id, "goal_id")
    return Goal.query.get_or_404(goal_id)

# TASK ROUTES

# Create a task
@task_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return {"details": "Invalid data"}, 400

    new_task = Task(
        title = request_body["title"],
        description = request_body["description"],
        completed_at = request_body["completed_at"],
    )

    db.session.add(new_task)
    db.session.commit()

    response_body = {"task":new_task.to_dict()}

    return jsonify(response_body), 201

# Read all tasks
@task_bp.route("", methods=["GET"])
def read_all_tasks():
    sort_query = request.args.get("sort")

    if sort_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    elif sort_query =="desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()

    tasks_response = []
    for task in tasks:
        tasks_response.append(
            task.to_dict()
        )

    return jsonify(tasks_response)

# Get task by id
@task_bp.route("/<task_id>", methods=["GET"])
def read_one_task(task_id):
    task = get_task_from_id(task_id)
    response_body = {"task":task.to_dict()}
    return jsonify(response_body),200

# Update task with PUT
@task_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = get_task_from_id(task_id)
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body:
        return {"message":"Request requires a title, description and completed_at info"}, 400
    else:
        task.title = request_body["title"]
        task.description = request_body["description"]
       
        db.session.commit()

        response_body = {"task":task.to_dict()}
        return jsonify(response_body), 200

# Delete a task by id
@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = get_task_from_id(task_id)
    db.session.delete(task)
    db.session.commit()
  
    return {'details': f'Task {task.task_id} "{task.title}" successfully deleted'}

# Mark complete on an incomplete task
@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_task_complete(task_id):
    task = get_task_from_id(task_id)
    task.completed_at = datetime.datetime.now()

    db.session.commit()

    # Slack bot
    bot_token = os.environ.get('BOT_API_TOKEN')
    channel_code = os.environ.get('CHANNEL_CODE')
    url= 'https://slack.com/api/chat.postMessage'
    param = {
        "token":bot_token,
        "channel":channel_code,
        "text":"Testing route. Very cool!"
    }
    requests.post(url, data=param)

    response_body = {"task": task.to_dict()}
    return jsonify(response_body), 200

# Mark incomplete on a completed task
@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_task_incomplete(task_id):
    task = get_task_from_id(task_id)
    task.completed_at = None

    db.session.commit()

    response_body = {"task": task.to_dict()}
    return jsonify(response_body), 200

# GOAL ROUTES

# Create a goal
@goal_bp.route("", methods=["POST"])
def create_goal():
    request_body = request.get_json()
    if "title" not in request_body:
        return {"details": "Invalid data"}, 400

    new_goal = Goal(
        title = request_body["title"]
    )

    db.session.add(new_goal)
    db.session.commit()

    response_body = {"goal":new_goal.to_dict_goal()}

    return jsonify(response_body), 201

# Read all goals
@goal_bp.route("", methods=["GET"])
def read_all_goals():
    goals = Goal.query.all()
    goals_response = []
    for goal in goals:
        goals_response.append(
            goal.to_dict_goal()
        )

    return jsonify(goals_response), 200

# Get one goal
@goal_bp.route("/<goal_id>", methods=["GET"])
def read_one_goal(goal_id):
    goal = get_goal_from_id(goal_id)
    response_body = {"goal":goal.to_dict_goal()}
    return jsonify(response_body),200

# Update goal
@goal_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    goal = get_goal_from_id(goal_id)
    request_body = request.get_json()
    if "title" not in request_body:
        return {"message":"Request requires a title"}, 400
    else:
        goal.title = request_body["title"]
       
        db.session.commit()

        response_body = {"goal":goal.to_dict_goal()}
        return jsonify(response_body), 200

# Delete goal by id
@goal_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = get_goal_from_id(goal_id)
    db.session.delete(goal)
    db.session.commit()
  
    return {'details': f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}

# One to many/nested routes

# Sending a list of task ids to a goal
@goal_bp.route("/<goal_id>/tasks", methods=["POST"])
def send_list_of_task_to_goal(goal_id):
    goal = get_goal_from_id(goal_id)
    # goal = Goal.query.get(goal_id)
    request_body = request.get_json()
    
    task_ids_list = request_body["task_ids"]

    for task_id in task_ids_list:
        current_task = Task.query.get(task_id)
        current_task.goal_id = goal.goal_id
    
    db.session.commit()

    response_body = {
        "id":goal.goal_id,
        "task_ids":task_ids_list,
    }

    return jsonify(response_body), 200

    # find goal by id
    # find tasks by own id and it's task_id

# Getting tasks of one goal
@goal_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_of_goal(goal_id):
    goal = get_goal_from_id(goal_id)
    all_tasks = []
    tasks = Task.query.filter(Task.goal_id == goal_id).all()
    for task in tasks:
        all_tasks.append(task.to_dict())

    response_body = {
        "id":goal.goal_id,
        "title":goal.title,
        "tasks":all_tasks
    }

    return jsonify(response_body), 200

