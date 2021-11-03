from flask import Blueprint, jsonify, make_response, request
from app.models.task import Task
from app.models.goal import Goal
from app import db
from datetime import datetime
import requests
import os


tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")
path = "https://slack.com/api/chat.postMessage"
token = os.environ.get("SLACK_TOKEN")


@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        sort_query = request.args.get("sort")
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc())
            print(tasks)
        elif sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc())
            print(tasks)
        else:
            tasks = Task.query.all()
            print(tasks)
        tasks_response = []

        for task in tasks:
            tasks_response.append(
                {
                    "id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": False if task.completed_at == None else True
                }
            )
        return jsonify(tasks_response), 200

    elif request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return {
                "details": "Invalid data"
            }, 400

        new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        completed_at=request_body["completed_at"])
        db.session.add(new_task)
        db.session.commit()

        new_task_response = {
            "task": {
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": False if new_task.completed_at == None else True
            }
        }
        return jsonify(new_task_response), 201


@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    if request.method == "GET":
        if task.goal_id is None:
            return {
                "task": {
                    "id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": False if task.completed_at == None else True
                }
            }
        if task.goal_id is not None:
            return {
                "task": {
                    "id": task.task_id,
                    "goal_id": task.goal_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": False if task.completed_at == None else True
                }
            }

    elif request.method == "PUT":
        form_data = request.get_json()
        task.title = form_data["title"]
        task.description = form_data["description"]
        db.session.commit()
        return {
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else True
            }
        }

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return {
            "details": f'Task {task.task_id} \"{task.title}\" successfully deleted'
        }


@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def task_complete(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    if request.method == "PATCH":
        task.completed_at = datetime.now()
        db.session.commit()
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "channel": "task-notifications",
            "text": "Someone just completed the task My Beautiful Task"
        }
        requests.post(path, headers=headers, data=data)
        return {
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else True
            }
        }


@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def task_incomplete(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    if request.method == "PATCH":
        task.completed_at = None
        db.session.commit()
        return {
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else True
            }
        }


# G O A L   E N D P O I N T S


@goals_bp.route("", methods=["POST", "GET"])
def handle_goals():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body:
            return {
                "details": "Invalid data"
            }, 400

        new_goal = Goal(title=request_body["title"])
        db.session.add(new_goal)
        db.session.commit()
        new_goal_response = {
            "goal": {
                "id": new_goal.goal_id,
                "title": new_goal.title,
            }
        }
        return jsonify(new_goal_response), 201

    elif request.method == "GET":
        goals = Goal.query.all()
        goals_response = []
        for goal in goals:
            goals_response.append(
                {
                    "id": goal.goal_id,
                    "title": goal.title
                }
            )
        return jsonify(goals_response), 200


@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response("", 404)

    if request.method == "GET":
        return {
            "goal": {
                "id": goal.goal_id,
                "title": goal.title
            }
        }

    elif request.method == "PUT":
        form_data = request.get_json()
        goal.title = form_data["title"]
        db.session.commit()
        return {
            "goal": {
                "id": goal.goal_id,
                "title": goal.title
            }
        }

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return {
            "details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'
        }

# G O A L S / T A S K S   E N D P O I N T S

@goals_bp.route("/<goal_id>/tasks", methods=["POST", "GET"])
def handle_goals_tasks(goal_id):
    goal = Goal.query.get(goal_id) 
    if goal is None:
        return make_response("", 404)

    if request.method == "POST":
        request_body = request.get_json()
        task_ids=request_body["task_ids"]
        for task_id in task_ids:
            task = Task.query.get(task_id)
            task.goal = goal
        db.session.commit()
        response_task_ids = []
        for task in goal.tasks:
            response_task_ids.append(task.task_id)
        new_tasks_response = {
            "id": goal.goal_id,
            "task_ids": response_task_ids
        }
        return jsonify(new_tasks_response), 200

    elif request.method == "GET":
        response_tasks = []
        for task in goal.tasks:
            response_tasks.append({
                "id": task.task_id,
                "goal_id": int(goal_id),
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else True
            })

        return {
            "id": goal.goal_id,
            "title": goal.title,
            "tasks": response_tasks
        }, 200
        
