from datetime import datetime
from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, make_response,request, abort
import requests
from dotenv import load_dotenv
import os

load_dotenv()
task_list_bp = Blueprint("task-list", __name__,url_prefix="/tasks")

# Helper Functions
def valid_int(number):
    try:
        return int(number)     
    except:
        abort(make_response({"error": f"{number} must be an int"}, 400))

def get_task_from_id(task_id):
    task_id = valid_int(task_id)
    return Task.query.get_or_404(task_id, description="{Task not found}")

@task_list_bp.route("",methods=["POST"])
def post_tasks():
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
    

    return {"task": new_task.to_dict()
    }, 201
    

    # return {
    #     "task": {"title":new_task.title,
    #     "description":new_task.description,
    #     "completed_at": new_task.completed_at
    # }
    # }
    # return make_response(f"{new_task.title} is successfully created", 201)

@task_list_bp.route("", methods=["GET"])
def get_tasks():
    sort_query = request.args.get("sort") #get the value of sort from the url
    if sort_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    elif sort_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all() 
    tasks_response = [task.to_dict() for task in tasks]
    return jsonify(tasks_response) 
    

@task_list_bp.route("/<task_id>", methods=["GET"])
def get_one_task(task_id):
    request_task = get_task_from_id(task_id)
    return {"task": 
        request_task.to_dict()
     }

@task_list_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task_with_this_id = get_task_from_id(task_id)
    task_updates = request.get_json()
    if "title" in task_updates:
        task_with_this_id.title = task_updates["title"]
    if "description" in task_updates:
        task_with_this_id.description = task_updates["description"]
    if "completed_at" in task_updates:
        task_with_this_id.completed_at = task_updates["completed_at"]
    
    db.session.commit()
    return {"task":task_with_this_id.to_dict()
    
    }

@task_list_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = get_task_from_id(task_id)
    
    db.session.delete(task)
    db.session.commit()
   
    return {
  "details": f'Task {task_id} "{task.title}" successfully deleted'
    }

@task_list_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def update_to_complete(task_id):  
    task = get_task_from_id(task_id)
    task.completed_at = datetime.timestamp
    print(datetime.timestamp)
    payload = {"channel":"task_notification", "text": f"Someone just completed the task {task.title}"}
    access_key = os.environ.get("SLACK_TOKEN")
    requests.post("https://slack.com/api/chat.postMessage", payload, headers={"Authorization":\
        f"Bearer {access_key}"
        }
    )
    

    return {
         "task" : task.to_complete()
    }

@task_list_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def update_to_incomplete(task_id):
    task = get_task_from_id(task_id)
    task.completed_at = None
    return {"task":task.to_incomplete()}




    
     







