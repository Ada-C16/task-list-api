from app import db
from app.models.goal import Goal
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request, abort
from datetime import date 
import requests
from dotenv import load_dotenv
import os

load_dotenv()
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST"])
def create_task():
    request_data=request.get_json()
    if "title" not in request_data or "description" not in request_data:
        return jsonify({"details": "Invalid data"}),400
    new_task=Task(title=request_data["title"], description=request_data["description"])
    db.session.add(new_task)
    db.session.commit()

    return jsonify({"task": new_task.to_dict()}), 201

@tasks_bp.route("", methods=["GET"])
def handle_tasks():
    tasks_response = []
    if request.args.get("sort")=="asc":
        tasks=Task.query.order_by(Task.title)
    elif request.args.get("sort")=="desc":
        tasks=Task.query.order_by(Task.title.desc())
   
    else:
        tasks = Task.query.all()
    for task in tasks:
        tasks_response.append(task.to_dict())
    return jsonify(tasks_response), 200

@tasks_bp.route("/<task_id>", methods=["GET", "PUT"])
def handle_task(task_id):
    task_id=validate_id_int(task_id)
    # task_id = int(task_id)
    task = Task.query.get(task_id)
    if not task:
        return make_response("", 404)
    if request.method=="GET":
        return jsonify({"task": task.to_dict()}), 200
    elif request.method== "PUT":
        request_data=request.get_json()
        task.title=request_data["title"]
        task.description=request_data["description"]
    
        db.session.commit()
        return jsonify({"task": task.to_dict()}),200

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def complete_task(task_id):
    task_id=validate_id_int(task_id)
    task = Task.query.get(task_id)
    patch_data=request.get_json()
    # print(patch_data)
    if not task:
        return make_response("", 404)
    
    else:
        task.completed_at=date.today()

        db.session.commit()
        
        my_token=os.environ.get("MY_TOKEN")
        message=f"Someone just completed the task {task.title}"
        query={"channel": "task-notifications", "text": message, "token": f"{my_token}"}
        requests.post("https://slack.com/api/chat.postMessage", data=query)
    
        
        return jsonify({"task": task.to_dict()}),200
 

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def incomplete_task(task_id):
    task_id=validate_id_int(task_id)
    task = Task.query.get(task_id)
    patch_data=request.get_json()
    # print(patch_data)
    if not task:
        return make_response("", 404)
    
    else:
        task.completed_at= None

        db.session.commit()
        return jsonify({"task": task.to_dict()}),200

@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task_id=validate_id_int(task_id)
    
    task = Task.query.get(task_id)

    if task:
        db.session.delete(task)
        db.session.commit()
        return {"details": f'Task {task_id} "{task.title}" successfully deleted'}, 200
    else:
        abort (404)

def validate_id_int(task_id):
    try:
        task_id = int(task_id)
        return (task_id)
    except:
        abort(400, "Error: Task ID needs to be a number")

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@goals_bp.route("", methods=["POST"])
def create_goal():
    request_data=request.get_json()
    if "title" not in request_data:
        return jsonify({"details": "Invalid data"}),400
    new_goal=Goal(title=request_data["title"])
    db.session.add(new_goal)
    db.session.commit()

    return jsonify({"goal": new_goal.goal_to_dict()}), 201


@goals_bp.route("", methods=["GET"])
def get_all_goals():
    all_goals_response = []    
    goals = Goal.query.all()
    for goal in goals:
        all_goals_response.append(goal.goal_to_dict())
    return jsonify(all_goals_response), 200

@goals_bp.route("/<goal_id>", methods=["GET", "PUT"])
def handle_one_goal(goal_id):
    goal_id=validate_goal_id_int(goal_id)
    goal = Goal.query.get(goal_id)
    if not goal:
        return make_response("", 404)
    if request.method=="GET":
        return jsonify({"goal": goal.goal_to_dict()}), 200
    elif request.method== "PUT":
        request_data=request.get_json()
        goal.title=request_data["title"]
    
        db.session.commit()
        return jsonify({"goal": goal.goal_to_dict()}),200

@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal_id=validate_goal_id_int(goal_id)
    
    goal = Goal.query.get(goal_id)

    if goal:
        db.session.delete(goal)
        db.session.commit()
        return {"details": f'Goal {goal_id} "{goal.title}" successfully deleted'}, 200
    else:
        abort (404)


def validate_goal_id_int(goal_id):
    try:
        goal_id = int(goal_id)
        return (goal_id)
    except:
        abort(400, "Error: Task ID needs to be a number")


@goals_bp.route("/<goal_id>/tasks", methods=["POST"])
def create_goal_tasks(goal_id):
    request_data=request.get_json()
    goal = Goal.query.get(goal_id)
    
    task_ids=request_data["task_ids"]
  
    for id in task_ids:
        new_task = Task.query.get(id)
        goal.tasks.append(new_task)

        db.session.commit()

    return jsonify({"id": goal.goal_id, "task_ids":[task.task_id for task in goal.tasks]}), 200

@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_goal_tasks(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return make_response("", 404)

    return jsonify({"id": goal.goal_id, "title":goal.title, "tasks":[task.to_dict() for task in goal.tasks]}), 200

    
    