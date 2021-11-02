from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify, request
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

from tests.test_wave_06 import test_post_task_ids_to_goal

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")


@tasks_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return jsonify({"details": "Invalid data"}), 400

    new_task = Task(title=request_body["title"],
                    description=request_body["description"],
                    completed_at=request_body["completed_at"])

    db.session.add(new_task)
    db.session.commit()

    response_body = {
        "task": {
            "id": new_task.task_id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": new_task.completed_at is not None
        }
    }
    return jsonify(response_body), 201


@tasks_bp.route("", methods=["GET"])
def read_task():

    # tasks hold all the information from the database. Becasue Task is referring to a table. So we are capturing all the records(rows) in the table and holding it in tasks.
    # queries are the records (i.e. rows)
    # creating task_response variable
    title_query = request.args.get("sort")
    if title_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    elif title_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()

    task_responses = []
    for task in tasks:
        task_response = {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at is not None
        }
        if task.goal_id:
            task_response["goal_id"] = task.goal_id
        task_responses.append(task_response)
    return jsonify(task_responses), 200


@tasks_bp.route("/<task_id>", methods=["GET"])
def read_one_task(task_id):
    task = Task.query.get_or_404(task_id)

    task_response = {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.completed_at is not None
    }
    if task.goal_id:
        task_response["goal_id"] = task.goal_id

    response_body = {"task": task_response}

    return jsonify(response_body), 200


@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_one_task(task_id):
    task = Task.query.get_or_404(task_id)

    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()

    response_body = {
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at is not None
        }
    }
    return jsonify(response_body), 200


@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_one_task(task_id):
    task = Task.query.get_or_404(task_id)

    db.session.delete(task)
    db.session.commit()

    return jsonify({
        "details": f"Task {task.task_id} \"{task.title}\" successfully deleted"
    }), 200


def slack_bot(title):
    query_path = {'channel': 'slack_api_test_channel', 'text': title}
    header = {'Authorization': os.environ.get('BOT')}
    response = requests.post(
        'https://slack.com/api/chat.postMessage', params=query_path, headers=header)
    return response.json()


@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed_at = datetime.utcnow()

    db.session.commit()

    slack_bot(task.title)

    response_body = {
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at is not None
        }
    }
    return jsonify(response_body), 200


@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed_at = None

    db.session.commit()

    response_body = {
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at is not None
        }
    }
    return jsonify(response_body), 200


@goals_bp.route("", methods=["POST"])
def create_goal():
    request_body = request.get_json()

    if "title" not in request_body:
        return jsonify({"details": "Invalid data"}), 400

    new_goal = Goal(title=request_body["title"])

    db.session.add(new_goal)
    db.session.commit()

    response_body = {
        "goal": {
            "id": new_goal.goal_id,
            "title": new_goal.title
        }
    }
    return jsonify(response_body), 201


@goals_bp.route("", methods=["GET"])
def read_goal():

    goals = Goal.query.all()

    goal_responses = []
    for goal in goals:
        goal_responses.append({
            "id": goal.goal_id,
            "title": goal.title
        })

    return jsonify(goal_responses), 200


@goals_bp.route("/<goal_id>", methods=["GET"])
def read_one_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    response_body = {
        "goal": {
            "id": goal.goal_id,
            "title": goal.title
        }
    }
    return jsonify(response_body), 200


@goals_bp.route("/<goal_id>", methods=["PUT"])
def update_one_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    request_body = request.get_json()

    goal.title = request_body["title"]

    db.session.commit()

    response_body = {
        "goal": {
            "id": goal.goal_id,
            "title": goal.title,
        }
    }
    return jsonify(response_body), 200


@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_one_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    db.session.delete(goal)
    db.session.commit()

    return jsonify({
        "details": f"Goal {goal.goal_id} \"{goal.title}\" successfully deleted"
    }), 200


@goals_bp.route("/<goal_id>/tasks", methods=["POST"])
def post_tasks_to_goal(goal_id):
    request_body = request.get_json()

    if "task_ids" not in request_body:
        return jsonify({"details": "Invalid data"}), 400

    task_ids = request_body["task_ids"]
    for task_id in task_ids:
        task = Task.query.get_or_404(task_id)
        task.goal_id = goal_id

    db.session.commit()

    response_body = {
        "id": int(goal_id),
        "task_ids": task_ids
    }
    return jsonify(response_body), 200


@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_for_a_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    tasks_response = []
    for task in goal.tasks:
        tasks_response.append(
            {
                "id": task.task_id,
                "goal_id": goal.goal_id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.completed_at is not None
            }
        )

    response_body = {
        "id": goal.goal_id,
        "title": goal.title,
        "tasks": tasks_response
    }
    return jsonify(response_body), 200
