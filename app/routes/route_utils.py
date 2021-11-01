from flask import abort, jsonify
from app.models.task import Task
from app.models.goal import Goal
import os
import requests


def is_valid_int(number):
    """Check for valid int and abort request with 400 if invalid"""
    try:
        int(number)
    except ValueError:
        abort(400)


def handle_invalid_data():
    return jsonify({"details": "Invalid data"}), 400


def get_task_by_id(id):
    """Grab one task from the database by id and return it"""
    is_valid_int(id)
    return Task.query.get_or_404(id)


def get_goal_by_id(id):
    """Grab one goal from the database by id and return it"""
    is_valid_int(id)
    return Goal.query.get_or_404(id)


def notify_slack_bot(task):
    """Send a post request to the slack api with the name of a specified task"""
    SLACK_API_KEY = os.environ.get("SLACK_API_KEY")

    req_body = {
        "channel": "task-notifications",
        "text": f"Someone just completed the task {task.title}"
    }

    headers = {
        "Authorization": f"Bearer {SLACK_API_KEY}"
    }

    path = "https://slack.com/api/chat.postMessage"

    requests.post(path, json=req_body, headers=headers)
