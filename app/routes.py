from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify, make_response, request
from sqlalchemy import asc, desc
from datetime import datetime, timezone
import requests
import os

SLACK_POST_MESSAGE_URL = 'https://slack.com/api/chat.postMessage'
SLACK_POST_MESSAGE_CHANNEL = '#task-list'
SLACK_BOT_TOKEN = os.environ.get('SLACK_TOKEN')
SLACK_BOT_USERNAME = 'Waebot'

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

def make_input_valid(number):
    try:
        int(number)
    except:
        return make_response(f"{number} is not an int!", 400)

def is_parameter_valid(parameter_id, mdl=Task):
    if make_input_valid(parameter_id) is not None:
        return make_input_valid(parameter_id)
    elif mdl.query.get(parameter_id) is None:
        return make_response(f"{parameter_id} is not a valid id!", 404)

def model_select(url):
    if "goals" in url:
        mdl = Goal
    else:
        mdl = Task
    return mdl

@goals_bp.route("",methods=["POST"])
@tasks_bp.route("", methods=["POST"])
def post_tasks():
    request_body = request.get_json()
    mdl = model_select(request.url)
    if mdl == Task:
        try: new_obj = Task(title=request_body["title"],
                description=request_body["description"],
                completed_at=request_body["completed_at"])
        except KeyError: return ({"details":"Invalid data"},400)
    if mdl == Goal:
        try: new_obj = Goal(title=request_body["title"])
        except KeyError: return ({"details":"Invalid data"},400)
    db.session.add(new_obj)
    db.session.commit()
    response_body = mdl.make_dict_response(new_obj, 201)
    return response_body

@goals_bp.route("<goal_id>/tasks", methods=["POST"])
def create_tasks_with_goals(goal_id):
    invalid_param = is_parameter_valid(goal_id, Goal)
    if invalid_param:
        return make_response(invalid_param)
    goal = Goal.query.get(goal_id)

    request_body = request.get_json()
    task_ids_list = []
    try: 
        for task_id in request_body["task_ids"]:
            task = Task.query.get(task_id)
            task.goal = goal
            task_ids_list.append(task.task_id)
            db.session.add(task)
    except KeyError: return ({"details":"Invalid data"},400)
    db.session.commit()
    response_body = {
        "id":int(goal_id),
        "task_ids": task_ids_list
    }
    return response_body

@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def read_goal_tasks(goal_id):
    invalid_param = is_parameter_valid(goal_id, Goal)
    if invalid_param:
        return invalid_param
    goal = Goal.query.get(goal_id)
    goal_tasks_response = []

    for task in goal.tasks:
        goal_tasks_response.append(
        {
            "id": task.task_id,
            "goal_id": task.goal_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete(),
        })

    return (jsonify({"id": int(goal_id), "title": goal.title, "tasks": goal_tasks_response}), 200)

@goals_bp.route("/<goal_id>",methods=["PUT"])
@tasks_bp.route("/<task_id>", methods=["PUT"])
def put_tasks(task_id=None, goal_id=None):
    if task_id:
        obj_id = task_id
    if goal_id:
        obj_id = goal_id
    mdl = model_select(request.url)
    invalid_param = is_parameter_valid(obj_id, mdl)
    if invalid_param:
        return make_response(invalid_param)
    model = mdl.query.get(obj_id)
    form_data = request.get_json()
    if form_data.get("title"):
        model.title = form_data["title"]
    if form_data.get("description"):
        model.description = form_data["description"]
    if form_data.get("completed_at"):
        model.completed_at = form_data["completed_at"]
    db.session.commit()
    response_body = mdl.make_dict_response(model, 200)
    return response_body

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_parameter_complete(task_id):
    invalid_param = is_parameter_valid(task_id, Task)
    if invalid_param:
        return make_response(invalid_param)
    text = "Someone just completed the task My Beautiful Task"

    response = requests.post(SLACK_POST_MESSAGE_URL, {
        'token': SLACK_BOT_TOKEN,
        'channel': SLACK_POST_MESSAGE_CHANNEL,
        'text': text,
        'username': SLACK_BOT_USERNAME,})
    
    task = Task.query.get(task_id)
    task.completed_at = datetime.now(timezone.utc)
    db.session.commit()
    print(response.text)
    return task.make_dict_response(200)

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_parameter_incomplete(task_id):
    invalid_param = is_parameter_valid(task_id, Task)
    if invalid_param:
        return make_response(invalid_param)
    task = Task.query.get(task_id)
    task.completed_at = None
    db.session.commit()
    return task.make_dict_response(200)

@goals_bp.route("",methods=["GET"])
@tasks_bp.route("",methods=["GET"])
def get_all_tasks_or_goals():
    mdl = model_select(request.url)
    sort_query = request.args.get("sort")
    if sort_query:
        if "asc" in sort_query:
            models = mdl.query.order_by(mdl.title).all()
        if "desc" in sort_query:
            models = mdl.query.order_by(mdl.title.desc()).all()
    else:
        models = mdl.query.all()
    models_response = []

    for mdl in models:
        try: 
            models_response.append({
        "id": mdl.get_id(),
        "title": mdl.title,
        "description": mdl.description,
        "is_complete": mdl.is_complete(),
        })
        except AttributeError:
            models_response.append({
        "id": mdl.get_id(),
        "title": mdl.title,
        })
    return (jsonify(models_response), 200)

@goals_bp.route("/<goal_id>", methods=["GET"])
@tasks_bp.route("/<task_id>", methods=["GET"])
def get_one_task_or_goal(task_id=None, goal_id=None):
    if task_id:
        invalid_param = is_parameter_valid(task_id, Task)
        if invalid_param:
            return make_response(invalid_param)
        obj = Task.query.get(task_id)
        if obj.goal_id:
            return {"task":{
            "id": obj.task_id,
            "goal_id": obj.goal_id,
            "title": obj.title,
            "description": obj.description,
            "is_complete": obj.is_complete(),
        }}

    if goal_id:
        invalid_param = is_parameter_valid(goal_id, Goal)
        if invalid_param:
            return invalid_param
        obj = Goal.query.get(goal_id)
    return obj.make_dict_response(200)

@goals_bp.route("/<goal_id>",methods=["DELETE"])
@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id=None, goal_id=None):
    if task_id:
        obj_id = task_id
        obj_str = "Task"
    if goal_id:
        obj_id = goal_id
        obj_str = "Goal"
    mdl = model_select(request.url)
    invalid_param = is_parameter_valid(obj_id, mdl)
    if invalid_param:
        return invalid_param
    obj = mdl.query.get(obj_id)
    db.session.delete(obj)
    db.session.commit()

    response_body = ({'details' : f'{obj_str} {obj.get_id()} "{obj.title}" successfully deleted'})
    return make_response(response_body, 200)