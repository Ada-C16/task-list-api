# from flask import Blueprint

from flask import Blueprint, jsonify, request, json
from flask.signals import request_tearing_down
from app.models.task import Task
from app import db
# import datetime
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

tasks_bp = Blueprint("tasks", __name__, url_prefix = "/tasks")

@tasks_bp.route("", methods = ["POST", "GET"])
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()

        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return {
                "details": "Invalid data"
            }, 400

        new_task = Task(title = request_body["title"],
                        description = request_body["description"],
                        completed_at = request_body["completed_at"])
        db.session.add(new_task)
        db.session.commit()

        return jsonify({
            "task": {
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": False if new_task.completed_at == None else True
            }}), 201

    elif request.method == "GET":
        task_query = request.args.get("title")
        if task_query:
            tasks = Task.query.filter_by(title = task_query)
        else:
            tasks = Task.query.all()

        sort_query = request.args.get("sort")
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc())
        elif sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc())
        else:
            tasks = Task.query.all()
        
        list_of_tasks = []
        for task in tasks:
            list_of_tasks.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                # "is_complete": task.completed_at
                "is_complete": False if task.completed_at == None else True
                # "is_complete": task.completed_at is not None
            })

        return jsonify(list_of_tasks), 200

@tasks_bp.route("/<task_id>", methods = ["GET", "PUT", "PATCH", "DELETE"])
def handle_specific_tasks(task_id):
    task = Task.query.get_or_404(task_id)

    if task is None:
        return jsonify(None), 404

    if request.method == "GET":
        return {
            "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False if task.completed_at == None else True
        }
        }
    
    elif request.method == "PUT":
        updated_body = request.get_json()

        task.title = updated_body["title"]
        task.description = updated_body["description"]
        # task.completed_at = updated_body["is_complete"]
        db.session.commit()

        return jsonify({
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else True
            }
        }), 200


# # @task_bp.route("/<task_id>/mark_complete")
#     elif request.method == "PATCH":
#         request_body = request.get_json()

#         if "title" in request_body:
#             task.title = request_body["title"]
        
#         if "description" in request_body:
#             task.description = request_body["description"]

#         if "is_complete" in request_body:
#             task.completed_at = request_body["is_complete"]
        
#         db.session.commit()

#         return jsonify({
#             "task": {
#                 "id": task.task_id,
#                 "title": task.title,
#                 "description": task.description,
#                 "is_complete": False if task.completed_at == None else True
#             }
#         }), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()

        return jsonify({
            "details": f'Task {task.task_id} "{task.title}" successfully deleted'
        }), 200

def slack_bot(title):
    query_path = {'channel':'slack_api_test_channel', 'text': title}
    header = {'Authorization': os.environ.get('slack_bot_token')}
    response = requests.post('https://slack.com/api/chat.postMessage', params = query_path, headers = header)
    return response.json()

@tasks_bp.route("/<task_id>/mark_complete", methods = ["PATCH"])
def handle_mark_complete_tasks(task_id):
    task = Task.query.get_or_404(task_id)
    
    task.completed_at = datetime.utcnow()
    db.session.commit()

    slack_bot(task.title)

    # if task is None:
    #     return jsonify(None), 404
    # else:
    #     request_body = request.get_json()

    #     if "title" in request_body:
    #         task.title = request_body["title"]
        
    #     elif "description" in request_body:
    #         task.description = request_body["description"]

    #     elif "is_complete" in request_body:
    #         task.completed_at = request_body["is_complete"]
        
        

    return jsonify({
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else True
            }
        }), 200


@tasks_bp.route("/<task_id>/mark_incomplete", methods = ["PATCH"])
def handle_mark_incomplete_tasks(task_id):
    # if request.method == "PATCH":
    
    task = Task.query.get_or_404(task_id)
    task.completed_at = None

        # slack_bot(task.title)

    # if task is None:
    #     return jsonify(None), 404
    # else:
    #     request_body = request.get_json()

    #     if "title" in request_body:
    #         task.title = request_body["title"]
        
    #     elif "description" in request_body:
    #         task.description = request_body["description"]

    #     elif "is_complete" in request_body:
    #         task.completed_at = request_body["is_complete"]
        
    db.session.commit()

    return jsonify({
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else True
            }
        }), 200

from app.models.goal import Goal

goals_bp = Blueprint("goals", __name__, url_prefix = "/goals")

@goals_bp.route("", methods = ["POST", "GET"])
def handle_goals():

    request_body = request.get_json()

    if request.method == "POST":
        new_goal = Goal(title = request_body["title"])

        db.session.add(new_goal)
        db.session.commit()

        return jsonify({
            "goal": {
                "id": new_goal.goal_id,
                "title": new_goal.title
            }
        })

    elif request.method == "GET":
        
        goal_query = request.args.get("title")
        if goal_query:
            goals = Goal.query.filter_by(title = goal_query)
        else:
            goals = Goal.query.all()

        
        list_of_goals = []
        for goal in goals:
            list_of_goals.append({
                "id": goal.goal_id,
                "title": goal.title
            })

        return jsonify(list_of_goals), 200
        

@goals_bp.route("/<goal_id>", methods = ["GET"])
def handle_one_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    if goal is None:
        return jsonify(None), 404

    if request.method == "GET":
        return jsonify({
            "goal": {
                "id": goal.goal_id,
                "title": goal.title
            }
        }), 200