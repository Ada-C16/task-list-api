from flask import abort, make_response
import requests, os 
from dotenv import load_dotenv
from app.models.task import Task
from app.models.goal import Goal

# Helper functions
def confirm_valid_id(id, id_type):
    try:
        int(id)
    except:
        abort(make_response({"error": f"{id_type} must be an int"}, 400))

def get_task_from_id(id):
    confirm_valid_id(id, "task_id")
    return Task.query.get_or_404(id)

def get_goal_from_id(id):
    confirm_valid_id(id, "goal_id")
    return Goal.query.get_or_404(id)

def send_completion_slack_message(selected_task):
    load_dotenv()
    token = os.environ.get("SLACK_BOT_TOKEN")
    channel = "task-notifications"
    text = f"Woohoo!! Someone has completed {selected_task.title}!"
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"channel": channel, "text": text}
    response = requests.post(url, headers=headers, params=payload)
    return response