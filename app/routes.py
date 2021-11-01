from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.task import Task
from app.models.goal import Goal
from sqlalchemy import desc
from datetime import date
import slack
import os 

tasks_bp = Blueprint("task", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goal", __name__, url_prefix="/goals")

def make_task_dict_without_goal_id(task):
    task_dict = {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": True,
    }

    if not task.completed_at:
        task_dict["is_complete"] = False  

    return task_dict 

def make_task_dict_with_goal_id(task):
    task_dict = {
        "id": task.task_id,
        "goal_id" : task.goal_id,
        "title": task.title,
        "description": task.description,
        "is_complete": True,
    }

    if not task.completed_at:
        task_dict["is_complete"] = False  

    return task_dict 

def make_goal_dict(goal):
    return {
        "id": goal.goal_id,
        "title": goal.title,
    }

@tasks_bp.route("", methods=["GET", "POST"])
def tasks():
    if request.method == "GET":
        sort_query = request.args.get("sort")
        if sort_query:
            if sort_query == "asc":
                tasks = Task.query.order_by("title") 
            else:
                tasks = Task.query.order_by(desc("title")) 
        else: 
            tasks = Task.query.all()

        tasks_response = [make_task_dict_without_goal_id(task) for task in tasks]     
        return jsonify(tasks_response), 200

    elif request.method == "POST": 
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body\
        or "completed_at" not in request_body:
            return { "details" : "Invalid data" }, 400

        new_task = Task(
            title=request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"]
        )

        db.session.add(new_task)
        db.session.commit()
        return jsonify({ "task" : make_task_dict_without_goal_id(new_task) }), 201

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def task(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return make_response("", 404)
    
    if request.method == "GET":
        return jsonify({ "task" : make_task_dict_with_goal_id(task) }), 200

    elif request.method == "PUT":
        request_data = request.get_json()
        task.title = request_data["title"]
        task.description = request_data["description"]
        if not task.completed_at:
            completed_or_not = False
        else:
            completed_or_not = True 

        db.session.commit()

        task_dict = {
                "id": task.task_id,
                "title": request_data["title"],
                "description": request_data["description"],
                "is_complete": completed_or_not 
            }

        return jsonify({ "task" : task_dict }), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return jsonify(
            { "details" : f"Task {task.task_id} \"{task.title}\" successfully deleted" }
        ), 200

@tasks_bp.route("/<task_id>/<completion_mark>", methods=["PATCH"])
def mark_task_complete_or_incomplete(task_id, completion_mark):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    if completion_mark == "mark_complete":
        task.completed_at = date.today()
        # Post slack-api-test-channel 
        client = slack.WebClient(token=os.environ.get("SLACK_TOKEN"))
        client.chat_postMessage(
            channel='#slack-api-test-channel',
            text=f"Someone just completed the task {task.title}" 
        )
    elif completion_mark == "mark_incomplete":
        task.completed_at = None 

    return jsonify({ "task" : make_task_dict_without_goal_id(task) }), 200 

@goals_bp.route("", methods=["GET", "POST"])
def goals():
    if request.method == "GET":
        goals = Goal.query.all()
        goals_response = [make_goal_dict(goal) for goal in goals]     
        return jsonify(goals_response), 200

    elif request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body:
            return { "details" : "Invalid data" }, 400

        new_goal = Goal(title=request_body["title"])
        db.session.add(new_goal)
        db.session.commit()
        return jsonify({ "goal" : make_goal_dict(new_goal) }), 201

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def goal(goal_id):
    goal = Goal.query.get(goal_id)

    if goal is None:
        return make_response("", 404)
    
    if request.method == "GET":
        return jsonify({ "goal" : make_goal_dict(goal) }), 200

    elif request.method == "PUT":
        request_data = request.get_json()
        goal.title = request_data["title"]

        db.session.commit()

        goal_dict = {
                "id": goal.goal_id,
                "title": request_data["title"],
            }

        return jsonify({ "goal" : goal_dict }), 200

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return { "details" : f"Goal {goal.goal_id} \"{goal.title}\" successfully deleted" }, 200

@goals_bp.route("/<goal_id>/tasks", methods=["GET", "POST"])
def goal_tasks(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response("", 404)

    if request.method == "GET":
        tasks = Task.query.filter_by(goal_id=goal.goal_id)
        tasks_response = [make_task_dict_with_goal_id(task) for task in tasks]
        return jsonify({
            "id": goal.goal_id,
            "title": goal.title,
            "tasks": tasks_response
            }), 200  
    else:
        request_body = request.get_json() # i.e. "task_ids": [1, 2, 3]
        for task_id in request_body["task_ids"]:
            task = Task.query.get(task_id)
            task.goal_id = goal.goal_id
        return jsonify({
            "id": goal.goal_id,
            "task_ids": request_body["task_ids"]
            }), 200