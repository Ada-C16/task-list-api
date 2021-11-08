from flask import abort, Blueprint, jsonify, request, make_response
from app.models.task import Task
from app.models.goal import Goal
from app import db
from datetime import datetime
from dotenv import load_dotenv
import os
import requests

load_dotenv()

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goal_bp", __name__, url_prefix="/goals")

@tasks_bp.route("", methods=["POST"])
def create_task():
    request_data = request.get_json()

    if "title" not in request_data or "description" not in request_data \
        or "completed_at" not in request_data:
        return jsonify({"details": "Invalid data"}), 400

    new_task = Task(title=request_data["title"], description=request_data["description"],
                completed_at=request_data["completed_at"])
    
    db.session.add(new_task)
    db.session.commit()

    return jsonify({"task": new_task.to_dict()}), 201
    

@tasks_bp.route("", methods=["GET"])
def list_all_tasks():
    tasks_response = []
    #Can't be jsonified
    if request.args.get('sort') == 'asc':
        tasks = Task.query.order_by(Task.title.asc()).all()

    elif request.args.get('sort') == 'desc':
        tasks = Task.query.order_by(Task.title.desc()).all()

    else:
        tasks = Task.query.all()

    for task in tasks:
        tasks_response.append(task.to_dict())
    return jsonify(tasks_response), 200


@tasks_bp.route("/<task_id>", methods=["GET", "PUT"])
def handle_task(task_id):
    print(f"handle task {task_id}")
    print(f"Request Method {request.method}")
    task_id = int(task_id)
    task = Task.query.get(task_id)
    if task is None:
        return make_response(f"Task {task_id} not found", 404)

    if request.method == "GET":
        return jsonify({"task": task.to_dict()}), 200
        
    elif request.method == "PUT":
        input_data = request.get_json()
        input_data = sanitize_data(input_data)
        task.title = input_data["title"]
        task.description = input_data["description"]
        db.session.commit()

        return jsonify({"task": task.to_dict()}), 200

def sanitize_data(input_data):
    data_types = {"title": str, "description": str}
    for name, val_type in data_types.items():
        try:
            val = input_data[name]
            type_test = val_type(val)
        except Exception as e:
            abort(400, "Bad Data")
    return input_data


@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    print(f"Delete{task_id}")
    try:
        task_id = int(task_id)
    except ValueError:
        return 404
    task = Task.query.get(task_id)

    if task:
        db.session.delete(task)
        db.session.commit()
        response_string = f'Task {task_id} "{task.title}" successfully deleted'

        return jsonify({
            "details": response_string
            }), 200

    else:
        return make_response("", 404)

@tasks_bp.route("/<task_id>/<completion_status>", methods=["PATCH"])
def mark_complete(task_id, completion_status):
    
    task = Task.query.get(task_id)
    PATH = "https://slack.com/api/chat.postMessage"

    if task is None:
        return make_response("", 404)

    elif completion_status == "mark_complete":
        task.completed_at = datetime.utcnow
        token=os.environ.get("TOKEN")
        query_params = {
        "token": token,
        "channel": "task-notifications",
        "text": f"Someone just completed task {task.title}"
    }

        requests.post(PATH, data=query_params)

    elif completion_status == "mark_incomplete":
        task.completed_at = None

    return jsonify({"task": task.to_dict()}), 200


@goal_bp.route("", methods=["GET", "POST"])
def handle_goals():
    goal_response = []

    if request.method == "GET":
        goals = Goal.query.all()
        goal_response = [goal.to_dict() for goal in goals]
        return jsonify(goal_response), 200

    elif request.method == "POST":
        request_body = request.get_json()

        if "title" not in request_body:
            return make_response({"details": "Invalid data"}, 400) 

        new_goal = Goal(title=request_body["title"])
        db.session.add(new_goal)
        db.session.commit()

        return make_response({"goal": new_goal.to_dict()}, 201)

@goal_bp.route("/<goal_id>", methods=["GET", "DELETE", "PUT", "PATCH"])
def handle_goal(goal_id):
    goal = Goal.query.get(goal_id)

    if request.method == "GET":
        if not goal:
            return make_response(f"Goal {goal_id} not found", 404)
        
        return {"goal": goal.to_dict()}

    elif request.method == "DELETE":
        if not goal:
            return make_response("", 404)

        db.session.delete(goal)
        db.session.commit()
        
        return {"details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}

    elif request.method == "PUT":
        if not goal:
            return make_response("", 404)

        request_body = request.get_json()
        goal.title = request_body["title"] if "title" in request_body else goal.title

        return make_response({"goal": goal.to_dict()}, 200)



@goal_bp.route("/<goal_id>/tasks", methods=["POST"])
def create_tasks_for_goal(goal_id):
    request_body = request.get_json()

    goal = Goal.query.get(goal_id)

    if not goal:
        return "", 404

    task_ids = request_body['task_ids']


    for id in task_ids:
        task = Task.query.get(id)
        task.goal_id = goal_id
        db.session.commit()


    return make_response({"id":int(goal_id), "task_ids": task_ids}), 200


@goal_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_for_goal(goal_id):
    goal = Goal.query.get(goal_id)

    if not goal:
        return "", 404

    task_list = []

    for task in goal.tasks:
        # task = Goal.query.get()
        task_list.append(task.to_dict())

    return {
        "id": goal.goal_id,
        "title": goal.title,
        "tasks": task_list
    }, 200

    