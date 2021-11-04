from flask import Blueprint,jsonify, request
from app import db
from app.models.task import Task
from app.models.goal import Goal
from sqlalchemy import asc, desc
from dotenv import load_dotenv
from datetime import datetime
import os
import requests


tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

# helper functions
def task_dict(task):
    return {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.completed_at is not None
    }

def task_goals_dict(task):
    return {
        "id": task.task_id,
        "goal_id": task.goal_id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.completed_at is not None
    }

def goal_dict(goal):
    return {
        "id": goal.goal_id,
        "title": goal.title
    }

def goal_with_tasks(goal):
    tasks = []
    for task in goal.tasks:
        tasks.append(task_goals_dict(task))
    return {
        "id": goal.goal_id,
        "title": goal.title,
        "tasks": tasks
    }
# end of helper functions


# using tasks endpoint
@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        task_sort_order = request.args.get("sort")
        if task_sort_order == "asc":
            tasks = Task.query.order_by(asc(Task.title))
        elif task_sort_order == "desc":
            tasks = Task.query.order_by(desc(Task.title))
        else:
            tasks = Task.query.all()

        tasks_response = []
        for task in tasks:
            tasks_response.append(task_dict(task))
        return jsonify(tasks_response), 200
        
        
    elif request.method == "POST":
        request_body = request.get_json()

        if "title" not in request_body or "description" not in request_body \
            or "completed_at" not in request_body:
            return jsonify({ "details" : "Invalid data"}), 400
        
        
        new_task = Task(
            title=request_body["title"], 
            description=request_body["description"], 
            completed_at=request_body["completed_at"])

        db.session.add(new_task)
        db.session.commit()

        response_body = {"task":task_dict(new_task)}
        return jsonify(response_body), 201


@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_one_task(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return jsonify(None), 404

    elif request.method == "GET":
        if task.goal_id:
            response_body = {"task": task_goals_dict(task)}
            return jsonify(response_body), 200


    elif request.method == "PUT":
        request_body = request.get_json()

        task.title = request_body["title"]
        task.description = request_body["description"]

        db.session.commit()
        response_body = {"task": task_dict(task)}
        return jsonify(response_body), 200


    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()

        return jsonify({
            "details": f'Task {task.task_id} "{task.title}" successfully deleted'
            }), 200

def slack_response(message):
    slack_api_token = os.environ.get("SLACK_API_TOKEN")
    path = "https://slack.com/api/chat.postMessage"
    query_params={
        "channel": "slack-api-test-channel",
        "text": message
    }
    headers = {"Authorization": f"Bearer {slack_api_token}"}
    requests.post(path, params=query_params,  headers=headers)


@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_task_complete(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return jsonify(None), 404

    task.completed_at = datetime.now()
    db.session.commit()

    message = f"Someone just completed the task {task.title}."
    slack_response(message)

    response_body = {"task": task_dict(task)}
    return jsonify(response_body), 200


@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark__task_incomplete(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return jsonify(None), 404

    task.completed_at = None
    db.session.commit()

    response_body = {"task": task_dict(task)}
    return jsonify(response_body), 200
    

# using goals endpoint
@goals_bp.route("", methods=["GET", "POST"])
def handle_goals():
    if request.method == "GET":
        goals = Goal.query.all()
        goals_response = []
        for goal in goals:
            goals_response.append(goal_dict(goal))
        return jsonify(goals_response), 200
        
        
    elif request.method == "POST":
        request_body = request.get_json()

        if "title" not in request_body:
            return jsonify({ "details" : "Invalid data"}), 400
        
        
        new_goal = Goal(title=request_body["title"])
            
    db.session.add(new_goal)
    db.session.commit()

    response_body = {"goal": goal_dict(new_goal)}
    return jsonify(response_body), 201
    

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_one_goal(goal_id):
    goal = Goal.query.get(goal_id)

    if goal == None:
        return jsonify(None), 404

    elif request.method == "GET":
        response_body = {"goal" : goal_dict(goal)}
        return jsonify(response_body), 200
        

    elif request.method == "PUT":
        request_body = request.get_json()
        goal.title = request_body["title"]

        db.session.commit()
        response_body = {"goal": goal_dict(goal)}
        return jsonify(response_body), 200

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()

        return jsonify({"details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}), 200

@goals_bp.route("/<goal_id>/tasks", methods=["GET", "POST"])
def handle_goals_tasks(goal_id):
    goal = Goal.query.get(goal_id)
    if goal == None:
        return jsonify(None), 404

    elif request.method == "GET":
        return jsonify(goal_with_tasks(goal)), 200

    elif request.method == "POST":
        request_body = request.get_json()
        task_ids = request_body["task_ids"]
        for task_id in task_ids:
            task = Task.query.get(task_id)
            task.goal_id = goal_id
        db.session.commit()
        new_tasks = []
        for task in goal.tasks:
            new_tasks.append(task.task_id)
        response_body = {
            "id": int(goal.goal_id),
            "task_ids": new_tasks,
        }

        return jsonify(response_body), 200