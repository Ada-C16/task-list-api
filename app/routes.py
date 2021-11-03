from flask import Blueprint, jsonify, request, abort, make_response
from app import db
from app.models.task import Task
from app.models.goal import Goal
from datetime import date
import requests
import os
from dotenv import load_dotenv

load_dotenv()

tasks_bp = Blueprint("tasks_bp",__name__, url_prefix="/tasks")
goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

# TASKS ROUTES
@tasks_bp.route('', methods=["POST"])
def new_task():
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return {"details": "Invalid data"}, 400

    new_task = Task(
        title = request_body["title"],
        description = request_body["description"],
        completed_at = request_body["completed_at"]
    )

    db.session.add(new_task)
    db.session.commit()

    return {"task": new_task.to_dict()}, 201

# get tasks
@tasks_bp.route('', methods=["GET"])
def get_all_tasks():
    response_tasks = []
    tasks = Task.query.all()

    # sort ascending or descending
    if request.args.get("sort") == "asc":
        tasks = Task.query.order_by(Task.title)
    elif request.args.get("sort") == "desc":
        tasks = Task.query.order_by(Task.title.desc())

    for task in tasks:
        response_tasks.append(task.to_dict())

    return jsonify(response_tasks), 200

@tasks_bp.route('/<task_id>', methods=["GET", "PUT", "DELETE"])
def get_one_task(task_id):
    task = Task.query.get(task_id)
    
    if not task:
            return make_response('', 404)
    elif request.method == "GET":
        return {"task": task.to_dict()}, 200
    elif request.method == "PUT":
        request_body = request.get_json()
        task.title = request_body["title"]
        task.description = request_body["description"]

        #Save Action
        db.session.commit()
        return {"task": task.to_dict()}, 200
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return {"details": f'Task {task_id} "{task.title}" successfully deleted'}, 200

@tasks_bp.route('<task_id>/mark_complete', methods=["PATCH"])
def mark_task_complete(task_id):
    task = Task.query.get(task_id)

    if not task:
        return make_response('', 404)

    task.completed_at = date.today()
    db.session.commit()

    PATH = "https://slack.com/api/chat.postMessage"

    query_params = {"token": os.environ.get('SLACK_API_TOKEN'),
            "channel": "task-notifications",
            "text": f"Someone just completed the task {task.title}" 
            }

    requests.post(PATH, data=query_params)

    return {"task": task.to_dict()} ,200

@tasks_bp.route('<task_id>/mark_incomplete', methods=["PATCH"])
def mark_task_incomplete(task_id):
    task = Task.query.get(task_id)

    if not task:
        return make_response('', 404)

    task.completed_at = None
    db.session.commit()

    return {"task": task.to_dict()} ,200


# GOALS ROUTES
@goals_bp.route('', methods=["POST"])
def new_goal():
    request_body = request.get_json()

    if "title" not in request_body:
        return {"details": "Invalid data"}, 400

    new_goal = Goal(title = request_body["title"])

    db.session.add(new_goal)
    db.session.commit()

    return {"goal": new_goal.to_dict()}, 201

@goals_bp.route('', methods=["GET"])
def get_all_goals():
    response_goals = []
    goals = Goal.query.all()

    for goal in goals:
        response_goals.append(goal.to_dict())

    return jsonify(response_goals), 200

@goals_bp.route('/<goal_id>', methods=["GET", "PUT", "DELETE"])
def get_one_goal(goal_id):
    goal = Goal.query.get(goal_id)
    
    if not goal:
            return make_response('', 404)
    elif request.method == "GET":
        return {"goal": goal.to_dict()}, 200
    elif request.method == "PUT":
        request_body = request.get_json()
        goal.title = request_body["title"]

        #Save Action
        db.session.commit()
        return {"goal": goal.to_dict()}, 200
    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return {"details": f'Goal {goal_id} "{goal.title}" successfully deleted'}, 200

@goals_bp.route("<goal_id>/tasks", methods=["GET", "POST"])
def handle_goals_tasks(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return make_response("", 404)

    if request.method == "POST":
        request_body = request.get_json()

        for id in request_body["task_ids"]:
            task = Task.query.get(id)
            if task not in goal.tasks:
                goal.tasks.append(task)

        db.session.commit()

        return make_response({"id": goal.goal_id,
        "task_ids": [task.task_id for task in goal.tasks]}, 200)

    if request.method == "GET":
        pass

