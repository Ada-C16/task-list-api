from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request
from sqlalchemy import asc, desc
from datetime import datetime, date
from app.models.goal import Goal
import requests, json
from dotenv import load_dotenv
import os
from app.models.utility_func import *

load_dotenv()


task_bp = Blueprint("task", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goal", __name__, url_prefix="/goals")

@task_bp.route("", methods=["GET"])
def get_tasks():
    all_tasks = Task.query.all()
    if not all_tasks:
        return jsonify([]), 200

    sort_query = request.args.get("sort", default="asc") 
    if sort_query == "asc":
        all_tasks = Task.query.order_by(asc(Task.title)).all()
    elif sort_query == "desc":
        all_tasks = Task.query.order_by(desc(Task.title)).all()

    tasks_response = []
    for task in all_tasks:
        tasks_response.append(task.convert_a_task_to_dict())
    return jsonify(tasks_response), 200

@task_bp.route("", methods=["POST"])
def post_a_task():
    request_body = request.get_json()

    try: 
        new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        completed_at=request_body["completed_at"])
        
        db.session.add(new_task)
        db.session.commit()

        # return {"task" : new_task.convert_a_task_to_dict()}, 201
        return new_task.concate_task_key_to_a_dict_with_return_code(201)
    except KeyError:
        return keyError_message()

@task_bp.route("/<int:task_id>", methods=["GET"])
def get_a_task_with_id(task_id):
    task = Task.query.get_or_404(task_id)
    return task.concate_task_key_to_a_dict_with_return_code(200)


@task_bp.route("/<int:task_id>", methods=["PUT"])
def put_a_task_with_id(task_id):
    task = Task.query.get_or_404(task_id)
    request_body = request.get_json()
    try:
        task.title = request_body['title']
        task.description = request_body['description']

        db.session.add(task)
        db.session.commit()
        return task.concate_task_key_to_a_dict_with_return_code()
    except KeyError:
        return keyError_message_require_all_fields()

@task_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_a_task_with_id(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return {"details": f'Task {task.task_id} \"{task.title}\" successfully deleted'}

@task_bp.route("<int:task_id>/<mark_complete_or_incomplete>", methods=["PATCH"])
def mark_a_task_completed_with_id(task_id, mark_complete_or_incomplete):
    task = Task.query.get_or_404(task_id)
    if mark_complete_or_incomplete == "mark_complete": 
        task.completed_at = date.today()

        token = os.environ.get("SLACK_API_TOKEN")
        url = "https://slack.com/api/chat.postMessage"
        headers = {'Authorization': 'Bearer ' + token}
        
        response = requests.post(url, json= {"Someone just completed the task {task.title}"}, headers={'Authorization': 'Bearer ' + token})

    else:   # mark_incomplete
        task.completed_at = None
    db.session.commit()
    return task.concate_task_key_to_a_dict_with_return_code()


@goal_bp.route("", methods=["GET"])
def get_goals():
    goals = Goal.query.all()
    if not goals:
        return jsonify([]), 200
    else:
        response = []
        for goal in goals:
            response.append(goal.convert_a_goal_to_dict())
        return jsonify(response), 200

@goal_bp.route("", methods=["POST"])
def post_a_goal():
    request_body = request.get_json()
    try:
        new_goal = Goal(title=request_body["title"])

        db.session.add(new_goal)
        db.session.commit()

        return new_goal.concate_goal_key_to_a_dict_with_return_code(201)

    except KeyError:
        return keyError_message()

@goal_bp.route("/<int:goal_id>", methods=["GET"])
def get_a_goal_with_id(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    return goal.concate_goal_key_to_a_dict_with_return_code()
        

@goal_bp.route("/<int:goal_id>", methods=["PUT"])
def put_a_goal_with_id(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    request_body = request.get_json()
    try:
        goal.title = request_body["title"]

        db.session.commit()
        return goal.concate_goal_key_to_a_dict_with_return_code(200)
    except:
        return make_response("missing require fields")

@goal_bp.route("/<int:goal_id>", methods=["DELETE"])
def delete_a_goal_with_id(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    db.session.delete(goal)
    db.session.commit()
    return {"details": f'Goal {goal.goal_id} \"{goal.title}\" successfully deleted'}


@goal_bp.route("/<int:goal_id>/tasks", methods=["GET"])
def relating_a_list_of_taskIDs_to_a_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    tasks_with_specific_goal_id = Task.query.filter_by(goal_id=goal_id).all()
    tasks_list = []
    for task in tasks_with_specific_goal_id:
        tasks_list.append(task.convert_a_task_to_dict(goal_id))

    goal_dict = goal.convert_a_goal_to_dict()
    goal_dict["tasks"] = tasks_list

    return goal_dict
        
        
@goal_bp.route("/<int:goal_id>/tasks", methods=["POST"])
def post_a_list_of_taskIDs_to_a_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    request_body = request.get_json()
    task_ids_list = request_body["task_ids"]

    for task_id in task_ids_list:
        task = Task.query.get_or_404(task_id)
        task.goal_id = goal_id
    goal.task = task_ids_list
    
    db.session.commit()
    
    return {
        "id" : goal_id,
        "task_ids" : task_ids_list
    }, 200






