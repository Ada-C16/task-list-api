from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify, make_response, request
from datetime import datetime
import os
import requests
from dotenv import load_dotenv
load_dotenv()

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        sort_query = request.args.get("sort")
        
        if sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc())
        elif sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc())            
        else:
            tasks = Task.query.all()

        tasks_response = []
        for task in tasks:
            tasks_response.append({
                "id" : task.task_id,
                "title" : task.title,
                "description" : task.description,
                "is_complete" : task.is_complete
            })
        return jsonify(tasks_response)

    elif request.method == "POST":
        request_body = request.get_json()
        title = request_body.get("title")
        description = request_body.get("description")

        if title is None or description is None:
            return jsonify({"details" : "Invalid data"}), 400

        try: 
            completed_at = request_body["completed_at"]
        except KeyError:
            return jsonify({"details" : "Invalid data"}), 400

        new_task = Task(title=title, description=description, completed_at=completed_at)

        if new_task.completed_at:
            new_task.is_complete = True

        db.session.add(new_task)
        db.session.commit()

        return jsonify({"task" : {
            "id" : new_task.task_id,
            "title" : new_task.title,
            "description" : new_task.description,
            "is_complete" : new_task.is_complete
        }}), 201

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return jsonify(None), 404
    
    if request.method == "GET":
        if task.goal_id:
            return {"task" : {
            "id" : task.task_id,
            "goal_id" : task.goal_id,
            "title" : task.title,
            "description" : task.description,
            "is_complete" : task.is_complete
        }}
        return {"task" : {
            "id" : task.task_id,
            "title" : task.title,
            "description" : task.description,
            "is_complete" : task.is_complete
        }}
    elif request.method == "PUT":
        request_body = request.get_json()

        task.title = request_body["title"]
        task.description = request_body["description"]

        if request_body.get("completed_at"):
            task.is_complete = True

        db.session.commit()

        return jsonify({"task" : {
            "id" : task.task_id,
            "title" : task.title,
            "description" : task.description,
            "is_complete" : task.is_complete
        }}), 200
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return jsonify({"details" : f'Task {task.task_id} "{task.title}" successfully deleted'})

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_tasks_complete(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return jsonify(None), 404

    task.is_complete = True
    task.completed_at = datetime.utcnow()

    # Slack API Call
    PATH = "https://slack.com/api/chat.postMessage"
    API_KEY = os.environ.get("API_KEY")

    post_header = {
        "authorization" :  f"Bearer {API_KEY}"
    }
    post_body = {
        "channel" : "task-notifications",
        "text" : f"Someone just completed the task {task.title}"
    }

    requests.post(PATH, json=post_body, headers=post_header)

    return jsonify({ "task" : {
        "id" : task.task_id,
        "title" : task.title,
        "description" : task.description,
        "is_complete" : task.is_complete
    }}), 200

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_tasks_incomplete(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return jsonify(None), 404

    # request_body = request.get_json()

    task.is_complete = False
    task.completed_at = None

    return jsonify({ "task" : {
        "id" : task.task_id,
        "title" : task.title,
        "description" : task.description,
        "is_complete" : task.is_complete
    }}), 200

@goals_bp.route("", methods=["GET","POST"])
def handle_goals():
    if request.method == "GET":
        goals = Goal.query.all()

        goals_response = []
        for goal in goals:
            goals_response.append({
                "id" : goal.goal_id,
                "title" : goal.title
            })
        return jsonify(goals_response)

    elif request.method == "POST":
        request_body = request.get_json()
        title = request_body.get("title")

        if not title:
            return jsonify({
                "details" : "Invalid data"
            }), 400

        new_goal = Goal(title=title)

        db.session.add(new_goal)
        db.session.commit()

        return jsonify({"goal" : {
            "id" : new_goal.goal_id,
            "title" : new_goal.title
        }}), 201

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal = Goal.query.get(goal_id)

    if not goal:
        return jsonify(None), 404
    
    if request.method == "GET":
        return jsonify({"goal" : {
            "id" : goal.goal_id,
            "title" : goal.title
        }})
    
    elif request.method == "PUT":
        request_body = request.get_json()
        title = request_body.get("title")

        if title:
            goal.title = title

            db.session.commit()

            return jsonify({"goal" : {
                "id" : goal.goal_id,
                "title" : goal.title
            }})
        else:
            return jsonify(None), 404
    
    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()

        return jsonify({
            "details" : f'Goal {goal.goal_id} "{goal.title}" successfully deleted'
        }) 

@goals_bp.route("/<goal_id>/tasks", methods=["POST", "GET"])
def handle_goals_tasks(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return jsonify(None), 404

    if request.method == "POST":
        request_body = request.get_json()

        task_ids = request_body.get("task_ids")
        for task_id in task_ids:
            task = Task.query.get(task_id)
            task.goal = goal

        db.session.commit()

        return jsonify({
            "id" : goal.goal_id,
            "task_ids" : task_ids
        })

    elif request.method == "GET":
        tasks_response = []
        for task in goal.tasks:
            tasks_response.append({
                "id" : task.task_id,
                "goal_id" : task.goal_id, 
                "title" : task.title,
                "description" : task.description,
                "is_complete" : task.is_complete
            })
        
        return jsonify({
            "id" : goal.goal_id,
            "title" : goal.title, 
            "tasks" : tasks_response
        })