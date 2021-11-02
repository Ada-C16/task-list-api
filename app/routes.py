from flask import Blueprint, jsonify, make_response, request
from app.models.task import Task
from app.models.goal import Goal
from app import db
from datetime import datetime, timezone
import requests
import os


tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

def is_input_valid(number):
    try:
        int(number)
    except:
        return make_response(f"{number} is not an int!", 400)


def is_parameter_found(model, parameter_id):
    if is_input_valid(parameter_id):
        return is_input_valid(parameter_id)
    elif model.query.get(parameter_id) is None:
        return make_response(f"{parameter_id} was not found!", 404)
    


#TASK ROUTES
@tasks_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return jsonify({"details": "Invalid data"}),400
    new_task = Task(title=request_body["title"],
                    description=request_body["description"], 
                    completed_at=request_body["completed_at"]
                    )

    db.session.add(new_task)
    db.session.commit()
    response_body = {}
    response_body["task"] = new_task.to_dict()
    return jsonify(response_body), 201


@tasks_bp.route("", methods=["GET"])
def read_tasks():
    tasks = Task.query.all()
    response_body = []
    sort_query = request.args.get("sort")

    if sort_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    elif sort_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()
        
    for task in tasks:
        response_body.append(
            task.to_dict())
    return jsonify(response_body), 200


@tasks_bp.route("/<task_id>", methods=["GET"])
def read_task(task_id):
    check_not_found = is_parameter_found(Task, task_id)
    if check_not_found:
        return check_not_found
    task = Task.query.get(task_id)
    task_response = {}
    task_response["task"] = task.to_dict()
    return jsonify(task_response), 200


@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    check_not_found = is_parameter_found(Task, task_id)
    if check_not_found:
        return check_not_found

    task = Task.query.get(task_id)
    request_body = request.get_json()
    task.title = request_body["title"]
    task.description = request_body["description"]
    db.session.commit()

    response_body = {}
    response_body["task"] = task.to_dict()
    return jsonify(response_body), 200


@tasks_bp.route("/<task_id>", methods=["PATCH"])
def update_task_parameter(task_id):
    check_not_found = is_parameter_found(Task, task_id)
    if check_not_found:
        return check_not_found

    task = Task.query.get(task_id)
    request_body = request.get_json()
    if "title" in request_body:
        task.name = request_body["title"]
    if "description" in request_body:
        task.description = request_body["description"]
    
    db.session.commit()
    return make_response(f"Task {task_id} successfully updated!", 200)

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_task_complete(task_id):
    check_not_found = is_parameter_found(Task, task_id)
    if check_not_found:
        return check_not_found

    task = Task.query.get(task_id)
    task.completed_at = datetime.now(timezone.utc)
    response_body = {}
    response_body = task.to_dict()

    db.session.commit()
    slack_url = "https://slack.com/api/chat.postMessage"
    slack_bot_data = {"token": os.environ.get("ADA_BOT_TOKEN"),
                        "channel": "task-notifications", 
                        "text": (f"Someone just completed the task {task.title}") 
                        }
    requests.post(slack_url, slack_bot_data)
    

    return jsonify({"task": response_body}), 200


@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_task_incomplete(task_id):
    check_not_found = is_parameter_found(Task, task_id)
    if check_not_found:
        return check_not_found

    task = Task.query.get(task_id)
    task.completed_at = None
    response_body = {}
    response_body = task.to_dict()

    db.session.commit()
    return jsonify({"task": response_body}), 200

@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    check_not_found = is_parameter_found(Task, task_id)
    if check_not_found:
        return check_not_found

    task = Task.query.get(task_id)
    task_title = task.title
    response_str = f'Task {task_id} "{task_title}" successfully deleted'

    db.session.delete(task)
    db.session.commit()
    return jsonify({
        "details": response_str
        }), 200



#GOAL ROUTES 

@goals_bp.route("", methods=["POST"])
def create_goal():
    request_body = request.get_json()
    if "title" not in request_body:
        return jsonify({"details": "Invalid data"}), 400

    new_goal = Goal(title=request_body["title"],
                    )

    db.session.add(new_goal)
    db.session.commit()
    response_body = {}
    response_body["goal"] = new_goal.to_dict()
    return jsonify(response_body), 201


@goals_bp.route("", methods=["GET"])
def read_goals():
    goals = Goal.query.all()
    response_body = []
    sort_query = request.args.get("sort")

    if sort_query == "asc":
        goals = Goal.query.order_by(Goal.title.asc())
    elif sort_query == "desc":
        goals = Goal.query.order_by(Goal.title.desc())
    else:
        goals = Goal.query.all()
        
    for goal in goals:
        response_body.append(
            goal.to_dict())
    return jsonify(response_body), 200


@goals_bp.route("/<goal_id>", methods=["GET"])
def read_goal(goal_id):
    check_not_found = is_parameter_found(Goal, goal_id)
    if check_not_found:
        return check_not_found

    goal = Goal.query.get(goal_id)
    goal_response = {}
    goal_response["goal"] = goal.to_dict()
    return jsonify(goal_response), 200


@goals_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    check_not_found = is_parameter_found(Goal, goal_id)
    if check_not_found:
        return check_not_found

    goal = Goal.query.get(goal_id)
    request_body = request.get_json()
    goal.title = request_body["title"]
    
    db.session.commit()

    response_body = {}
    response_body["goal"] = goal.to_dict()
    return jsonify(response_body), 200


@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    check_not_found = is_parameter_found(Goal, goal_id)
    if check_not_found:
        return check_not_found
        
    goal = Goal.query.get(goal_id)
    goal_title = goal.title
    response_str = f'Goal {goal_id} "{goal_title}" successfully deleted'

    db.session.delete(goal)
    db.session.commit()
    return jsonify({
        "details": response_str
    }), 200
