from flask import Blueprint, jsonify, make_response, request, Flask
from app.models.goal import Goal
from app.models.task import Task
from app import db
from datetime import datetime
import os, requests

task_list_bp = Blueprint("task_list", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@task_list_bp.route("", methods=["GET"])
def get_task_lists():
    query_sort = request.args.get("sort")
    tasks_response = []

    if query_sort == "asc":
        tasks = Task.query.order_by(Task.title)
    elif query_sort == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()
            
    for task in tasks:
        tasks_response.append(task.to_dict())

    return make_response(jsonify(tasks_response), 200)

@task_list_bp.route("/<task_id>", methods=["GET"])
def get_one_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    return make_response(jsonify({"task": task.to_dict()}), 200)

@task_list_bp.route("", methods=["POST"])
def create_a_valid_task():
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return make_response(jsonify({"details": "Invalid data"}), 400)

    new_task = Task(title = request_body["title"],
                    description = request_body["description"],
                    completed_at = request_body["completed_at"]
    )

    db.session.add(new_task)
    db.session.commit()

    return make_response(jsonify({"task": new_task.to_dict()}), 201)

@task_list_bp.route("/<task_id>", methods=["PUT"])
def update_one_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()

    task.title = data["title"]
    task.description = data["description"]
    
    db.session.commit()
    return make_response(jsonify({"task": task.to_dict()}), 200)

        

@task_list_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    db.session.delete(task)
    db.session.commit()
    return make_response(jsonify({"details": f'Task {task_id} "{task.title}" successfully deleted'}), 200)
    

@task_list_bp.route("/<task_id>/<complete_command>", methods=["PATCH"])
def mark_task_complete(task_id, complete_command):
    task = Task.query.get_or_404(task_id)

    if complete_command == "mark_complete":
        task.completed_at = datetime.utcnow()
        query = {"channel": "task-notifications", "text": f"CONGRATULATIONS YOU BEAUTIFUL HUMAN!!! You completed task: {task.title}!!!"}
        slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
        headers_dict = {"Authorization": f"Bearer {slack_bot_token}"}
        requests.post("https://slack.com/api/chat.postMessage", headers=headers_dict, params=query)
    elif complete_command == "mark_incomplete":
        task.completed_at = None   

    return make_response(jsonify({"task": task.to_dict()}), 200)

@goals_bp.route("", methods=["GET"])
def get_goals():
    query_sort = request.args.get("sort")
    goals_response = []

    if query_sort == "asc":
        goals = Goal.query.order_by(Goal.title)
    elif query_sort == "desc":
        goals = Goal.query.order_by(Goal.title.desc())
    else:
        goals = Goal.query.all()
        
    for goal in goals:
        goals_response.append(goal.to_dict())

    return make_response(jsonify(goals_response), 200)

@goals_bp.route("/<goal_id>", methods=["GET"])
def get_one_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    return make_response(jsonify({"goal": goal.to_dict()}), 200)

@goals_bp.route("", methods=["POST"])
def create_a_valid_goal():
    request_body = request.get_json()

    if "title" not in request_body:
        return make_response(jsonify({"details": "Invalid data"}), 400)
    
    new_goal = Goal(
        title = request_body["title"]
        )
    db.session.add(new_goal)
    db.session.commit()

    return make_response(jsonify({"goal": new_goal.to_dict()}), 201)

@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_a_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    db.session.delete(goal)
    db.session.commit()

    return make_response(jsonify({"details": f'Goal {goal_id} "{goal.title}" successfully deleted'}), 200)

@goals_bp.route("/<goal_id>", methods=["PUT"])
def update_a_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    request_body = request.get_json()

    goal.title = request_body["title"]
    db.session.commit
    
    return make_response(jsonify({"goal": goal.to_dict()}), 200)

@goals_bp.route("/<goal_id>/tasks", methods=["POST"])
def post_tasks_for_goal(goal_id):
    request_body = request.get_json()
    goal = Goal.query.get_or_404(goal_id)
    for each_task in request_body["task_ids"]:
        each_task = Task.query.get(each_task)
        each_task.fk_goal_id = goal.goal_id
    return make_response(jsonify({"id": goal.goal_id, "task_ids": request_body["task_ids"]}), 200)

@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_for_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    return make_response(jsonify(goal.to_dict_with_tasks(goal_id)), 200)
