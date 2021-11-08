from re import match
from app import db
from flask import Blueprint, request, make_response, jsonify, abort
from app.models.task import Task
from app.models.goal import Goal
from datetime import datetime
import requests
import os

# DEFINE BLUEPRINT
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

#-----------------
#HELPER FUNCTIONS 
def get_task_from_id(id):
    try:
        id = int(id)
    except:
        abort(400, {"error": "invalid id"})
    return Task.query.get_or_404(id)

def get_goal_from_id(id):
    try:
        id = int(id)
    except:
        abort(400, {"error": "invalid id"})
    return Goal.query.get_or_404(id)

#-----------------
#CREATE (aka POST)
@tasks_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()
    
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return make_response(jsonify({"details" : "Invalid data"}), 400)
    
    new_task = Task(
        title=request_body["title"],
        description=request_body["description"], 
        completed_at=request_body["completed_at"]
    )

    db.session.add(new_task)
    db.session.commit()

    return make_response(jsonify({"task": new_task.to_dict()}), 201)

@goals_bp.route("", methods=["POST"])
def create_goal():
    request_body = request.get_json()

    if "title" not in request_body:
        return make_response(jsonify({"details" : "Invalid data"}), 400)

    new_goal = Goal(
        title=request_body["title"]
        )

    db.session.add(new_goal)
    db.session.commit()

    return make_response(jsonify({"goal": new_goal.to_dict()}), 201)

@goals_bp.route("/<goal_id>/tasks", methods=["POST"])
def create_goal_tasks(goal_id):
    request_body = request.get_json()

    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response("Invalid Goal ID", 404)
    
    goal_task_ids = []

    for task_id in request_body["task_ids"]:
        task = Task.query.get(task_id)
        task.goal = goal
        goal_task_ids.append(task.task_id)
        db.session.add(task)
    db.session.commit
    
    return jsonify({"id": int(goal_id), "task_ids": goal_task_ids}) 

    
#-----------------
#READ ALL (aka GET)
@tasks_bp.route("", methods=["GET"])
def read_all_tasks():
    sort_query = request.args.get("sort")
    
    if sort_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    
    elif sort_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    
    else: 
        tasks = Task.query.all()
    
    tasks_response = []
    for task in tasks:
        tasks_response.append(task.to_dict())
    return jsonify(tasks_response)

@goals_bp.route("", methods=["GET"])
def read_all_goals():
    goals = Goal.query.all()

    goals_response = []
    for goal in goals:
        goals_response.append(goal.to_dict())
    return jsonify(goals_response)

#-----------------
#READ ONE (aka GET)
@tasks_bp.route("/<id>", methods=["GET"])
def read_one_task(id):
    task = get_task_from_id(id)
    request_body = request.get_json()

    if not task.goal_id:
        return make_response(jsonify({"task" : task.to_dict()}),200)
        
    else:
        task_goal_response = {
            "id": task.task_id,
            "goal_id": task.goal_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete(),
        }
        return jsonify({"task" : task_goal_response})
        
@goals_bp.route("/<id>", methods=["GET"])
def read_one_task(id):
    goal = get_goal_from_id(id)
    return make_response(jsonify({"goal" : goal.to_dict()}),200)

@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def read_goal_tasks(goal_id):
    goal = get_goal_from_id(goal_id)
    goal_tasks_response = []

    for task in goal.tasks:
        goal_tasks_response.append({
            "id": task.task_id,
            "goal_id": task.goal_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete(),
        })


    return (jsonify({"id": int(goal_id), "title": goal.title, "tasks": goal_tasks_response}), 200)
    
#-----------------
#UPDATE 
@tasks_bp.route("/<id>", methods=["PUT"]) 
def update_task(id):
    task = get_task_from_id(id)
    request_body = request.get_json()
    
    if "title" in request_body:
        task.title = request_body["title"]
    if "description" in request_body:
        task.description = request_body["description"]
    
    db.session.commit()
    
    return make_response(jsonify({"task" : task.to_dict()}),200)

@goals_bp.route("/<id>", methods=["PUT"]) 
def update_goal(id):
    goal = get_goal_from_id(id)
    request_body = request.get_json()
    
    goal.title = request_body["title"]

    db.session.commit()
    
    return make_response(jsonify({"goal" : goal.to_dict()}),200)

#-----------------
#UPDATE --TASK-- COMPLETION STATUS
@tasks_bp.route("/<id>/<completion_status>", methods=["PATCH"])
def mark_complete(id, completion_status):
    task = get_task_from_id(id)
    #task_dict = {}
    
    if completion_status == "mark_complete":
        task.completed_at = datetime.date
        
        #SLACK MESSAGING
        # SLACK_MSG_URL = 'https//slack.com/api/com.postMessage'
        # SLACK_MSG_CHANNEL = 'task-notifications'
        # SLACK_BOT_USERNAME = 'AliesBot'
        # SLACK_TOKEN = 'xoxb21582911322942688710391650efd5ToZNAmN0gXxyri2orNvT'
        # slack_msg = "Someone did a thing!"
        # slack_response = request.post(SLACK_MSG_URL,{
        #     "token": SLACK_TOKEN, 
        #     "channel": SLACK_MSG_CHANNEL,
        #     "text": slack_msg,
        #     "username": SLACK_BOT_USERNAME
        #     })

    if completion_status == "mark_incomplete":
        task.completed_at = None

    #task_dict["task"] = task.to_dict()
    return jsonify({"task" : task.to_dict()})
    
#-----------------
#DELETE
@tasks_bp.route("/<id>", methods=["DELETE"]) 
def delete_task(id):
    task = get_task_from_id(id)
    
    db.session.delete(task)
    db.session.commit()
    
    return make_response(jsonify({'details': f'Task {task.task_id} "{task.title}" successfully deleted'}),200) 

@goals_bp.route("/<id>", methods=["DELETE"]) 
def delete_goal(id):
    goal = get_goal_from_id(id)
    
    db.session.delete(goal)
    db.session.commit()
    
    return make_response(jsonify({'details': f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}),200)

