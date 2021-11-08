from re import T
from flask import Blueprint, json, jsonify, make_response, request, abort
from app import db
from app.models.task import Task
from datetime import datetime
import os
import requests

task_bp = Blueprint("task", __name__,url_prefix="/tasks")


# Helper functions to validate if task_id is integer
def valid_int(number, parameter_type):
    try:
        return int(number)
    except:
        abort(make_response({"error": f"{parameter_type} must be an int"}, 400))

def get_task_from_id(task_id):
    task_id = valid_int(task_id, "task_id")
    return Task.query.get_or_404(task_id, description=f"Task no: {task_id} not found")
    

# Helper function to post in slack
#
def send_slack_msg(task_id):
    task = get_task_from_id(task_id)
    response = requests.post("https://slack.com/api/chat.postMessage",
    {   "token" : os.environ.get("SLACK_BOT_TOKEN"),
        "channel": os.environ.get("SLACK_CHANNEL"),
        "text":f"Someone just completed the task {task.title}"})

    return response

#routes that use GET method
@task_bp.route("", methods=["GET"])
def get_tasks():
    
    sort_query = request.args.get('sort')

    #sorting sorterer
    if sort_query == 'asc':
            tasks = Task.query.order_by(Task.title.asc())
    elif sort_query == 'desc':
            tasks= Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()
            
    task_response=[]

    for task in tasks:
        task_response.append(task.to_dict())

    return jsonify(task_response)

@task_bp.route("/<task_id>", methods=["GET"])
def get_task(task_id):
    task = get_task_from_id(task_id)
    response_body = {"task":task.to_dict()}

    return make_response(jsonify(response_body),200)

#routes that use POST method
@task_bp.route("", methods=["POST"])
def create_task(): 
    form_data = request.get_json()

    if "title" not in form_data or "description" not in form_data or "completed_at" not in form_data:
        response_body = {"details": "Invalid data"}
        return make_response(jsonify(response_body), 400)

    new_task = Task(
        title = form_data["title"],
        description = form_data["description"],
        completed_at=form_data['completed_at'],
    )

    db.session.add(new_task)
    db.session.commit()
    response_body ={"task":new_task.to_dict()}
    return make_response(jsonify(response_body), 201)

#routes that use PATCH or PUT method
@task_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = get_task_from_id(task_id)
    form_data = request.get_json()

    if "title" in form_data:
        task.title = form_data["title"]
    if "description" in form_data:
        task.description = form_data["description"]

    db.session.commit()
    response_body = {"task": task.to_dict()}

    return make_response(jsonify(response_body), 200)

@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):
    task = get_task_from_id(task_id)
    task.completed_at = datetime.now()
    db.session.commit()


    response_body = {
        'task': task.to_dict()
    }
    send_slack_msg(task_id)
    response_body = {"task": task.to_dict()}

    return make_response(jsonify(response_body), 200)

@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(task_id):
    task = get_task_from_id(task_id)

    task.is_complete = False
    task.completed_at = None
    
    db.session.commit()
    response_body = {"task": task.to_dict()}

    return make_response(jsonify(response_body), 200)


#routes that use DELETE method
@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = get_task_from_id(task_id)

    db.session.delete(task)
    db.session.commit()

    response_body = {
        "details": f'Task {task_id} "{task.title}" successfully deleted'
    }
    
    return make_response(jsonify(response_body), 200)
