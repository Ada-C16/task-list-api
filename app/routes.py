from flask import Blueprint, jsonify, request, make_response
import requests
from app import db
from app.models.task import Task
from app.models.goal import Goal
from datetime import date, datetime, timezone
import os

# Create blueprints
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        sort_query = request.args.get("sort")

        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc()).all()
        elif sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc()).all()
        else:
            tasks = Task.query.all()

        tasks_response = []
        for task in tasks:
            tasks_response.append(task.to_json())

        return jsonify(tasks_response)
        
    elif request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in \
            request_body or "completed_at" not in request_body:
            return {
                "details": "Invalid data"
            }, 400
        
        new_task = Task(
            title= request_body["title"],
            description= request_body["description"],
            completed_at= datetime.now(timezone.utc) if \
                request_body["completed_at"] != None else None
        )
        db.session.add(new_task)
        db.session.commit()

        return {"task": new_task.to_json()}, 201

@tasks_bp.route("/<task_id>", methods =["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return make_response("", 404)
    
    if request.method == "GET":
        return {
            "task": task.to_json()}
    
    elif request.method == "PUT":
        request_data = request.get_json()

        task.title = request_data["title"]
        task.description = request_data["description"]
        task.completed_at = datetime.now(timezone.utc) if \
            task.completed_at else None

        db.session.commit()

        return {"task": task.to_json()}
    
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()

        return {"details": f'Task {task.task_id} "{task.title}" successfully deleted'}

@tasks_bp.route("/<task_id>/mark_complete", methods =["PATCH"])
def update_task_to_complete(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return make_response("", 404)

    else:
        API_endpoint = "https://slack.com/api/chat.postMessage"
        my_headers = {'Authorization': f'Bearer {os.environ.get("SLACK_API_KEY")}'}
        my_data = {"channel": "C02J08B9S0N",
        "text": f"Someone just completed the task {task.title}"}

        requests.post(API_endpoint, data= my_data, headers= my_headers)
        task.completed_at = date.today()
        return {"task": task.to_json()}, 200
    
@tasks_bp.route("/<task_id>/mark_incomplete", methods =["PATCH"])
def update_task_to_incomplete(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)
    
    else:
        task.completed_at = None
        
        return {"task": task.to_json()}, 200

@goals_bp.route("", methods=["POST", "GET"])
def handle_goals():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body:
            return {
                "details": "Invalid data"
            }, 400

        new_goal = Goal(
            title= request_body["title"],
        )
        db.session.add(new_goal)
        db.session.commit()

        return {"goal": {
            "id": new_goal.goal_id,
            "title": new_goal.title
        }}, 201

    elif request.method == "GET":
        goals = Goal.query.all()

        goals_response = []
        for goal in goals:
            goals_response.append({
                "id": goal.goal_id,
                "title": goal.title
            })
        
        return jsonify(goals_response)

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal = Goal.query.get(goal_id)

    if goal is None:
        return make_response("", 404)

    elif request.method == "GET":
        return {
            "goal": {
                "id": goal.goal_id,
                "title": goal.title
            }
        }
    
    elif request.method == "PUT":
        request_body = request.get_json()

        goal.title = request_body["title"]
        db.session.commit()

        return {
            "goal": {
                "id": goal.goal_id,
                "title": goal.title
            }
        }

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()

        return {"details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}