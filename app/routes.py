
from flask.globals import session
from flask.wrappers import Response
from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify, make_response, request
from datetime import datetime
import os
from dotenv import load_dotenv
import requests

tasks_bp = Blueprint("tasks_bp", __name__,url_prefix="/tasks")
goals_bp = Blueprint("goals_bp", __name__,url_prefix="/goals")

#TASKS ROUTES

@tasks_bp.route("",methods =["POST","GET"])
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at"not in request_body:
            return {
                "details": "Invalid data"
        },400
        new_task = Task(
            title = request_body["title"],
            description = request_body["description"],
            completed_at = request_body["completed_at"]
        )

        db.session.add(new_task)
        db.session.commit()
        return (new_task.to_dict()),201

    elif request.method == "GET":
        tasks_response = []
        if request.args.get("sort") =="asc":
            tasks = Task.query.order_by(Task.title)
        
        elif request.args.get("sort") =="desc":
            tasks = Task.query.order_by(Task.title.desc())

        else:
            tasks = Task.query.all()
        
        for task in tasks:
            
            if not task.completed_at:
                is_complete = False
            
            else:
                is_complete =task.completed_at
            task=({"id": task.task_id, 
                "title": task.title,
                "description": task.description,
                "is_complete": is_complete})
            tasks_response.append(task)
        
        return jsonify(tasks_response)

@tasks_bp.route("/<task_id>", methods = ["GET","PUT","DELETE"])
def handle_task(task_id):
    if not task_id.isnumeric():
        return { "Error": f"{task_id} must be numeric."}, 404
    task_id = int(task_id)
    task = Task.query.get(task_id)
    if not task:
        return "None",404

    if request.method == "GET":
        return (task.to_dict()),200

    elif request.method == "PUT":
        form_data = request.get_json()
        task.title = form_data["title"]
        task.description = form_data["description"]

        db.session.commit()

        return (task.to_dict()),200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()

        return {
            'details': f'Task {task.task_id} "{task.title}" successfully deleted'
        }, 200

@tasks_bp.route("/<task_id>/mark_incomplete", methods = ["PATCH"])
def mark_incomplete(task_id):
    if not task_id.isnumeric():
        return { "Error": f"{task_id} must be numeric."}, 404
    task_id = int(task_id)
    task = Task.query.get(task_id)
    if not task:
        return "None",404
 
    task.completed_at = None

    db.session.commit()

    return (task.to_dict()),200

@tasks_bp.route("/<task_id>/mark_complete", methods = ["PATCH"])
def mark_complete(task_id):
    if not task_id.isnumeric():
        return { "Error": f"{task_id} must be numeric."}, 404
    task_id = int(task_id)
    task = Task.query.get(task_id)
    if not task:
        return "None",404
    
    task.completed_at = datetime.utcnow()

    db.session.commit()
    path = "https://slack.com/api/chat.postMessage"

    SLACK_API_KEY = os.environ.get(
            "SLACK_API_KEY")
    
    query_params = {
    "token":SLACK_API_KEY,
    "channel": "task-notifications",
    "text": f"Someone just completed the task {task.title}!"
}

    response =requests.post(path, data=query_params)
    
    return (task.to_dict()),200

#GOALS ROUTES

@goals_bp.route("",methods =["POST","GET"])
def handle_goals():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body:
            return {
                "details": "Invalid data"
        },400
        new_goal = Goal(
            title = request_body["title"])

        db.session.add(new_goal)
        db.session.commit()
        return (new_goal.to_dict()),201

    elif request.method == "GET":
        goals_response = []
        goals = Goal.query.all()
        for goal in goals:
            goal=({"id": goal.goal_id, 
                "title": goal.title})
            goals_response.append(goal)
        
        return jsonify(goals_response)

@goals_bp.route("/<goal_id>", methods = ["GET","PUT","DELETE"])
def handle_goal(goal_id):
    if not goal_id.isnumeric():
        return { "Error": f"{goal_id} must be numeric."}, 404
    goal_id = int(goal_id)
    goal = Goal.query.get(goal_id)
    if not goal:
        return "None",404

    if request.method == "GET":
        return (goal.to_dict()),200

    elif request.method == "PUT":
        form_data = request.get_json()
        goal.title = form_data["title"]

        db.session.commit()

        return (goal.to_dict()),200

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()

        return {
            'details': f'Goal {goal.goal_id} "{goal.title}" successfully deleted'
        }, 200