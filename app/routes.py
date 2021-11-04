from io import DEFAULT_BUFFER_SIZE
from app import db
from flask import Blueprint, json, request, jsonify
from app.models.task import Task
from app.models.goal import Goal
from sqlalchemy import asc, desc
from datetime import datetime
import os, requests
from dotenv import load_dotenv

load_dotenv()

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

@tasks_bp.route("", methods=["POST", "GET"])
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        if (
            "title" not in request_body or 
            "description" not in request_body or 
            "completed_at" not in request_body
        ):
            return jsonify({"details": "Invalid data"}), 400

        new_task = Task(
            title=request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"]
        )

        db.session.add(new_task)
        db.session.commit()

        return jsonify({"task": new_task.task_dict()}), 201

    elif request.method == "GET":
        sort_query = request.args.get("sort")
        if sort_query == "asc":
            tasks = Task.query.order_by(asc("title"))
            task_response = [task.task_dict() for task in tasks]
        elif sort_query == "desc":
            tasks = Task.query.order_by(desc("title"))
            task_response = [task.task_dict() for task in tasks]
        else:
            tasks = Task.query.all()
            task_response = [task.task_dict() for task in tasks]
        return jsonify(task_response), 200


@tasks_bp.route("/<task_id>", methods={"GET", "PUT", "DELETE"})
def handle_one_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return jsonify(task), 404

    if request.method == "GET":
        if task.goal_id:
            return jsonify({"task": task.task_and_goal_dict()})
        return ({"task": task.task_dict()}), 200

    elif request.method == "PUT":
        request_body = request.get_json()
        task.title=request_body["title"]
        task.description=request_body["description"]

        db.session.commit()
        return jsonify({"task": task.task_dict()}), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        response_body = f'Task {task.task_id} "{task.title}" successfully deleted'
        return jsonify({"details": response_body}), 200


@tasks_bp.route("<task_id>/mark_complete", methods=["PATCH"])
def mark_task_complete(task_id):
    task= Task.query.get(task_id)
    if task is None:
        return jsonify(task), 404

    current_time = datetime.now()
    task.completed_at = current_time

    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    requests.post(
        url="https://slack.com/api/chat.postMessage", 
        headers={"Authorization": f"Bearer {BOT_TOKEN}"}, 
        data={"channel": "task_notifications", "text": f"Someone just completed the task {task.title}"}
    )

    db.session.commit()

    return jsonify({"task": task.task_dict()}), 200


@tasks_bp.route("<task_id>/mark_incomplete", methods=["PATCH"])
def mark_task_incomplete(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return jsonify(task), 404
    task.completed_at = None

    db.session.commit()

    return jsonify({"task": task.task_dict()}), 200


@goals_bp.route("", methods=["GET", "POST"])
def handle_goals():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body:
            return jsonify({"details": "Invalid data"}), 400

        new_goal = Goal(title = request_body["title"])

        db.session.add(new_goal)
        db.session.commit()

        return jsonify({"goal": new_goal.goal_dict()}), 201

    elif request.method == "GET":
        request_body = request.get_json()
        goals = Goal.query.all()
        goal_response = [goal.goal_dict() for goal in goals]
        return jsonify(goal_response), 200


@goals_bp.route("/<goal_id>", methods = ["GET", "PUT", "DELETE"])
def handle_one_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return jsonify(goal), 404

    request_body = request.get_json()
    if request.method == "GET":
        return jsonify({"goal": goal.goal_dict()}), 200

    elif request.method == "PUT":
        if "title" not in request_body:
            return jsonify({"details": "Invalid data"}), 400

        goal.title = request_body["title"]
        db.session.commit()
        return jsonify({"goal": goal.goal_dict()}), 200

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return jsonify({'details': f'Goal {goal.goal_id} "{goal.title}" successfully deleted'})


@goals_bp.route("/<goal_id>/tasks", methods=["POST", "GET"])
def handle_goal_and_task(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
            return jsonify(goal), 404

    if request.method=="POST":
        request_body = request.get_json()

        for task_id in request_body["task_ids"]:
            task = Task.query.get(task_id)
            if task is None:
                return jsonify(None), 404
            goal.tasks.append(task)
            db.session.commit()

        task_ids = []
        for task in goal.tasks:
            task_ids.append(task.task_id)

        return jsonify({"id": goal.goal_id, "task_ids": task_ids}), 200

    elif request.method == "GET":
        return jsonify(goal.goal_and_task_dict()), 200
