from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request, abort
from datetime import date
from pathlib import Path
import os
from dotenv import load_dotenv
import requests
from app.models.goal import Goal


tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")
env_path = Path('.')/ '.env'
load_dotenv()


@tasks_bp.route("", methods=["POST", "GET"])
def handle_tasks():
    
    if request.method == "POST":
        request_body = request.get_json()

        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return make_response({"details":"Invalid data"}, 400)

        new_task = Task(
            title=request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"]
        )

        db.session.add(new_task)
        db.session.commit()

        return jsonify({"task": new_task.to_dict()}), 201

    elif request.method == "GET":
        task_response= []
        if request.args.get('sort') == 'asc':
            tasks = Task.query.order_by(Task.title.asc()).all()
        elif request.args.get('sort') == 'desc':
            tasks = Task.query.order_by(Task.title.desc()).all()
        else:
            tasks = Task.query.all()

        for task in tasks:
            task_response.append(task.to_dict())
        return jsonify(task_response), 200

@tasks_bp.route("/<task_id>", methods= ["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    

    if task is None:
        return make_response(f"Task {task_id} not found"), 404
        
    if request.method == "GET":
        return jsonify({"task": task.to_dict()}), 200
        
    elif request.method == "PUT":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body:
            return make_response("invalid request"), 400

        task.title=request_body["title"]
        task.description=request_body["description"]
        

        db.session.commit()
        
        return jsonify({"task": task.to_dict()}),200
        

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
    
        return ({'details': f'Task {task_id} "{task.title}" successfully deleted'}), 200


@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):
    task = Task.query.get(task_id)
    today = date.today()
    if task is None:
        return make_response("", 404)
    else:
        task.completed_at = today
        db.session.commit()
        PATH = 'https://slack.com/api/chat.postMessage'
        params = {"token": os.environ.get("SLACK_TOKEN"),
                    "channel":"task-notifications",
                    "text":f"Someone just completed the task {task.title}"
                    }
        requests.post(PATH,data=params)
        return jsonify({"task":task.to_dict()}), 200

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(task_id):
    task = Task.query.get(task_id)
    today = date.today()
    if task is None:
        return make_response("", 404)
    else:
        task.completed_at = None
        db.session.commit()
        
        return jsonify({"task":task.to_dict()}), 200
        
@goals_bp.route("", methods=["POST"])
def create_goal():
    request_body=request.get_json()
    if "title" not in request_body:
            return jsonify({"details": "Invalid data"}), 400 
    new_goal=Goal(
        title = request_body["title"]
    )
    db.session.add(new_goal)
    db.session.commit()
    
    
    return jsonify({"goal": {"id": new_goal.goal_id, "title": new_goal.title}}), 201


@goals_bp.route("", methods=["GET"])
def get_goals():
    request_body=request.get_json()
    
    goals = Goal.query.all()
    goal_response=[]
    for goal in goals:
        goal_response.append(goal.to_dict())
        if not goal:
            return make_response("", 404)
    
    return jsonify(goal_response), 200


@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal_id=int(goal_id)
    goal = Goal.query.get(goal_id)
    if not goal:
        return make_response("", 404)
    if request.method == "GET":
        return jsonify({"goal": goal.to_dict()}), 200
    
    elif request.method == "PUT":
        input_data = request.get_json()

        goal.title=input_data["title"]
        db.session.commit()
        
        return jsonify({"goal": goal.to_dict()}),200

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
    
        return ({'details': f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}), 200

@goals_bp.route("/<goal_id>/tasks", methods=["GET", "POST"])
def handles_both(goal_id):
    goal = Goal.query.get(goal_id)
    goals_response=[]
    if goal is None:
        abort(404)
    if request.method == "GET":
        answer = {
            "id": goal.goal_id,
            "title": goal.title,
            "tasks": [task.to_dict() for task in goal.tasks]
        }
        return jsonify(answer), 200
    elif request.method == "POST":
        request_body=request.get_json()
        
        task_ids = request_body["task_ids"]
        for task_id in task_ids:
            
            task = Task.query.get(task_id)
            goal.tasks.append(task)

        db.session.commit()
        return jsonify({"id":goal.goal_id, "task_ids": [task.task_id for task in goal.tasks]}), 200
        
