from requests import auth
from app import db 
from app.models.task import Task
from flask import Blueprint, json, jsonify, make_response, request, abort
import datetime, requests
import os



task_bp = Blueprint("task", __name__, url_prefix="/tasks")

#Helper Functions 
def valid_int(number, parameter_type):
    try:
        int(number)
    except:
        abort(make_response({"error": f"{parameter_type} must be an int"}, 400))


def get_task_from_id(task_id):
    valid_int(task_id, "task_id")
    return Task.query.get_or_404(task_id, description="{task not found}")

#ROUTES
@task_bp.route("", methods=["GET"])
def read_all_tasks():

    title_query = request.args.get("title")
    sort_query = request.args.get("sort")
    sort_id_query =  request.args.get("sort_id")
    
    
    if sort_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    elif sort_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    elif sort_id_query  == "asc":
        tasks = Task.query.order_by(Task.task_id.asc())
    elif sort_id_query  == "desc":
        tasks = Task.query.order_by(Task.task_id.desc())
    elif title_query:
        tasks = Task.query.filter_by(title=title_query)
    else:
        tasks = Task.query.all()

    tasks_response = []
    for task in tasks:
        tasks_response.append(
            task.to_dict()
        )
    return jsonify(tasks_response)


# Create one task 
@task_bp.route("", methods=["POST"])
def create_tasks():
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return {"details": "Invalid data"}, 400

    new_task = Task(
        title=request_body["title"],
        description=request_body["description"],
        completed_at=request_body["completed_at"]
    )

    db.session.add(new_task)
    db.session.commit()

    return make_response({"task":new_task.to_dict()}, 201)



#Get one task with id 
@task_bp.route("/<task_id>", methods=["GET"])
def read_task(task_id):
    task = get_task_from_id(task_id)
    return {"task": task.to_dict()}


#Mark complete on incomplete task
@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete_on_incomplete_task(task_id):

    task = get_task_from_id(task_id)

    task.completed_at = datetime.date.today()
    db.session.commit()

    URL = os.environ.get('URL')
    API_KEY = os.environ.get('KEY')
    params = {"channel":"task-notifications", "text":f"Someone just completed the task {task.title}"}
    header = {'Authorization' : API_KEY}
    
    try: 
        response = requests.post(URL, params=params, headers=header)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return f"Slack API returned error {e}"
     
    return {"task": task.to_dict()}


@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete_on_complete_task(task_id):
    task = get_task_from_id(task_id)

    task.completed_at = None
    db.session.commit()

    return {"task": task.to_dict()}



#UPDATE A TASK
@task_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = get_task_from_id(task_id)
    request_body = request.get_json()

    if "title" in request_body:
        task.title = request_body["title"]
    if "description" in request_body:
        task.description = request_body["description"]
    if "completed_at" in request_body:
        task.completed_at = request_body["completed_at"]
    
    db.session.commit()
    return make_response({"task": task.to_dict()},200)

#DELETE A TASK
@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = get_task_from_id(task_id)

    db.session.delete(task)
    db.session.commit()
    return ({"details": f'Task {task_id} "{task.title}" successfully deleted'})


#OPTIONAL ROUTES

# @task_bp.route("/<task_id>", methods=["GET"])
# def read_task(task_id):
#     task = get_task_from_id(task_id)
#     return {"task": task.to_dict()}



