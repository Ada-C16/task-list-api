from datetime import datetime
from operator import truediv
from flask import Blueprint, json, jsonify, request, make_response
from flask_sqlalchemy import _make_table
from app import db
from app.models.task import Task
from app.models.goal import Goal

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

# POST /tasks Create a new task to the db and return the task body.
@tasks_bp.route("", methods = ["POST"])
def post_new_task():
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        response_body = create_details("Invalid data")
        return response_body, 400

    new_task = Task(title=request_body["title"], description=request_body["description"], completed_at=request_body["completed_at"])
    db.session.add(new_task)
    db.session.commit()

    response_body = create_task_body(new_task)
    return response_body, 201

# GET /tasks Get a list of all tasks. Handle sort requests via query params.
@tasks_bp.route("", methods = ["GET"])
def get_tasks():
    sort_query = request.args.get("sort")

    if sort_query:
    
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc())

        if sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()

    response_body = list_of_tasks(tasks)
    return response_body, 200

# GET /tasks/<task_id>  Get a specific task.
@tasks_bp.route("/<task_id>", methods = ["GET"])
def get_one_task(task_id):
    task = Task.query.get(task_id)
    if not task: 
        return make_response("", 404)

    if task.goal_id:
        response_body = create_task_body_goal(task)
    else:    
        response_body = create_task_body(task)
    return response_body, 200

# PUT /tasks/<task_id> Update a specific task in the db and return the updated task body.
@tasks_bp.route("/<task_id>", methods = ["PUT"])
def update_one_task(task_id):
    task = Task.query.get(task_id)
    if not task: 
        return make_response("", 404)

    updated_task_information = request.get_json()
    task.title = updated_task_information["title"]
    task.description = updated_task_information["description"]

    db.session.commit()

    response_body = create_task_body(task)
    return response_body, 200

# DELETE /tasks/<task_id>  Delete a specific task and return details of deletion.
@tasks_bp.route("/<task_id>", methods = ["DELETE"])
def delete_one_task(task_id):
    task = Task.query.get(task_id)
    if not task: 
        return make_response("", 404)

    db.session.delete(task)
    db.session.commit()

    response_body = create_details(f"Task {task.task_id} \"{task.title}\" successfully deleted")
    return response_body, 200 

# PATCH /tasks/<task_id>/<completion_status> Update completed at date if marked complete; change to None if marked incomplete.
@tasks_bp.route("/<task_id>/<completion_status>", methods = ["PATCH"])
def mark_completion_status(task_id, completion_status):
    task = Task.query.get(task_id)
    if not task: 
        return make_response("", 404)
    
    if completion_status == "mark_complete":
        task.completed_at = datetime.utcnow()
        send_slack_notification(task)
    
    elif completion_status == "mark_incomplete":
        task.completed_at = None

    db.session.commit()

    response_body = create_task_body(task)
    return response_body, 200

# Post a notification on Slack when a task has been marked as completed.
def send_slack_notification(task):
    import requests
    import os
    from dotenv import load_dotenv
    load_dotenv()

    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": os.environ.get("SLACK_API_TOKEN")}
    text = f"Someone just completed the task {task.title}"
    data = {"channel": "task-notifications", "text": text}

    requests.post(url=url, params=data, headers=headers)

### Helper functions TASKS###

def is_complete(task):
    is_complete = task.completed_at

    if not task.completed_at:
        is_complete = False

    else:
        is_complete = True

    return is_complete

def create_task_body(task):
    task_body = {"task": {
    "id": task.task_id,
    "title": task.title,
    "description": task.description,
    "is_complete": is_complete(task)
    }}
    return task_body

def create_task_body_goal(task):
    task_body = {"task": {
    "id": task.task_id,
    "goal_id": task.goal_id,
    "title": task.title,
    "description": task.description,
    "is_complete": is_complete(task)
    }}
    return task_body

def create_details(details):
    
    response = {"details": details}
    
    return response

def list_of_tasks(tasks):
        
    list_of_tasks = []
        
    for task in tasks:
        list_of_tasks.append(dict(id=task.task_id, title=task.title, description=task.description, is_complete=is_complete(task)))

    return jsonify(list_of_tasks)


# ### GOALS ####

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@goals_bp.route("", methods = ["POST", "GET"])
def handle_goals():
    
    if request.method == "POST":
        request_body = request.get_json()

        if "title" not in request_body:
            return jsonify(create_details("Invalid data")), 400

        new_goal = Goal(title = request_body["title"])
        db.session.add(new_goal)
        db.session.commit()

        response_body = create_goal_body(new_goal)

        return jsonify(response_body), 201
    
    elif request.method == "GET":
        goals = Goal.query.all()
        return jsonify_list_of_goals(goals), 200

@goals_bp.route("/<goal_id>", methods = ["GET", "PUT", "DELETE"])
def handle_one_goal(goal_id):

    goal = Goal.query.get(goal_id)

    if not goal: 
        return make_response("", 404)

    if request.method == "GET":
        response_body = create_goal_body(goal)
        return jsonify(response_body), 200

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()

        return jsonify(create_details(f"Goal {goal.goal_id} \"{goal.title}\" successfully deleted"
        )), 200 

    elif request.method == "PUT":
        response_body = request.get_json()
        goal.title = response_body["title"]
        db.session.commit()

        response_body = create_goal_body(goal)
        return jsonify(response_body), 200

@goals_bp.route("/<goal_id>/tasks", methods = ["POST", "GET"])
def handle_goal_and_task_relationship(goal_id):

    goal = Goal.query.get(goal_id)

    if request.method == "GET":
        if not goal:
            return make_response("", 404)

        else:
            tasks = goal.tasks
            list_of_tasks = list_tasks_goals(tasks)
            response_body = dict(id=goal.goal_id, title=goal.title, tasks=list_of_tasks)
            return jsonify (response_body), 200

    elif request.method == "POST":
        request_body = request.get_json()
        task_ids = request_body["task_ids"]
        for task_id in task_ids:
            task = Task.query.get(task_id)
            task.goal_id = goal.goal_id

        db.session.commit()
        response_body = dict(id=goal.goal_id, task_ids=task_ids)
        return jsonify(response_body)


## Helper functions GOALS ###

def create_goal_body(goal):
    goal_body = {"goal": {
    "id": goal.goal_id,
    "title": goal.title,
    }}
    return goal_body

def jsonify_list_of_goals(goals):
        
    list_of_goals = []
        
    for goal in goals:
        list_of_goals.append(dict(id=goal.goal_id, title=goal.title))

    return jsonify(list_of_goals)

def list_tasks_goals(tasks):

    list_of_tasks = []

    if tasks:        
        for task in tasks:
            list_of_tasks.append(dict(id=task.task_id, goal_id=task.goal_id, title=task.title, description=task.description, is_complete=is_complete(task)))

    return list_of_tasks