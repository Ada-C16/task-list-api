from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request
from datetime import date
from pathlib import Path
import os
from dotenv import load_dotenv
import requests

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
env_path = Path('.')/ '.env'
load_dotenv()


@tasks_bp.route("", methods=["POST", "GET"])
def handle_tasks():
    
    if request.method == "POST":
        request_body = request.get_json()

        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return make_response({"details":"Invalid data"}, 400)

        new_task = Task(
            title=request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"]
        )

        db.session.add(new_task)
        db.session.commit()

        return jsonify({"task": new_task.to_dict()}), 201

    elif request.method == "GET":
        task_response= []
        if request.args.get('sort') == 'asc':
            tasks = Task.query.order_by(Task.title.asc()).all()
        elif request.args.get('sort') == 'desc':
            tasks = Task.query.order_by(Task.title.desc()).all()
        else:
            tasks = Task.query.all()

        for task in tasks:
            task_response.append(task.to_dict())
        return jsonify(task_response), 200

@tasks_bp.route("/<task_id>", methods= ["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    

    if task is None:
        return make_response(f"Task {task_id} not found"), 404
        
    if request.method == "GET":
        return jsonify({"task": task.to_dict()}), 200
        
    elif request.method == "PUT":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body:
            return make_response("invalid request"), 400

        task.title=request_body["title"]
        task.description=request_body["description"]
        

        db.session.commit()
        
        return jsonify({"task": task.to_dict()}),200
        

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
    
        return ({'details': f'Task {task_id} "{task.title}" successfully deleted'}), 200


@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):
    task = Task.query.get(task_id)
    today = date.today()
    if task is None:
        return make_response("", 404)
    else:
        task.completed_at = today
        db.session.commit()
        PATH = 'https://slack.com/api/chat.postMessage'
        params = {"token": os.environ.get("SLACK_TOKEN"),
                    "channel":"task-notifications",
                    "text":f"Someone just completed the task {task.title}"
                    }
        requests.post(PATH,data=params)
        
        
        return jsonify({"task":task.to_dict()}),200