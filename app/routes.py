from flask import Blueprint, jsonify, request, json
from flask.signals import request_tearing_down
from app.models.task import Task
from app import db
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

tasks_bp = Blueprint("tasks", __name__, url_prefix = "/tasks")

@tasks_bp.route("", methods = ["POST", "GET"])
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()

        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return {
                "details": "Invalid data"
            }, 400

        new_task = Task(title = request_body["title"],
                        description = request_body["description"],
                        completed_at = request_body["completed_at"])
        db.session.add(new_task)
        db.session.commit()

        return jsonify({
            "task": {
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": False if new_task.completed_at == None else True
            }}), 201

    elif request.method == "GET":
        task_query = request.args.get("title")
        if task_query:
            tasks = Task.query.filter_by(title = task_query)
        else:
            tasks = Task.query.all()

        sort_query = request.args.get("sort")
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc())
        elif sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc())
        else:
            tasks = Task.query.all()
        
        list_of_tasks = []
        for task in tasks:
            list_of_tasks.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                # "is_complete": task.completed_at
                "is_complete": False if task.completed_at == None else True
                # "is_complete": task.completed_at is not None
            })

        return jsonify(list_of_tasks), 200

@tasks_bp.route("/<task_id>", methods = ["GET", "PUT", "DELETE"])
def handle_specific_tasks(task_id):
    task = Task.query.get_or_404(task_id)

    if task is None:
        return jsonify(None), 404

    if request.method == "GET":
        if not task.goal_id:
            return jsonify({
                "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else True
            }
            }), 200
        else:
            return jsonify({
                "task": {
                "id": task.task_id,
                "goal_id": task.goal_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else True
            }
            }), 200
    
    elif request.method == "PUT":
        updated_body = request.get_json()

        task.title = updated_body["title"]
        task.description = updated_body["description"]
        db.session.commit()

        return jsonify({
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else True
            }
        }), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()

        return jsonify({
            "details": f'Task {task.task_id} "{task.title}" successfully deleted'
        }), 200

def slack_bot(title):
    query_path = {'channel':'slack_api_test_channel', 'text': title}
    header = {'Authorization': os.environ.get('slack_bot_token')}
    response = requests.post('https://slack.com/api/chat.postMessage', params = query_path, headers = header)
    return response.json()

@tasks_bp.route("/<task_id>/mark_complete", methods = ["PATCH"])
def handle_mark_complete_tasks(task_id):
    task = Task.query.get_or_404(task_id)
    
    task.completed_at = datetime.utcnow()
    db.session.commit()

    slack_bot(task.title)

    return jsonify({
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else True
            }
        }), 200


@tasks_bp.route("/<task_id>/mark_incomplete", methods = ["PATCH"])
def handle_mark_incomplete_tasks(task_id):
    
    task = Task.query.get_or_404(task_id)
    task.completed_at = None

    db.session.commit()

    return jsonify({
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else True
            }
        }), 200

from app.models.goal import Goal

goals_bp = Blueprint("goals", __name__, url_prefix = "/goals")

@goals_bp.route("", methods = ["POST", "GET"])
def handle_goals():
    if request.method == "POST":
    
        request_body = request.get_json()

        if "title" not in request_body:
            return jsonify({
                "details": "Invalid data"
            }), 400
        else:
            new_goal = Goal(title = request_body["title"])
            db.session.add(new_goal)
            db.session.commit()
            
        return jsonify({
                "goal": {
                    "id": new_goal.goal_id,
                    "title": new_goal.title
                }
            }), 201

    elif request.method == "GET":
        goal_query = request.args.get("title")

        if goal_query:
            goals = Goal.query.filter_by(title = goal_query)
        else:
            goals = Goal.query.all()
        
        list_of_goals = []
        for goal in goals:
            list_of_goals.append({
                "id": goal.goal_id,
                "title": goal.title
            })

        if list_of_goals is None:
            return jsonify([]), 200
        else:
            return jsonify(list_of_goals), 200

@goals_bp.route("/<goal_id>", methods = ["GET", "PUT", "DELETE"])
def handle_specific_goals(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    

    if goal is None:
        return jsonify(None), 404

    if request.method == "GET":
        return {
            "goal": {
            "id": goal.goal_id,
            "title": goal.title
        }}, 200

    elif request.method == "PUT":
        updated_body = request.get_json()

        goal.title = updated_body["title"]
        db.session.commit()

        return jsonify({
            "goal": {
            "id": goal.goal_id,
            "title": goal.title
        }}), 200

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()

        return jsonify({
            "details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'
        }), 200
        

@goals_bp.route("/<goal_id>/tasks", methods = ["POST", "GET"])
def handle_tasks_in_goals(goal_id):
    goal = Goal.query.get(goal_id)

    if goal is None:
        return jsonify(None), 404

    elif request.method == "POST":
        request_body = request.get_json()
        task_ids = request_body["task_ids"]

        for task_id in task_ids:
            task = Task.query.get(task_id)
            task.goal_id = goal.goal_id

        db.session.commit()

        return jsonify({
            "id": goal.goal_id,
            "task_ids": request_body["task_ids"]
        }), 200

    elif request.method == "GET":
        tasks_in_goals = []
        for task in goal.tasks:
            tasks_in_goals.append({
                "id": task.task_id,
                "goal_id": task.goal_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else True
            })
        
        return jsonify({
            "id": goal.goal_id,
            "title": goal.title,
            "tasks": tasks_in_goals
        }), 200
