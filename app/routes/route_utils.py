from flask import jsonify
import os
import requests


def handle_invalid_data():
    return jsonify({"details": "Invalid data"}), 400


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
