from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request
from datetime import datetime, timezone
import os
from slack import WebClient
from slack.errors import SlackApiError

#create the blueprint for the endpoints
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


#Create a Task: Valid Task With null completed_at
@tasks_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return make_response({"details": "Invalid data"}, 400)
    
    if request_body["completed_at"] is not None:
        new_task = Task(title=request_body["title"],
                    description=request_body["description"],
                    completed_at=request_body["completed_at"])
    else:
        new_task = Task(title=request_body["title"],
                    description=request_body["description"],
                    completed_at = None)

    db.session.add(new_task)
    db.session.commit()

    response = {}
    task = {}
    task['id'] = new_task.task_id
    task['title'] = request_body["title"]
    task['description'] = request_body["description"]
    if request_body["completed_at"] is not None:
        task['is_complete'] = True
    else:
        task['is_complete'] = False
    response['task'] = task
    print(response)

    return make_response(response, 201)

#Get Tasks: Getting Saved Tasks
@tasks_bp.route("", methods=["GET"])
def get_tasks():

    sort_query = request.args.get("sort")
    if(sort_query == "asc"):
        tasks = Task.query.order_by(Task.title).all()
    elif(sort_query == "desc"):
        tasks = Task.query.order_by(Task.title.desc()).all()
    else:
        tasks = Task.query.all()
    
    response = []

    for task in tasks:
        task_dict = {}
        task_dict["id"] = task.task_id
        task_dict["title"] = task.title
        task_dict["description"] = task.description
        
        if task.completed_at is not None:
            task_dict["is_complete"] = True
        else:
            task_dict["is_complete"] = False

        response.append(task_dict)

    return jsonify(response)

#Get a Task
@tasks_bp.route("/<task_id>", methods=["GET"])
def get_task(task_id):
    task = Task.query.get(task_id)
    
    if task is None:
        return make_response("Not Found", 404)
    
    response = {}
    task_dict = {}

    task_dict["id"] = task.task_id
    task_dict["title"] = task.title
    task_dict["description"] = task.description
    
    if task.completed_at is not None:
        task_dict["is_complete"] = True
    else:
        task_dict["is_complete"] = False
    
    response["task"] = task_dict
    return response

#Update One Task
@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = Task.query.get(task_id)
    
    if task is None:
        return make_response(f"Task {task_id} not found", 404)
    
    form_data = request.get_json()
    task.title = form_data["title"]
    task.description = form_data["description"]
    #task.completed_at = form_data["completed_at"]

    db.session.commit()
    
    response = {}
    task_dict = {}

    task_dict["id"] = task.task_id
    task_dict["title"] = task.title
    task_dict["description"] = task.description

    if task.completed_at is not None:
        task_dict["is_complete"] = True
    else:
        task_dict["is_complete"] = False

    response["task"] = task_dict
    return make_response(response, 200)
    #return make_response(f"Task #{task.task_id} successfully updated")




# Delete One Task
@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    
    if task is None:
        return make_response(f"Task {task_id} not found", 404)

    response = {"details": f'Task {task.task_id} "{task.title}" successfully deleted' }
    db.session.delete(task)
    db.session.commit()

    return make_response(response, 200)


        
@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):

    # #
    slack_token = os.environ["SLACK_API_TOKEN"]
    client = WebClient(token=slack_token)
    # #

    task = Task.query.get(task_id)
    if task is None:
        return make_response("Not Found", 404)

    #first get the task
    response_json = {}
    task_dict = {} 

    #check the competion of the task
    # if task.completed_at is None:
    #     #update it 
    task.completed_at = datetime.now(timezone.utc)
    db.session.commit()
    task_dict["is_complete"]= True 

    task_dict["id"]= task.task_id
    task_dict["title"]= task.title
    task_dict["description"]= task.description
    
    response_json["task"] = task_dict

    print(task.completed_at)

    # 
    try:
        response = client.chat_postMessage(
            channel="task-notifications",
            text=f"Someone just completed the task {task_dict['title']} :tada:")
    
    except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    # 
    return make_response(response_json, 200)

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("Not Found", 404)

    response = {}
    task_dict = {} 

    # if task.completed_at is not None:
    task.completed_at = None
    
    task_dict["id"]= task.task_id
    task_dict["title"]= task.title
    task_dict["description"]= task.description
    task_dict["is_complete"]= False
    
    response["task"] = task_dict

    print(task.completed_at)

    return make_response(response, 200)

# @tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
# def mark_complete_on_complete_task(task_id):
#     #first get the task
#     task = Task.query.get(task_id)
#     response = {}
#     task_dict = {} 

#     #check the competion of the task
#     #update it 
#     task.completed_at = datetime.now(timezone.utc)
#     task_dict["is_complete"]= True 

#     task_dict["id"]= task.task_id
#     task_dict["title"]= task.title
#     task_dict["description"]= task.description
    
#     response["task"] = task_dict

#     print(task.completed_at)

#     return make_response(response, 200)