from flask import Blueprint, jsonify, request, make_response
from app import db
from app.models.task import Task
from app.models.goal import Goal
import requests
from dotenv import load_dotenv
import os
from datetime import date

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

# ********************************************
# '/tasks' routes
# ********************************************
@tasks_bp.route("", methods = ["POST", "GET"])
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return make_response(
                {"details":"Invalid data"}, 400
            )
        new_task = Task(
            title = request_body["title"],
            description = request_body["description"],
            completed_at = request_body["completed_at"],
            
        )
        db.session.add(new_task)
        db.session.commit()

        return make_response({"task": new_task.to_dict()}, 201)
    elif request.method == "GET":
        if request.args.get("sort") == "asc":
            tasks = Task.query.order_by(Task.title.asc())
        elif request.args.get("sort") == "desc":
            tasks = Task.query.order_by(Task.title.desc())
        else:
            tasks = Task.query.all()
        task_response = []
        for task in tasks:
            task_response.append(task.to_dict())
        return jsonify(task_response), 200

@tasks_bp.route("/<task_id>", methods = ["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if not task: 
        return make_response("", 404)     
    if request.method == "GET":
        return make_response({"task": (task.to_dict())}, 200)    
    elif request.method == "PUT":
        request_body = request.get_json()
        task.title = request_body["title"]
        task.description = request_body["description"]
        if "completed_at" in request_body:
            task.completed_at = request_body["completed_at"]
        else:
            task.completed_at = None
        db.session.commit()
        return make_response({"task": task.to_dict()}, 200)
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return make_response({"details": f'Task {task.task_id} "{task.title}" successfully deleted'})

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_task_completed(task_id):
    task_id = int(task_id)
    task = Task.query.get(task_id)
    if not task:
        return make_response("", 404)
    task.completed_at = date.today()
    SLACK_API_KEY = os.environ.get("SLACK_API_KEY")
    path = "https://slack.com/api/chat.postMessage"
    payload = {
        "token": SLACK_API_KEY,
        "channel": "task-notifications",
        "text": f"Someone just completed the task {task.title}"
    }
    response = requests.post(path, payload)
    
    db.session.commit()
    return make_response({"task": task.to_dict()}, 200)

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_task_incompleted(task_id):
    task_id = int(task_id)
    task = Task.query.get(task_id)
    if not task:
        return make_response("", 404)
    task.completed_at = None
    db.session.commit()
    return make_response({"task": task.to_dict()}, 200)



# ********************************************
# '/goals' routes
# ********************************************
@goals_bp.route("", methods = ["POST", "GET"])
def handle_goals():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body:
            return make_response({"details": "Invalid data"}, 400)
        new_goal = Goal(
            title = request_body["title"]
        )
        db.session.add(new_goal)
        db.session.commit()

        return make_response({"goal": new_goal.to_dict()}, 201)
    
    elif request.method == "GET":
        goals = Goal.query.all()
        goal_response = []
        for goal in goals:
            goal_response.append(goal.to_dict())
        return jsonify(goal_response), 200


@goals_bp.route("/<goal_id>", methods = ["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return make_response("", 404)
    if request.method == "GET":
        return make_response({"goal": (goal.to_dict())}, 200)
    elif request.method == "PUT":
        request_body = request.get_json()
        goal.title = request_body["title"]
        db.session.commit()
        return make_response({"goal":goal.to_dict()})
    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return make_response({"details":f'Goal {goal.goal_id} "{goal.title}" successfully deleted'})

@goals_bp.route("/<goal_id>/tasks", methods=["POST", "GET"])
def save_tasks_for_goal(goal_id):
    request_body = request.get_json()
    if request.method == "POST":
        for task_id in request_body["task_ids"]:
            task = Task.query.get(task_id)
            if task is None:
                return make_response("", 404)
            task.goal_id_fk = goal_id
            db.session.commit()

        return make_response({
            "id": int(goal_id),
            "task_ids": request_body["task_ids"]
        }, 200)


    elif request.method == "GET":
        goal = Goal.query.get(goal_id)
        if not goal:
            return make_response("", 404)
        tasks_response = []
        for tasks in goal.tasks:
            tasks_response.append(
                tasks.to_dict()
                )    
        return jsonify({
            "id": goal.goal_id,
            "title": goal.title,
            "tasks": tasks_response
        })
        
     

        
    





    