from functools import wraps
from app.models.task import Task
from app.models.goal import Goal
from flask import request, make_response

# Decorator to check if task exists.
def require_valid_task_id(endpoint):
    @wraps(endpoint)
    def fn(*args, task_id, **kwargs):

        task = Task.query.get(task_id)

        if not task: 
            return make_response("", 404)

        return endpoint(*args, task=task, **kwargs)
    return fn

# Decorator to check if goal exists.
def require_valid_goal_id(endpoint):
    @wraps(endpoint)
    def fn(*args, goal_id, **kwargs):

        goal = Goal.query.get(goal_id)

        if not goal: 
            return make_response("", 404)

        return endpoint(*args, goal=goal, **kwargs)
    return fn

# Decorator to check if the request body to create a new goal includes "title".
def require_valid_goal_request_body(endpoint):
    @wraps(endpoint)
    def fn(*args, **kwargs):
        request_body = request.get_json()

        if "title" not in request_body:
            return {"details": "Invalid data"}, 400

        return endpoint(*args, request_body=request_body, **kwargs)

    return fn


# Create response body for details in error message responses.
def create_details_response(details):
    return {"details": details}

# Create list of tasks.
def list_of_tasks(tasks):
    list_of_tasks = [task.task_body() for task in tasks]
    return list_of_tasks


# Post a notification on Slack when a task has been marked as completed.
def send_slack_notification_of_task_completion(task):
    import requests
    import os
    from dotenv import load_dotenv
    load_dotenv()

    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": os.environ.get("SLACK_API_TOKEN")}
    text = f"Someone just completed the task {task.title}"
    data = {"channel": "task-notifications", "text": text}

    requests.post(url=url, params=data, headers=headers)
