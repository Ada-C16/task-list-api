from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.task import Task
from app.models.goal import Goal
from sqlalchemy import desc, asc, func
from datetime import datetime
import requests, os
from dotenv import load_dotenv
load_dotenv()

task_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goal_bp", __name__, url_prefix="/goals")

@task_bp.route("", methods = ["POST", "GET"])
def handle_tasks():
    if request.method=="POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return jsonify({"details": "Invalid data"}), 400
        else:
            new_task = Task(
                title=request_body["title"],
                description=request_body["description"],
                completed_at= request_body["completed_at"]
            )
            db.session.add(new_task)
            db.session.commit()
            print(new_task)
            return jsonify({"task": new_task.task_dict()}), 201

    elif request.method == "GET":
        sort_query = request.args.get("sort")
        if sort_query == "desc":
            tasks = Task.query.order_by(desc("title"))
            task_list = [task.task_dict() for task in tasks]
        elif sort_query == "asc":
            tasks = Task.query.order_by(asc("title"))
            task_list = [task.task_dict() for task in tasks]
        else:
            tasks = Task.query.all()
            task_list = [task.task_dict() for task in tasks]
        return jsonify(task_list), 200

@task_bp.route("/<task_id>", methods= ["GET", "PUT", "DELETE"])
def handle_one_task(task_id):
    one_task= Task.query.get(task_id)
    if one_task is None:
        return jsonify(one_task), 404
    
    if request.method== "GET":
        if one_task.goal_id:
            return jsonify({"task": one_task.task_dict_with_goal()})
        
        return jsonify({"task": one_task.task_dict()}), 200

    elif request.method == "PUT":
        request_body = request.get_json()
        one_task.title=request_body["title"]
        one_task.description=request_body["description"]
        db.session.commit()
        return jsonify({"task": one_task.task_dict()}), 200

    elif request.method == "DELETE":
        db.session.delete(one_task)
        db.session.commit()
        response_body = f'Task {task_id} "{one_task.title}" successfully deleted'
        return jsonify({"details": response_body}), 200

@task_bp.route("/<task_id>/mark_complete", methods= ["PATCH"])
def mark_complete_task(task_id):
    path = "https://slack.com/api/chat.postMessage"
    one_task= Task.query.get(task_id)

    if one_task is None:
        return jsonify(one_task), 404

    current_time = datetime.now(tz=None)
    one_task.completed_at = current_time
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    requests.post(path, headers= {"Authorization": BOT_TOKEN}, 
    data={"channel" : "slack-api-test-channel", "text": f"Someone just completed the task {one_task.title}"})
    db.session.commit()

    return jsonify({"task": one_task.task_dict()}), 200

@task_bp.route("/<task_id>/mark_incomplete", methods= ["PATCH"])
def mark_incomplete_task(task_id):
    one_task = Task.query.get(task_id)
    if one_task is None:
        return jsonify(one_task), 404
    one_task.completed_at = None
    db.session.commit()
    return jsonify({"task": one_task.task_dict()}), 200

@goal_bp.route("", methods=["GET", "POST"])
def handle_goals():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body:
            return jsonify({"details": "Invalid data"}), 400
        new_goal = Goal(
            title = request_body["title"]
        )
        db.session.add(new_goal)
        db.session.commit()
        return jsonify({"goal": new_goal.goal_dict()}), 201
    
    elif request.method == "GET":
        request_body = request.get_json()
        goals = Goal.query.all()
        goals_response = [goal.goal_dict() for goal in goals]
        return jsonify(goals_response), 200

@goal_bp.route("/<goal_id>", methods = ["GET", "PUT", "DELETE"])
def handle_one_goal(goal_id):
    one_goal = Goal.query.get(goal_id)
    if one_goal is None:
        return jsonify(one_goal), 404

    request_body = request.get_json()
    if request.method == "GET":
        return jsonify({"goal": one_goal.goal_dict()}), 200
    
    elif request.method == "PUT":
        if "title" not in request_body:
            return jsonify({"details": "Invalid data"}), 400
        one_goal.title = request_body["title"]
        db.session.commit()
        return jsonify({"goal": one_goal.goal_dict()}), 200

    elif request.method == "DELETE":
        db.session.delete(one_goal)
        db.session.commit()
        return jsonify({"details": f"Goal {one_goal.goal_id} \"{one_goal.title}\" successfully deleted"})

@goal_bp.route("/<goal_id>/tasks", methods=["POST", "GET"])
def handle_goal_task(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
            return jsonify(goal), 404

    if request.method=="POST":
        request_body = request.get_json()
        for num in request_body["task_ids"]:
            task = Task.query.get(num)
            print(task.task_dict_with_goal())
            task.goal_id = goal_id
            goal.tasks.append(task)
            db.session.commit()
        return jsonify({"id": goal.goal_id, "task_ids": [task["id"] for task in goal.goal_task_dict()["tasks"]]}), 200
    
    elif request.method == "GET":
        return jsonify(goal.goal_task_dict()), 200
