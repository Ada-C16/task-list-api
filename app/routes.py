import requests
from app import db
from flask import Blueprint, jsonify, request, make_response
from app.models.task import Task
from datetime import datetime
import os


tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST", "GET"])
def handle_tasks():
    # POST REQUESTS
    if request.method == "POST":

        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            
            return jsonify({"details": "Invalid data"}), 400

        new_task = Task(
            title = request_body["title"],
            description = request_body["description"],
            completed_at = request_body["completed_at"]
        )

        db.session.add(new_task)
        db.session.commit()

        new_task_response = { 
            "task":
        {
            "id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": new_task.completed_at is not None
        }
        }

        return jsonify(new_task_response), 201

    # GET REQUESTS
    elif request.method == "GET":
        title_query = request.args.get("title")
        description_query = request.args.get("description")
        if title_query:
            tasks = Task.query.filter(Task.title.contains(title_query))
        elif description_query:
            tasks = Task.query.filter(Task.description.contains(description_query))
        else:
            tasks = Task.query.all()

        # QUERY PARAMS (Ascending and Descending Order by Title)
        sort_query = request.args.get("sort")
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc())
        elif sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc()) 
        else:
            tasks = Task.query.all()

        task_response = []
        for task in tasks:
            task_response.append(
            {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": task.completed_at is not None
                }
            )

        if task_response == []:
            return jsonify(task_response), 200

        return jsonify(task_response), 200

# GET, PUT, DELETE ONE AT A TIME
@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_one_task_at_a_time(task_id):
    if request.method == "GET":
        task = Task.query.get(task_id)
        if task is None:
            return jsonify(None), 404
        else:
            return {
                "task":{
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.completed_at is not None
                }
            }, 200

    elif request.method == "PUT":
        task = Task.query.get(task_id)
        if task is None:
            return jsonify(None), 404
    
        request_body = request.get_json()

        task.title = request_body["title"]
        task.description = request_body["description"]

        db.session.commit()

        updated_task_response = {
            "task":{
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.completed_at is not None
            }
        }

        return jsonify(updated_task_response), 200

    elif request.method == "DELETE":
        task = Task.query.get(task_id)
        if task is None:
            return jsonify(None), 404
    
        db.session.delete(task)
        db.session.commit()

        delete_response = {"details": (f'Task {task_id} "{task.title}" successfully deleted')}

        return jsonify(delete_response), 200

# PATCH REQUESTS as either complete or not complete
# endpoints are expressed w/out carrots for search specificity
@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_tasks_complete(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return jsonify(None), 404

    # setting the completed_at with a datetime
    task.completed_at = datetime.utcnow()
    db.session.commit()

    # Send Slack Message Using Slack API
    slack_url = "https://slack.com/api/chat.postMessage"
    bearer_token = os.environ.get("BEARER_TOKEN")
    slack_channel = 'slack-api-test-channel'
    text = f'Someone just completed the task {task.title}'
    slack_user_name = "Starseed's Bot"
    
    requests.patch(slack_url, data={
        'token': bearer_token,
        'channel': slack_channel,
        'text': text,
        'username': slack_user_name,}).json()

    updated_task_response =  {
            "task":   {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.completed_at is not None
                }
            }
    
    return jsonify(updated_task_response), 200

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def handle_tasks_not_complete(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return jsonify(None), 404

    
    # setting the completed_at to None
    task.completed_at = None
    db.session.commit()

    updated_task_response =  {
            "task":   {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.completed_at is not None
            }
        }
    return jsonify(updated_task_response), 200




