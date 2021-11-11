from app.models.task import Task
from flask import jsonify
from flask import Blueprint, make_response, request, jsonify, abort
from app import db, SLACK_TOKEN
from datetime import datetime
import requests


#helper functions
task_bp = Blueprint("task", __name__,url_prefix="/tasks")
def valid_int(number, parameter_type):
    try:
        int(number)
    except:
        abort(make_response({"error": f"{parameter_type} must be an int"})), 400

def get_task_from_id(task_id):
    valid_int(task_id, "task_id")
    return Task.query.get_or_404(task_id, description="{task not found}")
# get all tasks

@task_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        
    #write query to fetch all tasks 
        sort_query = request.args.get("sort") ###WAVE 2###

        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc())
        elif sort_query == "desc": 
            tasks = Task.query.order_by(Task.title.desc())
        else:    
            tasks = Task.query.all()    
        tasks_response = [task.to_dict() for task in tasks]
        return jsonify(tasks_response), 200
    
    elif request.method == "POST":
        request_body = request.get_json()
        if not "title" in request_body or not "description" in request_body or not "completed_at" in request_body:
            return jsonify({"details":"Invalid data"}), 400
        new_task = Task(title=request_body["title"], 
                        description=request_body["description"],
                        completed_at=request_body["completed_at"],
            
        )
        
        db.session.add(new_task)
        db.session.commit()
        return jsonify({"task": new_task.to_dict()}), 201 
        
        

@task_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task_id = int(task_id)
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)
    if request.method == "GET":
    
        return jsonify({"task": task.to_dict()}), 200

    elif request.method == "PUT":
        request_body = request.get_json()
            
        task.title = request_body["title"]
        task.description = request_body["description"]
            
        db.session.commit()
        return jsonify({"task": task.to_dict()}), 200
    
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return jsonify({"details":f'Task {task.task_id} "{task.title}" successfully deleted'}), 200

##WAVE 4 Slack Helper Function###   
def post_complete_task_to_slack(task):
    url = "https://slack.com/api/chat.postMessage"
    message = f"Someone just completed the task {task.title}"
    query_params = {
        "token": SLACK_TOKEN,
        "channel": 'task-list-api',
        "text" : message
    }
    return requests.post(url, data=query_params).json()

##wave 3 complete/incomplete##
@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def update_task_completion(task_id):
    task= get_task_from_id(task_id)
    task.is_complete=True
    task.completed_at = datetime.now()
    db.session.commit()
    post_complete_task_to_slack(task)
    return jsonify({"task": task.to_dict()}), 200 


@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def update_task_incomplete(task_id):
    task= get_task_from_id(task_id)
    task.is_complete=False
    task.completed_at = None
    db.session.commit()
    return jsonify({"task": task.to_dict()}), 200 

# @task_bp.route("/<task_id>", methods=["GET"])
# def handle_task(task_id):
#     task_id = int(task_id)
#     task = Task.query.get(task_id)
#     if not task:
#         return make_response(f"Task {task_id} Bad data", 400)
    
    # if request.method == GET

    # for task in tasks:
    #     if task.id == task_id:
    #         return vars(task)

    # return "Not found", 404
