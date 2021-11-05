from flask import Blueprint, jsonify, request, make_response
from flask.globals import session
from app import db
from app.models.task import Task
from app.models.goal import Goal
from sqlalchemy import asc, desc
from datetime import datetime
import requests
import urllib.parse
from dotenv import load_dotenv
import os 

load_dotenv()

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals",__name__, url_prefix="/goals")

@tasks_bp.route("", methods=["POST","GET"], strict_slashes=False)
def create_task():
    if request.method == "POST":
        request_body = request.get_json()
        if ("title" not in request_body) or ("description" not in request_body) or ("completed_at" not in request_body):
            return {"details": "Invalid data"}, 400
        else:
            new_task = Task(title=request_body['title'], description=request_body['description'], completed_at=request_body['completed_at'])
            db.session.add(new_task)
            db.session.commit()
            if request_body['completed_at'] == None:
                return make_response({"task":new_task.to_dict()}), 201
            else:    
                return make_response({"task":new_task.to_dict()}), 201
    elif request.method == "GET":
        if "sort" in request.args:
            title_sorter = request.args.get("sort")
            if title_sorter == "asc":
                tasks_list = Task.query.order_by(Task.title.asc()).all()
            elif title_sorter == "desc":
                tasks_list = Task.query.order_by(Task.title.desc()).all()
        else:
            tasks_list = Task.query.all()
        response = []
        for my_task in tasks_list:
            response.append(my_task.to_dict())
        return jsonify(response), 200

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"], strict_slashes=False)
def get_task(task_id):
    task_id = int(task_id)
    my_task = Task.query.get(task_id)
    if request.method == "GET":
        if my_task is None:
            return "", 404
        else:
            return make_response({"task":my_task.to_dict()}), 200

    elif request.method == "PUT":
        request_body = request.get_json()
        try:
            my_task.title = request_body["title"]
            my_task.description = request_body["description"]
            if "completed_at" in request_body :
                my_task.completed_at = request_body["completed_at"]
            db.session.commit()        
            return make_response({"task":my_task.to_dict()}), 200
        except AttributeError as ae:
            return make_response("", 404)

    elif request.method == "DELETE":
        if my_task is None:
            return "", 404
        else:        
            db.session.delete(my_task)
            db.session.commit()
            myResponse = 'Task ' + str(task_id) + ' "' + my_task.title + '" successfully deleted'
            return make_response({"details":myResponse}), 200

@tasks_bp.route("/<task_id>/<completed_status>", methods=["PATCH"], strict_slashes=False )
def mark_complete(task_id, completed_status):
    task_id = int(task_id)
    my_task = Task.query.get(task_id)
    if request.method == "PATCH":
        if my_task is None:
            return "", 404
        else:
            if completed_status == "mark_complete":
                my_task.completed_at = datetime.now()
                send_slack_notice(my_task.title)
            elif completed_status == "mark_incomplete":
                my_task.completed_at = None
            db.session.commit() 
            return make_response({"task" : my_task.to_dict()}), 200


def send_slack_notice(this_task_title):
    #here we need to create an http.request to the slack end point
    myNotice = urllib.parse.quote_plus("Someone just completed the task " + this_task_title)
    my_url = "https://slack.com/api/chat.postMessage?channel=task-notifications&text=" + myNotice + "&pretty=1"
    #add a request.header "Authorization", "super secret"
    my_token = os.environ.get("MY_SLACK_TOKEN")
    my_headers = {"Authorization": f"Bearer {my_token}"}
    #send
    r = requests.post(my_url, data="", headers=my_headers)

@goals_bp.route("", methods=["GET", "POST"], strict_slashes=False)
def create_goal():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body:
            return {"details": "Invalid data"}, 400
        else:        
            new_goal = Goal(title=request_body['title'])
            db.session.add(new_goal)
            db.session.commit()
            return make_response({"goal":new_goal.to_dict()}), 201

    if request.method == "GET":
        goals_list = Goal.query.all()
        response = []
        for my_goal in goals_list:
            response.append(my_goal.to_dict())
        
        return jsonify(response), 200

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"], strict_slashes=False)
def get_goal(goal_id):
    goal_id = int(goal_id)
    my_goal = Goal.query.get(goal_id)
    if request.method == "GET":
        if my_goal is None:
            return "", 404
        else:
            return make_response({"goal":my_goal.to_dict()}), 200

    elif request.method == "PUT":
        request_body = request.get_json()
        try:
            my_goal.title = request_body["title"]
            db.session.commit()        
            return make_response({"goal":my_goal.to_dict()}), 200
        except AttributeError as ae:
            return make_response("", 404)

    elif request.method == "DELETE":
        if my_goal is None:
            return "", 404
        else:        
            db.session.delete(my_goal)
            db.session.commit()
            myResponse = 'Goal ' + str(goal_id) + ' "' + my_goal.title + '" successfully deleted'
            return make_response({"details":myResponse}), 200

@goals_bp.route("/<goal_id>/tasks", methods=["GET", "POST"], strict_slashes=False)
def create_task_ids_to_goals(goal_id):
    # goal_id = int(goal_id)
    my_goal = Goal.query.get(goal_id)
    if my_goal is None:
        return "", 404
    request_body = request.get_json()
    if request_body is not None:
        task_ids = request_body['task_ids']
    else:
        task_ids = []

    if request.method == "POST":
        #update all the tasks to point to the goal
        listoftasks = []
        for taskid in task_ids:
            mytask = Task.query.get(taskid)
            mytask.goal_id = goal_id
            listoftasks.append(taskid)
            db.session.commit()             
        #return my_goal.goal_tasks_to_dict, 200
        #Query all the tasks with the goalID
        # create your response here and not in the db.models
        return make_response({"id":int(goal_id), "task_ids":listoftasks}), 200

    if request.method == "GET":
        #set up a list
        listoftasks = []
        #Query all the tasks with the goalID
        mytasks = Task.query.filter(Task.goal_id == goal_id)
        for tasker in mytasks:
            listoftasks.append(tasker.to_dict())          
        #return my_goal.goal_tasks_to_dict, 200
        
        # create your response here and not in the db.models
        return make_response({"id":int(goal_id), "title":my_goal.title, "tasks":listoftasks}), 200

