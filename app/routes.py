from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.task import Task 
from app.models.goal import Goal 
from sqlalchemy import desc
from sqlalchemy import asc
import datetime
import requests 
import os
from dotenv import load_dotenv

tasks_bp = Blueprint("tasks" , __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

def return_response_task(task_id):
    task = Task.query.get(task_id)
    return {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete" : False if task.completed_at == None else True 
        }
def return_response_goal(goal_id):
    goal = Goal.query.get(goal_id)
    return {
            "id": goal.goal_id,
            "title": goal.title
            }

def return_response_goal_id(task_id):
    task = Task.query.get(task_id)
    return {
            "id": task.task_id,
            "title": task.title,
            "goal_id": task.goal_id,
            "description": task.description,
            "is_complete": False if task.completed_at == None else True 
            }

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        sort_title_query = request.args.get("sort")
        if sort_title_query:
            if sort_title_query == "asc":
                tasks = Task.query.order_by(Task.title.asc())
            elif sort_title_query == "desc":
                tasks = Task.query.order_by(Task.title.desc())
        else:
            tasks = Task.query.all()
        tasks_response = []
        for task in tasks:
            tasks_response.append(return_response_task(task.task_id))
        return jsonify(tasks_response) 

    elif request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            response_body = {"details": "Invalid data"}
            return response_body, 400   
        new_task = Task(title=request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"])
        db.session.add(new_task)
        db.session.commit()
        if new_task.completed_at is None:
            response_body = {"task" : return_response_task(new_task.task_id)}
        else:
            response_body = {"task" : return_response_task(new_task.task_id)}
        return response_body, 201

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("Task does not exist", 404)
    elif request.method == "GET":
        if task.goal_id:
            response_body = {"task" : return_response_goal_id(task_id)}
        else:
            response_body = {"task" : return_response_task(task.task_id)}
        return response_body
    elif request.method == "PUT":
        form_data = request.get_json()
        if task.completed_at is None:
            task.title = form_data["title"]
            task.description = form_data["description"]
            db.session.commit()
            response_body = {"task" : return_response_task(task.task_id)}
        else:
            task.title = form_data["title"]
            task.description = form_data["description"]
            completed_at = datetime.date.today()
            db.session.commit()
            response_body = {"task" : return_response_task(task.task_id)}
        return response_body, 200
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        response_body = {"details": f'Task {task_id} "{task.title}" successfully deleted'}
        return response_body, 200

def slack_bot(title):
    query_path = {"channel": 'slack-api-test-channel', "text" : f"Someone just completed the task {title}"}
    header = {"Authorization": os.environ.get('BOT')}
    response = requests.post('https://slack.com/api/chat.postMessage', params=query_path, headers=header)
    return response.json()

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("Not Found", 404)
    task.completed_at = datetime.date.today()
    db.session.commit()
    slack_bot(task.title)
    return jsonify ({"task" : return_response_task(task.task_id)}), 200

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("Not Found", 404)
    task.completed_at = None
    db.session.commit()
    response_body = {"task" : return_response_task(task.task_id)}
    return response_body

@goals_bp.route("", methods=["POST", "GET"])
def handle_goals():
    request_body = request.get_json()
    if request_body == {}:
            response_body = {"details": "Invalid data"}
            return response_body, 400 
    if request.method == "POST":
        new_goal = Goal(title=request_body["title"])
        db.session.add(new_goal)
        db.session.commit()
        response_body = {"goal" : return_response_goal(new_goal.goal_id)}
        return response_body, 201
    if request.method == "GET":
        goals = Goal.query.all()
        goals_response = []
        for goal in goals:
            goals_response.append({
            "id": goal.goal_id,
            "title": goal.title})
        return jsonify(goals_response) 

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response("Goal does not exist", 404)
    elif request.method =="GET":
        response_body = {"goal" : return_response_goal(goal_id)}
        return response_body
    elif request.method == "PUT":
        form_data = request.get_json()
        goal.title = form_data["title"]
        db.session.commit()
        response_body = {"goal" : return_response_goal(goal_id)}
        return response_body
    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        response_body = {"details": f'Goal {goal_id} "{goal.title}" successfully deleted'}
        return response_body, 200

@goals_bp.route("/<goal_id>/tasks", methods=["GET", "POST"])
def handle_goals_tasks(goal_id):
    goal = Goal.query.get(goal_id)
    tasks = []
    if goal is None:
        return make_response("Goal not found", 404)
    if request.method == "POST":
        request_body = request.get_json()
        for task_id in request_body["task_ids"]:
            tasks.append(Task.query.get(task_id))
        goal.tasks = tasks
        db.session.commit()
        task_ids = []
        for task in goal.tasks:
            task_ids.append(task.task_id)
        return {"id": goal.goal_id,
        "task_ids": task_ids}
    elif request.method == "GET":
        tasks = goal.tasks
        tasks_list = []
        response_body = {
                "id": goal.goal_id,
                "title": goal.title,
                "tasks": tasks_list}
        if tasks is None:
            return response_body
        else:  
            for task in goal.tasks:
                tasks_list.append(
                    return_response_goal_id(goal_id))
        return response_body

@tasks_bp.route("/<goal_id>", methods=["GET"])
def handle_task_goal(goal_id):
    task = Task.query.get(goal_id)
    if request.method == "GET":
        return {"task": return_response_goal_id(goal_id)}



