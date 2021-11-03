from flask import Blueprint, json, jsonify, request
from .models.task import Task
from .models.goal import Goal
from app import db
from datetime import datetime
import requests
from dotenv import load_dotenv
import os
from .models.messages import *
import json
import pprint
import slack

load_dotenv()

slack_url_prefix = "https://slack.com/api/"

task_notifications_channel = "C02K5T92807"

slack_api_key = os.environ.get("SLACK_API_KEY")

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")
slack_bp = Blueprint("slack", __name__, url_prefix="/slack")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():

    if request.method == "POST":
        request_body = request.get_json()

        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return invalid_data_message()

        new_task = Task(
            title=request_body["title"],
            description=request_body["description"],
            completed_at = datetime.today() if request_body["completed_at"] else None
            )
        
        db.session.add(new_task)
        db.session.commit()

        return success_message(new_task, 201)

    elif request.method == "GET":

        sort_order = request.args.get("sort")

        if not sort_order:

            tasks = Task.query.all()

        elif sort_order == 'asc':

            tasks = Task.query.order_by(Task.title)

        elif sort_order == 'desc':

            tasks = Task.query.order_by(Task.title.desc())

        return jsonify([task.to_dict() for task in tasks])

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):

    id_error = validate_id(Task, task_id)
    if id_error:
        return id_error

    task = Task.query.get(task_id)

    if request.method == "GET":

        return success_message(task, 200)

    elif request.method == "DELETE":

        db.session.delete(task)

        db.session.commit()

        return jsonify({
            "details": f'Task {task_id} "{task.title}" successfully deleted'
        }), 200

    elif request.method == "PUT":
        
        request_body = request.get_json()

        if "title" not in request_body or "description" not in request_body:
            return invalid_data_message()

        task.title = request_body["title"]
        task.description = request_body["description"]

        if "completed_at" in request_body:
            task.completed_at = datetime.today()

        db.session.commit()

        return success_message(task, 200)

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_task_complete(task_id):
    
    id_error = validate_id(Task, task_id)
    if id_error:
        return id_error

    task = Task.query.get(task_id)

    task.completed_at = datetime.today()

    db.session.commit()

    # notify via slack
    # set headers
    headers = {
        "Authorization" : f"Bearer {slack_api_key}"
    }

    params = {
        "channel" : task_notifications_channel,
        "text" : f"Someone just completed the task {task.title}"
    }

    slack_api_action = "chat.postMessage"

    url = slack_url_prefix + slack_api_action

    try:
        response = requests.post(url, params=params, headers=headers)
        r_json = response.json()
        if not r_json["ok"]:
            return invalid_data_message()
    except requests.exceptions.RequestException as e:
        return "Something went wrong when posting a message to Slack.", 404

    return success_message(task, 200)

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def handle_task_incomplete(task_id):
    
    id_error = validate_id(Task, task_id)
    if id_error:
        return id_error

    task = Task.query.get(task_id)

    task.completed_at = None

    db.session.commit()

    return success_message(task, 200)

@goals_bp.route("", methods=["GET", "POST"])
def handle_goals():

    if request.method == "POST":

        request_body = request.get_json()

        if "title" not in request_body:
            return invalid_data_message()
        
        new_goal = Goal(title=request_body["title"])

        db.session.add(new_goal)
        db.session.commit()

        return success_message(new_goal, 201)

    elif request.method == "GET":
        
        goals = Goal.query.all()

        return jsonify([goal.to_dict() for goal in goals])

@goals_bp.route("/<goal_id>", methods=["DELETE", "PUT", "GET"])
def handle_goal(goal_id):

    id_error = validate_id(Goal, goal_id)

    if id_error:
        return id_error

    goal = Goal.query.get(goal_id)

    if request.method == "GET":

        return success_message(goal, 200)

    elif request.method == "PUT":

        request_body = request.get_json()

        if "title" not in request_body:
            return invalid_data_message

        goal.title = request_body["title"]

        db.session.commit()

        return success_message(goal, 200)

    elif request.method == "DELETE":

        db.session.delete(goal)
        db.session.commit()

        return jsonify({ "details" : f'Goal {goal_id} "{goal.title}" successfully deleted'})

@goals_bp.route("/<goal_id>/tasks", methods=["GET", "POST"])
def handle_goal_tasks(goal_id):

    id_error = validate_id(Goal, goal_id)

    if id_error:
        return id_error

    if request.method == "GET":

        goal = Goal.query.get(goal_id)

        return jsonify(goal.to_dict_with_relationship())

    elif request.method == "POST":
        
        request_body = request.get_json()

        if "task_ids" not in request_body:
            return invalid_data_message()

        for task_id in request_body["task_ids"]:
            task = Task.query.get(task_id)
            task.goal_id = goal_id
            db.session.commit()

        return {
            "id": int(goal_id),
            "task_ids": request_body["task_ids"]
        }, 200

# respond to /task command in slack
@slack_bp.route("/tasks", methods=["POST"])
def handle_slack_task():
    
    data = request.form
    print(data)

    command = data.get("command")
    print("Command is", command)

    if command == '/task':

        return create_item_slash_command(Task, data)
    
    elif command == '/see-tasks':

        filter = data.get("text")

        return get_items_slash_command(Task, data, filter=filter)


#respond to /goal command in slack
@slack_bp.route("/goals", methods=["POST"])
def handle_slack_goal():

    data = request.form
    print(data)

    command = data.get("command")
    print("Command is", command)

    if command == '/goal':

        return create_item_slash_command(Goal, data)
    
    elif command == '/see-goals':

        return get_items_slash_command(Goal, data)

@slack_bp.route("/mark_task", methods=["POST"])
def handle_slack_mark_task():

    data = request.form
    payload_dict = json.loads(data['payload'])
    task_id = int(payload_dict["actions"][0]["value"])
    channel_id = payload_dict["container"]["channel_id"]
    
    #print(json.dumps(payload_dict["actions"], indent=4))

    task = Task.query.get(task_id)

    if task.completed_at:
        task.completed_at = None
        completion_status = "incomplete"
    else:
        task.completed_at = datetime.today()
        completion_status = "complete"

    db.session.commit()

    text = f"The task *{task.title}* has been marked {completion_status}."
    
    client = slack.WebClient(token=slack_api_key)
    client.chat_postMessage(channel=channel_id, text=text)

    return "", 200