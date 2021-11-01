from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.task import Task
from app.models.goal import Goal
from sqlalchemy import asc, desc, null
from datetime import datetime, timezone
import requests
import os
from dotenv import load_dotenv

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goals", __name__, url_prefix="/goals")

@task_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        sort_query = request.args.get("sort")
        if sort_query:
            tasks = Task.query.order_by(eval(sort_query)(Task.title))
        else:
            tasks = Task.query.all()
        tasks_response = []
        for task in tasks:
            tasks_response.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": bool(task.completed_at)    
            })
        return jsonify(tasks_response), 200
    if request.method == "POST":
        request_body = request.get_json()
        try:
            new_task = Task(title=request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"])

            db.session.add(new_task)
            db.session.commit()

            return {
                "task": {
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": bool(new_task.completed_at)  
                }
            }, 201
        except KeyError:
            return {"details": "Invalid data"}, 400 

@task_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return ("", 404)
    if request.method == "GET":
        response_body = {
            "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)    
        }}
        if task.goal_id:
            response_body["task"]["goal_id"] = task.goal_id
        return (response_body, 200)
    elif request.method == "PUT":
        request_body = request.get_json()
        task.title = request_body["title"]
        task.description = request_body["description"]
        db.session.commit()
        task = Task.query.get(task_id)
        return {
            "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)  
            }
        }, 200
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return {
            "details": f"Task {task.task_id} \"{task.title}\" successfully deleted"
        }, 200

@task_bp.route("/<task_id>/mark_<completion_status>", methods=["PATCH"])
def handle_task_completion(task_id, completion_status):
    task = Task.query.get(task_id)
    if task is None:
        return ("", 404)
    if request.method == "PATCH":
        if completion_status == "complete":
            task.completed_at = datetime.now(timezone.utc)
            requests.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {os.environ.get('SLACK_API_KEY')}"},
                params={
                    "channel": "task-notifications",
                    "text": f"Someone just completed the task {task.title}"
                })        
        elif completion_status == "incomplete":
            task.completed_at = None
        db.session.commit()
        return {
                "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": bool(task.completed_at)  
                }
            }, 200

@goal_bp.route("", methods=["GET", "POST"])
def handle_goals():
    if request.method == "GET":
        goals = Goal.query.all()
        goals_response = []
        for goal in goals:
            goals_response.append({
                "id": goal.goal_id,
                "title": goal.title,   
            })
        return jsonify(goals_response), 200
    if request.method == "POST":
        request_body = request.get_json()
        try:
            new_goal = Goal(title=request_body["title"])
            db.session.add(new_goal)
            db.session.commit()

            return {
                "goal": {
                "id": new_goal.goal_id,
                "title": new_goal.title  
                }
            }, 201
        except KeyError:
            return {"details": "Invalid data"}, 400

@goal_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return ("", 404)
    if request.method == "GET":
        return {
            "goal": {
            "id": goal.goal_id,
            "title": goal.title
            }
        }, 200
    if request.method == "PUT":
        request_body = request.get_json()
        goal.title = request_body["title"]
        db.session.commit()
        goal = Goal.query.get(goal_id)
        return {
            "goal": {
            "id": goal.goal_id,
            "title": goal.title 
            }
        }, 200
    if request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return {
            "details": f"Goal {goal.goal_id} \"{goal.title}\" successfully deleted"
        }, 200

@goal_bp.route("/<goal_id>/tasks", methods=["GET", "POST"])
def handle_goal_tasks(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return ("", 404)
    
    if request.method == "POST":
        request_body = request.get_json()
        tasks_to_update = request_body["task_ids"]
        for task in tasks_to_update:
            task = Task.query.get(task)
            task.goal_id = goal_id
        db.session.commit()

        return { 
            "id": eval(goal_id),
            "task_ids": tasks_to_update
        }, 200
    elif request.method == "GET":
        tasks_response = []
        for task in goal.tasks:
            tasks_response.append({
                "id": task.task_id,
                "goal_id": task.goal_id,
                "title": task.title,
                "description": task.description,
                "is_complete": bool(task.completed_at)
            })
        return {
            "id": goal.goal_id,
            "title": goal.title,
            "tasks": tasks_response}, 200