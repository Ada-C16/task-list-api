import os
import requests
from sqlalchemy.orm import query
from app import db
from datetime import datetime
from dotenv import load_dotenv
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint ,jsonify, request


tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@tasks_bp.route("", methods=["GET","POST"])
def handle_tasks():
    if request.method == 'GET':
        sort_query = request.args.get("sort")
        if sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc())
        elif sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc())
        else:
            tasks = Task.query.all()
        tasks_response= []
        for task in tasks:
            tasks_response.append(task.task_dict())

        return jsonify(tasks_response), 200

    elif request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return jsonify({
                "details": "Invalid data"
            }) ,400 
        new_task = Task(
            title = request_body["title"],
            description = request_body["description"],
            completed_at = request_body["completed_at"]
    )

    db.session.add(new_task)
    db.session.commit()

    response_body = {"task":(new_task.task_dict())}
    return jsonify(response_body),201

@tasks_bp.route("/<task_id>", methods= ["GET", "PUT", "DELETE"])
def handle_get_task(task_id): 
    task = Task.query.get(task_id)
    if task is None:
        return jsonify(None), 404
    elif request.method == "GET":
        if task.goal_id:
            response_body = {"task":(task.tasked_dict())}
            return jsonify(response_body), 200
        return jsonify({"task":task.task_dict()}),200

    elif request.method == "PUT":
        request_body = request.get_json()
        task.title = request_body["title"]
        task.description = request_body["description"]
        db.session.commit()

        response_body = {"task":(task.task_dict())}
        return jsonify(response_body), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return jsonify({
        "details": f'Task {task.task_id} "{task.title}" successfully deleted'
    }),200

@tasks_bp.route("/<task_id>/mark_complete", methods= ["PATCH"])
def change_task_complete(task_id): 
    task = Task.query.get(task_id)
    if task is None:
        return jsonify(None), 404

    task.completed_at = datetime.now()

    load_dotenv()

    db.session.commit()
    
    data = {"token": os.environ.get("SLACK_TOKEN"), "channel":os.environ.get("CHANNEL"),
        "text": f"Someone just completed the task {task.title}"}
    url = os.environ.get("URL")
    requests.post(url, data)

    response_body = {"task":(task.task_dict())}
    return jsonify(response_body), 200   
    
@tasks_bp.route("/<task_id>/mark_incomplete", methods= ["PATCH"])
def change_task_incomplete(task_id): 
    task = Task.query.get(task_id)
    if task is None:
        return jsonify(None), 404
    task.completed_at = None

    db.session.commit()

    response_body = {"task":(task.task_dict())}
    return jsonify(response_body), 200

###
@goals_bp.route("", methods= ["GET","POST"])
def get_goal():
    if request.method == "GET":
        goals =  Goal.query.all()
        goals_response = []
        for goal in goals:
            goals_response.append(goal.goal_dict())

        return jsonify(goals_response), 200

    elif request.method == "POST":
        request_body = request.get_json()
        if not "title" in request_body: 
            return jsonify({
                "details": "Invalid data"
            }) ,400 

        new_goal = Goal(
            title = request_body["title"]
            )

    db.session.add(new_goal)
    db.session.commit()

    response_body = {"goal":(new_goal.goal_dict())}
    return jsonify(response_body),201

@goals_bp.route("/<goal_id>", methods= ["GET", "PUT", "DELETE"])
def manage_goal(goal_id): 
    goal = Goal.query.get(goal_id)
    if goal == None:
        return jsonify(None), 404
    elif request.method == "GET":
        response_body = {"goal":(goal.goal_dict())}
        return jsonify(response_body),200

    elif request.method == "PUT":
        request_body = request.get_json()
        goal.title = request_body["title"]
        db.session.commit()

        response_body = {"goal":(goal.goal_dict())}
        return jsonify(response_body), 200

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
    
        return jsonify({"details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'
    }),200

####
@goals_bp.route("/<goal_id>/tasks", methods= ["GET","POST"])
def acquire_tasks_goals(goal_id):
    goal = Goal.query.get(goal_id)
    if goal == None:
        return jsonify(None), 404
    elif request.method == "GET":

        return jsonify(goal.tasked_goal()), 200

    elif request.method == "POST":
        request_body = request.get_json()
        task_ids = request_body["task_ids"] 
        for id in task_ids:
            task = Task.query.get(id)
            task.goal_id = goal_id
        db.session.commit()
        new_tasks = []
        for task in goal.tasks:
            new_tasks.append(task.task_id)
        response_body ={
            "id": int(goal_id),
            "task_ids": new_tasks
        }
        return jsonify(response_body), 200
    
