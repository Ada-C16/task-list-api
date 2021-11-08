import re
from flask import Blueprint, jsonify, request
from flask.helpers import make_response
from app.models.task import Task
from app.models.goal import Goal
import requests
from datetime import datetime 
from app import db
import os
from dotenv import load_dotenv

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()
    
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return jsonify({"details": "Invalid data"}), 400
    
    new_task = Task(
        title=request_body["title"], 
        description=request_body["description"], 
        completed_at=request_body["completed_at"]
        )
    
    db.session.add(new_task) 
    db.session.commit()
    
    response_body = {
        "task": {
            "id": new_task.task_id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": new_task.completed_at is not None
            }
        }
    
    return jsonify(response_body), 201

@tasks_bp.route("", methods=["GET"])
def read_tasks():
    title_query = request.args.get("sort")

    if title_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    elif title_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all() 
    
    task_responses = []
    for task in tasks:
        task_responses.append(
                {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.completed_at is not None
                }
            )
    
    return jsonify(task_responses), 200

@tasks_bp.route("/<task_id>", methods=["GET"])
def read_task(task_id):
    task_id = int(task_id)
    task = Task.query.get(task_id)
    
    if task == None:
        return jsonify(None), 404

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

@tasks_bp.route("/<task_id>",methods=["PUT"])
def update_task(task_id):
    task_id = int(task_id)
    task = Task.query.get(task_id)

    updated_body = request.get_json()

    if task == None:
        return jsonify(None), 404

    else: 
        task.title = updated_body["title"]
        task.description = updated_body["description"]
        
        db.session.commit()
        
        task_dict = {}
        task_dict = {
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.completed_at is not None
            }
        }
        
        return jsonify(task_dict), 200

@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task_id = int(task_id)
    task = Task.query.get(task_id)
    
    if task == None:
        return jsonify(None), 404

    else: 
        db.session.delete(task)
        db.session.commit()
    
    response_body = {}
    response_body = {
        "details": f'Task {task.task_id} "{task.title}" successfully deleted'}
    return jsonify(response_body), 200

def slack_bot(title):
    query_path = {'channel':'slack_api_test_channel', 'text': title}
    header = {'Authorization': os.environ.get('BOT')}
    response = requests.post('https://slack.com/api/chat.postMessage', params = query_path, headers = header)
    return response.json()

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def update_complete(task_id):
    task_id = int(task_id)
    task = Task.query.get(task_id)

    if task == None:
        return jsonify(None), 404

    task.completed_at = datetime.now()
    db.session.commit()

    slack_bot(task.title)

    task_dict = {}
    task_dict = {
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.completed_at is not None
            }
        }
    
    return jsonify(task_dict), 200

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def update_incomplete(task_id):
    task_id = int(task_id)
    task = Task.query.get(task_id)

    if task == None:
        return jsonify(None), 404
    
    task.completed_at = None

    db.session.commit()

    task_dict = {}
    task_dict = {
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.completed_at is not None
            }
        }
    
    return jsonify(task_dict), 200

goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

@goals_bp.route("", methods=["POST"])
def create_goal():
    request_body = request.get_json()

    if "title" not in request_body:
        return jsonify({"details": "Invalid data"}), 400

    new_goal = Goal(
        title=request_body["title"]
    )

    db.session.add(new_goal)
    db.session.commit()

    response_body = {
        "goal": {
            "id": new_goal.goal_id,
            "title": new_goal.title
        }
    }

    return jsonify(response_body), 201

@goals_bp.route("", methods=["GET"])
def read_goals():
    title_query = request.args.get("sort") 

    if title_query == "asc":
        goals = Goal.query.order_by(Goal.title.asc())
    elif title_query == "desc":
        goals = Goal.query.order_by(Goal.title.desc())
    else:
        goals = Goal.query.all() 

    goal_responses = []
    for goal in goals:
        goal_responses.append(
                {
                "id": goal.goal_id,
                "title": goal.title
                }
            )
    
    return jsonify(goal_responses), 200

@goals_bp.route("/<goal_id>", methods=["GET"])
def read_goal(goal_id):
    goal_id = int(goal_id)
    goal = Goal.query.get(goal_id)
    
    goal_dict = {}
    if goal == None:
        return jsonify(None), 404
    else: 
        goal_dict = {
            "goal": {
                "id": goal.goal_id,
                "title": goal.title
        }
    }
    
    return jsonify(goal_dict), 200

@goals_bp.route("/<goal_id>",methods=["PUT"])
def update_goal(goal_id):
    goal_id = int(goal_id)
    goal = Goal.query.get(goal_id)

    updated_body = request.get_json()

    if goal == None:
        return jsonify(None), 404

    else: 
        goal.title = updated_body["title"]
        
        db.session.commit()
        
        goal_dict = {}
        goal_dict = {
            "goal": {
                "id": goal.goal_id,
                "title": goal.title
            }
        }
        
        return jsonify(goal_dict), 200

@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal_id = int(goal_id)
    goal = Goal.query.get(goal_id)

    
    if goal == None:
        return jsonify(None), 404

    else: 
        db.session.delete(goal)
        db.session.commit()
    
    response_body = {}
    response_body = {
        "details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}
    return jsonify(response_body), 200

@goals_bp.route("/<goal_id>/tasks", methods=["POST", "GET"])
def create_list(goal_id):
    goal_id = int(goal_id)
    goal = Goal.query.get(goal_id)

    if goal == None:
        return jsonify(None), 404

    if request.method == "POST":
        request_body = request.get_json()
        task_ids = request_body["task_ids"]

        for task_id in task_ids:
            task = Task.query.get(task_id)
            task.goal_id = goal.goal_id
        
        db.session.commit()
        
        return jsonify({"id": goal.goal_id, "task_ids": request_body["task_ids"]}), 200

    elif request.method == "GET":
        tasks_and_goals = []

        for task in goal.tasks:
            tasks_and_goals.append({
                "id": task.task_id,
                "goal_id": task.goal_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else True
            })
        
        return jsonify({"id": goal.goal_id, "title": goal.title, "tasks": tasks_and_goals}), 200