from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import request, Blueprint, jsonify
from sqlalchemy import desc
from datetime import datetime
import requests

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")


@tasks_bp.route("", methods=["POST", "GET"])
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return jsonify(details="Invalid data"), 400

        new_task = Task(
            title=request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"]
        )

        db.session.add(new_task)
        db.session.commit()

        return jsonify(task=new_task.to_json()), 201

    elif request.method == "GET":
        query = request.args.get("sort")
        if query == "desc":
            tasks = Task.query.order_by(Task.title.desc())
        elif query == "asc":
            tasks = Task.query.order_by(Task.title.asc())
        else:
            tasks = Task.query.all()

        response_body = []
        for task in tasks:
            response_body.append(task.to_json())

        return jsonify(response_body), 200


@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == "GET":
        if task.goal_id:
            return jsonify(task=task.to_json_task()), 200
        else:
            return jsonify(task=task.to_json()), 200

    elif request.method == "PUT":
        request_body = request.get_json()
        task.title = request_body["title"]
        task.description = request_body["description"]
        db.session.commit()
        return jsonify(task=task.to_json()), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return jsonify(details="Task 1 \"Go on my daily walk 🏞\" successfully deleted"), 200


@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_task_complete(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed_at = datetime.now()
    db.session.commit()
    return jsonify(task=task.to_json()), 200


@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def handle_task_incomplete(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed_at = None
    db.session.commit()
    return jsonify(task=task.to_json()), 200

# send to slack success
# @tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
# def handle_task_complete(task_id):
#     task = Task.query.get_or_404(task_id)
#     request_body = request.get_json()
#     task.title = request_body["title"]
#     task.completed_at=request_body["completed_at"]
#     db.session.commit()
#     payload = {'channel': 'task-notifications', 'text':'Someone just completed the task My Beautiful Task'}
#     headers = {'Authorization': 'Bearer xoxb-2670534943107-2670566648851-uFPaGz2Tg58fjVfyzo8lZjq2'}
#     r = requests.post('https://slack.com/api/chat.postMessage', params=payload, headers=headers)
#     return jsonify(task=task.to_json()), 200


# goals
@goals_bp.route("", methods=["POST", "GET"])
def handle_goals():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body:
            return jsonify(details="Invalid data"), 400

        new_goal = Goal(
            title=request_body["title"]
        )

        db.session.add(new_goal)
        db.session.commit()

        return jsonify(goal=new_goal.to_json_goal()), 201

    elif request.method == "GET":
        goals = Goal.query.all()
        response_body = []
        for goal in goals:
            response_body.append(goal.to_json_goal())

        return jsonify(response_body), 200


@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_Goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if request.method == "GET":
        return jsonify(goal=goal.to_json_goal()), 200

    elif request.method == "PUT":
        request_body = request.get_json()
        goal.title = request_body["title"]
        db.session.commit()
        return jsonify(goal=goal.to_json_goal()), 200

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return jsonify(details="Goal 1 \"Build a habit of going outside daily\" successfully deleted"), 200


@goals_bp.route("/<goal_id>/tasks", methods=["GET", "POST"])
def handle_goals_tasks(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    if request.method == "POST":
        request_body = request.get_json()
        task_list = request_body["task_ids"]

        for task_id in task_list:
            task = Task.query.get(task_id)
            task.goal = goal

        db.session.commit()
        return {
            "id": goal.id,
            "task_ids": task_list
        }, 200

    elif request.method == "GET":
        tasks = goal.tasks
        task_response = []
        for task in tasks:
            task_response.append(task.to_json_task())

        return {
            "id":  goal.id,
            "title": goal.title,
            "tasks": task_response
        }, 200
