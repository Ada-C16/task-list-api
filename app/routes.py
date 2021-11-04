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
        response_body = create_details_response("Invalid data")
        return response_body, 400

    new_task = Task(title=request_body["title"], description=request_body["description"], completed_at=request_body["completed_at"])
    db.session.add(new_task)
    db.session.commit()

    response_body = new_task.create_task_response()
    return response_body, 201

# GET /tasks Get a list of all tasks. Handle sort requests via query params.
@tasks_bp.route("", methods = ["GET"])
def get_tasks():
    sort_query = request.args.get("sort")
    title_query = request.args.get("title")

    if sort_query:
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc())

        if sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc())

    elif title_query:
        tasks = Task.query.filter_by(title=title_query)

    else:
        tasks = Task.query.all()

    response_body = jsonify(list_of_tasks(tasks))
    return response_body, 200

# GET /tasks/<task_id>  Get a specific task.
@tasks_bp.route("/<task_id>", methods = ["GET"])
def get_one_task(task_id):
    task = Task.query.get(task_id)
    if not task: 
        return make_response("", 404)

    response_body = task.create_task_response()
    return response_body, 200

# PUT /tasks/<task_id> Update a specific task in the db and return the updated task body.
@tasks_bp.route("/<task_id>", methods = ["PUT"])
def update_one_task(task_id):
    task = Task.query.get(task_id)
    if not task: 
        return make_response("", 404)

    updated_task_information = request.get_json()
    if "title" not in updated_task_information or "description" not in updated_task_information:
        response_body = create_details_response("Invalid data")
        return response_body, 400

    task.title = updated_task_information["title"]
    task.description = updated_task_information["description"]

    db.session.commit()

    response_body = task.create_task_response()
    return response_body, 200

# DELETE /tasks/<task_id>  Delete a specific task and return details of deletion.
@tasks_bp.route("/<task_id>", methods = ["DELETE"])
def delete_one_task(task_id):
    task = Task.query.get(task_id)
    if not task: 
        return make_response("", 404)

    db.session.delete(task)
    db.session.commit()

    response_body = create_details_response(f"Task {task.task_id} \"{task.title}\" successfully deleted")
    return response_body, 200 

# PATCH /tasks/<task_id>/<completion_status> Update completed at date if marked complete; change to None if marked incomplete.
@tasks_bp.route("/<task_id>/<completion_status>", methods = ["PATCH"])
def mark_completion_status(task_id, completion_status):
    task = Task.query.get(task_id)
    if not task: 
        return make_response("", 404)
    
    if completion_status == "mark_complete":
        task.completed_at = datetime.utcnow()
        send_slack_notification_of_task_completion(task)
    
    elif completion_status == "mark_incomplete":
        task.completed_at = None

    db.session.commit()

    response_body = task.create_task_response()
    return response_body, 200

# Post a notification on Slack when a task has been marked as completed.
def send_slack_notification_of_task_completion(task):
    import requests
    import os
    from dotenv import load_dotenv
    load_dotenv()

    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": os.environ.get("SLACK_API_TOKEN")}
    text = f"Someone just completed the task {task.title}"
    data = {"channel": "task-notifications", "text": text}

    requests.post(url=url, params=data, headers=headers)


goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

# POST /goals Create a goal and commit to the db.
@goals_bp.route("", methods = ["POST"])
def post_new_goal():
    request_body = request.get_json()

    if "title" not in request_body:
        response_body = create_details_response("Invalid data")
        return response_body, 400

    new_goal = Goal(title = request_body["title"])
    db.session.add(new_goal)
    db.session.commit()

    response_body = new_goal.create_goal_response()
    return response_body, 201

# GET /goals Get a list of all goals. 
@goals_bp.route("", methods = ["GET"])
def get_goals():
    goals = Goal.query.all()

    response_body = [goal.goal_body() for goal in goals]
    return jsonify(response_body), 200

# GET /goals/<goal_id> Get a specific goal.
@goals_bp.route("/<goal_id>", methods = ["GET"])
def get_one_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal: 
        return make_response("", 404)

    response_body = goal.create_goal_response()
    return response_body, 200

# PUT /goals/<goal_id> Update a specific goal in the db and return the updated goal body.
@goals_bp.route("/<goal_id>", methods = ["PUT"])
def update_one_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal: 
        return make_response("", 404)

    request_body = request.get_json()
    if "title" not in request_body:
        response_body = create_details_response("Invalid data")
        return response_body, 400

    goal.title = request_body["title"]
    db.session.commit()

    response_body = goal.create_goal_response()
    return response_body, 200

# DELETE /goals/<goal_id>  Delete a specific goal and return details of deletion.
@goals_bp.route("/<goal_id>", methods = ["DELETE"])
def delete_one_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal: 
        return make_response("", 404)

    db.session.delete(goal)
    db.session.commit()

    response_body = create_details_response(f"Goal {goal.goal_id} \"{goal.title}\" successfully deleted")
    return response_body, 200 

# POST /goals/<goal_id>/tasks Assign tasks to a specific goal and return the goal body.
@goals_bp.route("/<goal_id>/tasks", methods = ["POST"])
def assign_goal_to_task(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return make_response("", 404)

    request_body = request.get_json()
    if "task_ids" not in request_body:
        response_body = create_details_response("Invalid data")
        return response_body, 400

    task_ids = request_body["task_ids"]
    
    for task_id in task_ids:
        task = Task.query.get(task_id)
        task.goal_id = goal.goal_id

    db.session.commit()
    response_body = dict(id=goal.goal_id, task_ids=task_ids)
    return jsonify(response_body), 200

# GET /goals/<goal_id>/tasks Get a list of tasks assigned to a specific goal.
@goals_bp.route("/<goal_id>/tasks", methods = ["GET"])
def get_tasks_for_specific_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return make_response("", 404)

    tasks = goal.tasks
    tasks_list = list_of_tasks(tasks)
    response_body = dict(id=goal.goal_id, title=goal.title, tasks=tasks_list)
    return jsonify(response_body), 200

## Helper functions ###

# Create response body for details in error message responses.
def create_details_response(details):
    return {"details": details}

# Create list of tasks.
def list_of_tasks(tasks):
    list_of_tasks = [task.task_body() for task in tasks]
    return list_of_tasks
