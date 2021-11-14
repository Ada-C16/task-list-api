from app import db
from app.models.task import Task
import requests
from flask import Blueprint, jsonify, request
from sqlalchemy import desc
from datetime import date
import os


tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET"])
def read_tasks():
    sort_query = request.args.get("sort")
    if sort_query:
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title)
        else:
            tasks = Task.query.order_by(desc(Task.title))
    else:
        tasks = Task.query.all()

    tasks_response = [task.to_dict() for task in tasks]

    return jsonify(tasks_response)


@tasks_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()
    try:
        new_task = Task.from_dict(request_body)

        db.session.add(new_task)
        db.session.commit()

        response = {"task": new_task.to_dict()}

        return jsonify(response), 201

    except KeyError:
        return jsonify({"details": "Invalid data"}), 400


@tasks_bp.route("/<id>", methods=["GET"])
def get_one_task(id):
    task = Task.query.get(id)
    if task is None:
        return jsonify(None), 404

    return {"task": task.to_dict()}


@tasks_bp.route("/<id>", methods=["PUT"])
def update_one_task(id):
    task = Task.query.get(id)
    if task is None:
        return jsonify(None), 404

    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()

    response = {"task": task.to_dict()}

    return jsonify(response), 200


@tasks_bp.route("/<id>", methods=["DELETE"])
def delete_one_task(id):
    task = Task.query.get(id)
    if task is None:
        return jsonify(None), 404

    db.session.delete(task)
    db.session.commit()

    response = {'details': f'Task {task.id} "{task.title}" successfully deleted'}

    return jsonify(response), 200


def slack_chat_post_message(task):
    url = "https://slack.com/api/chat.postMessage"
    auth_token = os.environ.get("AUTHORIZATION_TOKEN")
    auth = f"Bearer {auth_token}"
    channel_id = "task-notifications"
    text = f"Someone just completed the task {task.title}"

    requests.post(url, headers=dict(authorization=auth),
        data=dict(channel=channel_id, text=text))


@tasks_bp.route("/<id>/mark_complete", methods=["PATCH"])
def update_task_completed(id):
    task = Task.query.get(id)
    if task is None:
        return jsonify(None), 404

    task.completed_at = date.today()
    db.session.commit()

    response = {"task": task.to_dict()}

    slack_chat_post_message(task)

    return jsonify(response), 200


@tasks_bp.route("/<id>/mark_incomplete", methods=["PATCH"])
def update_task_not_completed(id):
    task = Task.query.get(id)
    if task is None:
        return jsonify(None), 404

    task.completed_at = None
    db.session.commit()

    response = {"task": task.to_dict()}

    return jsonify(response), 200
