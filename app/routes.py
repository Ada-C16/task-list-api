from flask.wrappers import Response
from sqlalchemy.orm import query
from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request
from datetime import datetime
import os
import requests
from app.models.goal import Goal

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "POST":
        
        request_body = request.get_json()
        
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return {
                "details": "Invalid data"
            },400
        new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        completed_at=request_body["completed_at"])
        is_complete = new_task.completed_at is not None

        db.session.add(new_task)
        db.session.commit()

        return {'task':
            {"id": new_task.task_id,
            "title": new_task.title,
            "description": new_task.description,
                
            "is_complete": is_complete
            }},201
    
    elif request.method == "GET":
        query = request.args.get("sort")
        if query ==  "asc":
            tasks = Task.query.order_by(Task.title)
        elif query == "desc":
            tasks = Task.query.order_by(Task.title.desc())   
        else:
            tasks = Task.query.all()
        tasks_response = []
        for task in tasks:
            is_complete = task.completed_at is not None
            tasks_response.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                
                "is_complete": is_complete
            })
        return jsonify(tasks_response)

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
            return make_response("", 404)

    if request.method == "GET":
        response_body = {"task": (task.to_dict())}
        return jsonify(response_body),200 
        
    
    elif request.method == "PUT":
        form_data = request.get_json()

        task.title = form_data["title"]
        task.description = form_data["description"]
        if "completed_at" in form_data :
            task.completed_at = form_data["completed_at"]
        else:
            task.completed_at = None

        db.session.commit()
        

        return {"task":
        {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete":bool(task.completed_at) 
        }
        },200
    
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return {
        "details": f'Task {task_id} "{task.title}" successfully deleted'
    }

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):
    if not task_id.isnumeric():
        return {"Error": f"{task_id} must be numeric."} , 404
    task_id = int(task_id)
    task = Task.query.get(task_id)
    if not task :
        return "None", 404

    task.completed_at = datetime.utcnow()
    #save action
    db.session.commit()
    path = "https://slack.com/api/chat.postMessage"

    SLACK_API_KEY = os.environ.get("SLACK_API_KEY")

    query_params = {
        "token":SLACK_API_KEY,
        "channel": "task-notifications",
        "text":f"Task {task.title} is complete!"
    }
    response = requests.post(path, data=query_params)
    
    return {"task":{
        "id":task.task_id,
        "title":task.title,
        "description": task.description,
        "is_complete": True
            } }, 200

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(task_id):
    if not task_id.isnumeric():
        return {"Error": f"{task_id} must be numeric."} , 404
    task_id = int(task_id)
    task = Task.query.get(task_id)
    if not task :
        return "None", 404

    task.completed_at = None
    #save action
    db.session.commit()
    return {"task":{
        "id":task.task_id,
        "title":task.title,
        "description": task.description,
        "is_complete": False
            } }, 200

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")


@goals_bp.route("", methods=["GET", "POST"])
def handle_goals():
    if request.method == "POST":
        
        request_body = request.get_json()
        
        if "title" not in request_body:
            return {
                "details": "Invalid data"
            },400
        new_goal = Goal(title=request_body["title"])

        db.session.add(new_goal)
        db.session.commit()

        return {'goal':
            {"id": new_goal.goal_id,
            "title": new_goal.title
            }},201
    
    elif request.method == "GET":
        query = request.args.get("sort")
        if query ==  "asc":
            goals = Goal.query.order_by(Goal.title)
        elif query == "desc":
            goals = Goal.query.order_by(Goal.title.desc())   
        else:
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

    if request.method == "GET":
        return {"goal":
        {
            "id": goal.goal_id,
            "title": goal.title
        }
        }
    
    elif request.method == "PUT":
        form_data = request.get_json()
        goal.title = form_data["title"]

        db.session.commit()
        

        return {"goal":
            {
                "id": goal.goal_id,
                "title": goal.title
            }
        },200
    
    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return {
        "details": f'Goal {goal_id} "{goal.title}" successfully deleted'
    }

@goals_bp.route("/<goal_id>/tasks", methods=["POST"])
def post_tasks_for_goals(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    request_body = request.get_json()

    for each_task in request_body["task_ids"]:
        each_task = Task.query.get(each_task)
        each_task.fk_goal_id = goal.goal_id
    
    return make_response(jsonify({"id":goal.goal_id, "task_ids":request_body["task_ids"]}),200)

@goals_bp.route("/<goal_id>/tasks",methods=["GET"])
def get_tasks_for_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    response_body=goal.verbose_goal_dict()
    return jsonify(response_body), 200