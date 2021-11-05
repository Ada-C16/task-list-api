from app import db
from app.models.task import Task
from flask import Blueprint, jsonify,request, make_response, abort 
from datetime import date
from app.models.goal import Goal
import os
import requests
from dotenv import load_dotenv
# from slack_sdk import WebClient
# from slack_sdk.errors import SlackApiError


def valid_int(number,parameter_type):
    try:
        int(number)
    except:
        abort(make_response({"error":f"{parameter_type} must be an int"},400))

# def slack_notification():
#     load_dotenv()
#     slack_token = os.environ["SLACK_TOKENS"]
#     client = WebClient(token=slack_token)
#     try:
#         response = client.chat_postMessage(
#             channel ="CNEEJDLAW",
#             text = "Task completed"
#         )
#     except SlackApiError as e:
#         return jsonify({"Error": "chanel not found"})
            
tasks_bp = Blueprint("tasks",__name__,url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__,url_prefix="/goals")

@tasks_bp.route("",methods=["GET"])
def handle_tasks():
    sort_query = request.args.get("sort")
    if sort_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    elif sort_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()
    tasks_response =[]
    for task in tasks:
        tasks_response.append(task.to_dict())
    return jsonify(tasks_response),200

@tasks_bp.route("/<task_id>",methods=["GET","put","DELETE"])
def get_task(task_id):
    valid_int(task_id, "task_id")
    task = Task.query.get_or_404(task_id)
    if request.method == "GET":
        return jsonify({"task":task.to_dict()}),200
    elif request.method == "PUT":
        request_body = request.get_json()
        if "title" in request_body:
            task.title = request_body["title"]
        if "description" in request_body:
            task.description = request_body["description"]
        if "completed_at" in request_body:
            task.completed_at = request_body["completed_at"]
        db.session.commit()
        return jsonify({"task":task.to_dict()}),200
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return jsonify({"details":f'Task {task_id} "{task.title}" successfully deleted'}),200

@tasks_bp.route("",methods=["POST"])
def create_task():
    request_body = request.get_json()
    if 'title' not in request_body or 'description' not in request_body or\
    'completed_at' not in request_body:
        return jsonify({'details': "Invalid data"}),400
    
    new_task = Task(
        title=request_body["title"],
        description = request_body["description"],
        completed_at = request_body["completed_at"]
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"task":new_task.to_dict()}),201

@tasks_bp.route("/<task_id>/mark_complete",methods=["PATCH"])
def mark_complete_task(task_id):
    valid_int(task_id, "task_id")
    task = Task.query.get_or_404(task_id)
    task.completed_at = date.today()
    db.session.commit()
    path = "https://slack.com/api/chat.postMessage"
    SLACK_TOKENS = os.environ.get("SLACK_TOKENS")
    query_param = {
        "token":SLACK_TOKENS,
        "channel":"CNEEJDLAW",
        "text": "Task completed"
    }
    requests.post(path,query_param)
    # slack_notification()
    
    return jsonify({"task":task.to_dict()}),200

@tasks_bp.route("/<task_id>/mark_incomplete",methods=["PATCH"])
def mark_incomplete_task(task_id):
    valid_int(task_id, "task_id")
    task = Task.query.get_or_404(task_id)
    task.completed_at = None 
    db.session.commit()
    return jsonify({"task":task.to_dict()}),200     

@goals_bp.route("", methods=["POST"])
def create_goal():
    request_body = request.get_json()
    if "title" not in request_body:
        return jsonify({'details': "Invalid data"}),400
    new_goal = Goal(title = request_body["title"])
    db.session.add(new_goal)
    db.session.commit()
    return jsonify({"goal":new_goal.to_dict()}),201
    
@goals_bp.route("", methods=["GET"])
def handle_goals():
    goals = Goal.query.all()
    goals_response = []
    for goal in goals:
        goals_response.append(goal.to_dict())
    return jsonify(goals_response), 200
        
@goals_bp.route("/<goal_id>", methods=["GET", "PUT","DELETE"])
def get_goal(goal_id):
    valid_int(goal_id,"goal_id")
    goal = Goal.query.get_or_404(goal_id)
    if request.method == "GET":
        return jsonify({"goal":goal.to_dict()}),200
    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return jsonify({"details":f"Goal {goal_id} \"{goal.title}\" successfully deleted"})
    elif request.method == "PUT":
        request_body = request.get_json()
        goal.title = request_body["title"]
        db.session.commit()
        return jsonify({"goal":goal.to_dict()}),200
    
@goals_bp.route("/<goal_id>/tasks", methods=["POST"])
def post_task_ids_to_goal(goal_id):
    valid_int(goal_id,"goal_id")
    request_body = request.get_json()
    goal = Goal.query.get(goal_id)
    task_ids = request_body["task_ids"]
    for task_id in task_ids:
        task = Task.query.get(task_id)
        goal.tasks.append(task)
        db.session.commit()
    return jsonify({"id":goal.id, "task_ids": [task.id for task in goal.tasks]}),200 

@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_for_goal(goal_id):
    valid_int(goal_id,"goal_id")
    goal = Goal.query.get_or_404(goal_id)
    response_body = {"id":goal.id,
        "title":goal.title,
        "tasks":goal.task_lists() 
    }
    print(response_body)
    return jsonify(response_body),200