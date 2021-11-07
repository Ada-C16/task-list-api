from flask import Blueprint, jsonify, make_response, request
from app.models.task import Task 
from app.models.goal import Goal
from app import db
from datetime import date
import requests
import os
from dotenv import load_dotenv

load_dotenv()

task_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goal_bp", __name__, url_prefix="/goals")

@task_bp.route("", methods=["GET", "POST"])
def handle_all_tasks():
    tasks_response = []
    
    #WV2: Get Tasks Asc, Get Tasks Desc
    if request.method == "GET":
        if request.args.get('sort') == 'asc':
            tasks = Task.query.order_by(Task.title.asc()).all()
        elif request.args.get('sort') == 'desc':
            tasks = Task.query.order_by(Task.title.desc()).all()

        #WV1: No Saved Tasks, One Saved Tasks
        else:
            tasks = Task.query.all()     
        for task in tasks:
            tasks_response.append(task.to_dict())
        return jsonify(tasks_response), 200 

    #WV1: Create Task With None Completed_At, Create Task - Title, Create Task - Description, Create Task - Completed_At
    #WV3: Create Task Wtih Valid Completed_At
    if request.method == "POST":
        request_body = request.get_json()
        try:
            new_task = Task(title = request_body["title"], 
                            description = request_body["description"],
                            completed_at = request_body["completed_at"])
        except KeyError:
            return ({'details': 'Invalid data'}, 400)        
        db.session.add(new_task)
        db.session.commit()
        return jsonify({"task":new_task.to_dict()}), 201

@task_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_single_task(task_id):
    task_id = int(task_id)
    task = Task.query.get(task_id)

    #WV1: Get Task, Get Task Not Found
    if request.method == "GET":
        if task is None:
            return make_response("", 404)
        return jsonify({"task": task.to_dict()}), 200 

    #WV1: Update Task, Update Task Not Found
    #WV3: Update Task With Valid Completed At
    elif request.method == "PUT":
        input_data = request.get_json()
        if task is None:
            return make_response("", 404)
        task.title = input_data["title"]
        task.description = input_data["description"]
        db.session.commit()
        return ({"task":task.to_dict()}), 200

    #WV1: Delete Task, Delete Task Not Found
    elif request.method == "DELETE":
        if task is None:
            return make_response("", 404)
        else:
            db.session.delete(task)
            db.session.commit()
            return ({'details': f'Task {task_id} "{task.title}" successfully deleted'}), 200

#WV3: Mark Comp on Incom, Mark Incom on Comp, Mark Comp on Comp, Marck Comp on Missing, Mark Incom on Missing 
@task_bp.route("/<task_id>/<completion_status>", methods=["PATCH"])
def mark_complete(task_id, completion_status):

    task = Task.query.get(task_id)
    PATH="https://slack.com/api/chat.postMessage"
    if task is None:
        return make_response("", 404)
    
    if completion_status == "mark_complete":
        task.completed_at = date.today()

        #WV4: Send Slack Message
        token=os.environ.get("TOKEN")   
        query_params = {
            "token": token,
            "channel": "task-notifications",
            "text": f"Somone just completed task {task.title}"
        }
        requests.post(PATH, data=query_params)

    if completion_status == "mark_incomplete":
        task.completed_at = None
    db.session.commit()
    
    return jsonify({"task": task.to_dict()})

@goal_bp.route("", methods=["GET", "POST"])
def handle_all_goals():
    goal_response = []

    #WV5: No Saved Goals, One Saved Goals
    if request.method == "GET":
        goals = Goal.query.all() 
        for goal in goals:
            goal_response.append(goal.to_dict())
        return jsonify(goal_response), 200 

    #WV5: Create Goal, Create Goal Missing Title
    if request.method == "POST":
        request_body = request.get_json()
        try:
            new_goal = Goal(title = request_body["title"])
        except KeyError:
            return ({'details': 'Invalid data'}, 400)       
        db.session.add(new_goal)
        db.session.commit()

        return jsonify({"goal": new_goal.to_dict()}), 201 

@goal_bp.route("/<goal_id>", methods=["GET", "DELETE", "PUT", "PATCH"])
def handle_single_goal(goal_id):
    goal_id = int(goal_id)
    goal = Goal.query.get(goal_id)

    #WV5: Get Goal, Get Goal Not Found
    if request.method == "GET":
        if goal is None:
            return make_response("", 404)
        return jsonify({"goal": goal.to_dict()}), 200 

    #WV5: Update Goal, Update Goal Not Found
    elif request.method == "PUT":
        input_data = request.get_json()
        if goal is None:
            return make_response("", 404)
        goal.title = input_data["title"]
        db.session.commit()
        return ({"goal": goal.to_dict()}), 200

    #WV5: Delete Goal Not Found, Delete Goal
    elif request.method == "DELETE":
        if goal is None:
            return make_response("", 404)
        else:
            db.session.delete(goal)
            db.session.commit()
            return ({'details': f'Goal {goal_id} "{goal.title}" successfully deleted'}), 200

@goal_bp.route("/<goal_id>/tasks", methods=["GET", "POST"])
def handle_goal_and_tasks(goal_id):
    goal = Goal.query.get(goal_id)
    request_body = request.get_json()
    
    #W5: Get Tasks, Get Tasks No Goal, Get Tasks No Tasks, Task Include Goal ID
    if request.method == "GET":
        if goal is None:
            return make_response("", 404)       
        task_list = []
        for task in goal.tasks:
            task_list.append(task.to_dict())
        return {
            "id": goal.goal_id,
            "title": goal.title,
            "tasks": task_list
        }, 200
    
    #W5: Post Tasks IDs to Goal, Post Tasks to Goal with Goals
    if request.method == "POST":
        if goal is None:
            return make_response("", 404)
    task_ids = request_body["task_ids"]
    for id in task_ids:
        task = Task.query.get(id)
        task.goal_id = goal_id
        db.session.commit()
    return make_response({"id": int(goal_id), "task_ids": task_ids}), 200
