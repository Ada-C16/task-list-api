from sqlalchemy.sql.elements import Null
from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify, request, make_response
from sqlalchemy import asc, desc
from datetime import datetime
import os
import requests


tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


# client wants to make a POST request to /tasks
@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        task_sort_order = request.args.get("sort")
        if task_sort_order is None:
            tasks = Task.query.all()
        elif task_sort_order == "asc":
            tasks = Task.query.order_by(asc(Task.title))
        elif task_sort_order == "desc":
            tasks = Task.query.order_by(desc(Task.title))

        tasks_response = []
        for task in tasks:
            task_status = True if task.completed_at else False
            tasks_response.append({
                "id": task.task_id,
                "title": task.title, 
                "description": task.description, 
                "is_complete": task_status
            })
        return jsonify(tasks_response), 200
        
        
    if request.method == "POST":
        request_body = request.get_json()

        if "title" not in request_body or "description" not in request_body \
            or "completed_at" not in request_body:
            return jsonify({ "details" : "Invalid data"}), 400
        
        
        new_task = Task(
            title=request_body["title"], 
            description=request_body["description"], 
            completed_at=request_body["completed_at"])
        
        if "completed_at" in request_body:
            new_task.completed_at = request_body["completed_at"]

        task_status = True if new_task.completed_at else False

        db.session.add(new_task)
        db.session.commit()

        return jsonify({
            "task": {
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": task_status,
            },
        }), 201

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_one_task(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return make_response("Not Found", 404)

    if request.method == "GET":
        task_status = True if task.completed_at else False

        return jsonify({
            "task": {
                "id": task.task_id,
                "title": task.title, 
                "description": task.description, 
                "is_complete": task_status
            },
        }), 200

    if request.method == "PUT":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body:
            return jsonify("Not Found"), 404

        task_status = True if task.completed_at else False

        task.title = request_body["title"]
        task.description = request_body["description"]

        db.session.commit()

        return jsonify({
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": task_status
            },
        }), 200

    if request.method == "DELETE":
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


@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"], strict_slashes=False)
def mark_task_complete(task_id):
    
    if request.method == "PATCH":
        task = Task.query.get(task_id)

        if task is None:
            return "Not Found", 404

        task.completed_at = datetime.now()
        task_status = True

        message = f"Someone just completed the task {task.title}."
        slack_response(message)
    

        return jsonify({
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": task_status
            }
        }), 200


@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark__task_incomplete(task_id):
    task_id = int(task_id)
    task = Task.query.get(task_id)

    if task is None:
        return "Not Found", 404

    task.completed_at = None
    task_status = False 
    

    db.session.commit()

    return jsonify({
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task_status
        },
    }), 200


# NEW GOAL MODEL

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@goals_bp.route("", methods=["GET", "POST"])
def handle_goals():
    if request.method == "GET":
        goals = Goal.query.all()
        goals_response = []
        for goal in goals:
            goals_response.append({
                "id": goal.goal_id,
                "title": goal.title
            })

        return jsonify(goals_response), 200
        
        
    if request.method == "POST":
        request_body = request.get_json()

        if "title" not in request_body:
            return jsonify({ "details" : "Invalid data"}), 400
        
        
        new_goal = Goal(title=request_body["title"])
            
        db.session.add(new_goal)
        db.session.commit()

        return jsonify({
            "goal": {
                "id": new_goal.goal_id,
                "title": new_goal.title,
            },
        }), 201

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_one_goal(goal_id):
    goal = Goal.query.get(goal_id)

    if goal is None:
        return make_response("Not Found", 404)

    if request.method == "GET":
        return jsonify({
        "goal": {
            "id": goal.goal_id,
            "title": goal.title 
        },
    }), 200 

    if request.method == "PUT":
        request_body = request.get_json()
        goal.title = request_body["title"]

        db.session.commit()

        return jsonify({
            "goal": {
                "id": goal.goal_id,
                "title": goal.title
            }
        }), 200

    if request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()

        return jsonify({
            "details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}), 200