import re
from flask.helpers import make_response

from werkzeug.datastructures import HeaderSet
from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, request, jsonify
import requests, os, json
from datetime import datetime

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goals", __name__, url_prefix="/goals")
BOT_TOKEN = os.environ.get('BOT_TOKEN')

@task_bp.route("", methods=["POST", "GET"])
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return jsonify({"details": "Invalid data"}), 400
        new_task = Task(
            title= request_body["title"],
            description= request_body["description"],
            completed_at = request_body["completed_at"]
        )
        db.session.add(new_task)
        db.session.commit()
        if new_task.completed_at:
            new_task.is_complete = True
        
        response = {}
        response["task"] = {
            "id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": new_task.is_complete
        }
        return jsonify(response), 201

    elif request.method == "GET":
        sort_query = request.args.get("sort")
        if sort_query:
            if sort_query == "asc":
                tasks = Task.query.order_by(Task.title).all()
            elif sort_query == "desc":
                tasks = Task.query.order_by(Task.title.desc()).all()
        else: 
            tasks = Task.query.all()
        
        response_body = []
        for task in tasks:
            response_body.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.is_complete
            })
        return jsonify(response_body), 200

@task_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    if request.method == "GET":
        response = {}
        response["task"] = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete
        }
        if task.goal_id:
            response["task"]["goal_id"]=task.goal_id
        return jsonify(response)

    elif request.method == "PUT":
        request_body = request.get_json()
        task.title = request_body["title"]
        task.description = request_body["description"]
        if "completed_at" in request_body:
            task.completed_at = request_body["completed_at"]
            task.is_complete = True
        db.session.commit()

        response_body = {}
        response_body["task"] = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete
        }
        return jsonify(response_body), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        response_body = {
            "details": f"Task {task.id} \"{task.title}\" successfully deleted"
        }
        return jsonify(response_body), 200

@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)
    task.is_complete = True
    db.session.commit()
    task.completed_at = datetime.now()
    
    # posts to slack
    url = 'https://slack.com/api/chat.postMessage'
    slack_request = {
        "token": BOT_TOKEN,
        "channel": "task-notifications",
        "text": f"Someone just completed the task {task.title}"
    }
    requests.post(url, data=slack_request)

    response_body = {}
    response_body["task"] = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.is_complete
    }
    return jsonify(response_body)

@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)
    task.is_complete = False
    db.session.commit()
    task.completed_at = None

    response_body = {}
    response_body["task"] = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.is_complete
    }
    return jsonify(response_body)

@goal_bp.route("", methods=["POST", "GET"])
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body:
            return jsonify({"details": "Invalid data"}), 400
        new_goal = Goal(title= request_body["title"])
        db.session.add(new_goal)
        db.session.commit()
        
        response = {}
        response["goal"] = {
            "id": new_goal.goal_id,
            "title": new_goal.title
        }
        return jsonify(response), 201
    elif request.method == "GET":
        goals = Goal.query.all()

        response_body = []
        for goal in goals:
            response_body.append({
                "id": goal.goal_id,
                "title": goal.title
            })
        return jsonify(response_body)

@goal_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response("", 404)

    if request.method == "GET":
        response_body = {}
        response_body["goal"] = {
            "id": goal.goal_id,
            "title": goal.title
        }
        return jsonify(response_body)

    elif request.method == "PUT":
        request_body = request.get_json()
        goal.title = request_body["title"]
        db.session.commit()

        response_body = {}
        response_body["goal"] = {
            "id": goal.goal_id,
            "title": goal.title
        }
        return jsonify(response_body)

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        response_body = {
            "details": f"Goal {goal.goal_id} \"{goal.title}\" successfully deleted"
        }
        return jsonify(response_body)

@goal_bp.route("/<goal_id>/tasks", methods=["POST", "GET"])
def handle_relationship(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response("", 404)

    if request.method == "POST":
        request_body = request.get_json()
        for task_id in request_body["task_ids"]:
            goal.tasks.append(Task.query.get(task_id))
        db.session.commit()

        response_body = {
            "id": goal.goal_id,
            "task_ids": request_body["task_ids"]
        }
        return jsonify(response_body)
    
    elif request.method == "GET":
        goal_dict = {
            "id": goal.goal_id,
            "title": goal.title,
            "tasks":[]
        }
        for task in goal.tasks:
            goal_dict["tasks"].append({
                "id": task.id,
                "goal_id": task.goal_id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.is_complete
            })
        return jsonify(goal_dict)