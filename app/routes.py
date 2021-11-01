from flask import Blueprint, jsonify, make_response, request
from app.models.task import Task
from app.models.goal import Goal
from app import db
from sqlalchemy import desc, asc
import datetime, requests
import os
from dotenv import load_dotenv

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_all_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            error_dict = {"details": "Invalid data"}
            return jsonify(error_dict), 400
        
        new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        completed_at=request_body["completed_at"]
                        )
        
        db.session.add(new_task)
        db.session.commit()

        task_response = {"task": new_task.create_dict()}
        return jsonify(task_response), 201

    elif request.method == "GET":
        name_from_url = request.args.get("name")
        if name_from_url:
            tasks = Task.query.filter_by(name=name_from_url).all()
            if not tasks:
                tasks = Task.query.filter(Task.name.contains(name_from_url))
        sort_query = request.args.get("sort")     
        if sort_query == "desc":
            tasks = Task.query.order_by(desc(Task.title))
        elif sort_query == "asc":
            tasks = Task.query.order_by(asc(Task.title))
        else:
            tasks = Task.query.all()
            
        tasks_response = []
        for task in tasks:
            tasks_response.append(task.create_dict())
        
        if not tasks_response:
            tasks = Task.query.all()
            for task in tasks:
                tasks_response.append(task.create_dict())
        
        return jsonify(tasks_response)

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def tasks_by_id(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify(None), 404
    
    if request.method == "GET":
        task_response = {"task": task.create_dict()}
        return jsonify(task_response), 200
    
    elif request.method == "PUT":
        form_data = request.get_json()

        task.title = form_data["title"]
        task.description = form_data["description"]
        task.iscomplete = None

        db.session.commit()

        task_response = {"task": task.create_dict()}
        return jsonify(task_response), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        
        delete_string = f'Task {task.task_id} "{task.title}" successfully deleted'
        delete_message = {"details": delete_string}
        
        return jsonify(delete_message), 200

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def task_completed(task_id):
    if request.method == "PATCH":
        task = Task.query.get(task_id)
        if not task:
            return jsonify(None), 404
        
        task.completed_at = datetime.datetime.now()
        db.session.commit()
        
        load_dotenv()

        data = {"token": os.environ.get("SLACK_TOKEN"), 
                "channel": os.environ.get("CHANNEL_ID"), 
                "text": f"Someone just completed the task {task.title}"}
        url = os.environ.get("SLACK_URL")
        requests.post(url, data)

        task_response = {"task": task.create_dict()}
        return jsonify(task_response), 200

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def task_incomplete(task_id):
    if request.method == "PATCH":
        task = Task.query.get(task_id)
        if not task:
            return jsonify(None), 404
        
        task.completed_at = None
        db.session.commit()

        task_response = {"task": task.create_dict()}
        return jsonify(task_response), 200


# Start Goals Routes

@goals_bp.route("", methods=["GET", "POST"])
def handle_all_goals():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body:
            error_dict = {"details": "Invalid data"}
            return jsonify(error_dict), 400
        
        new_goal = Goal(title=request_body["title"])
        
        db.session.add(new_goal)
        db.session.commit()

        goal_response = {"goal": new_goal.create_dict()}
        return jsonify(goal_response), 201

    elif request.method == "GET":
        name_from_url = request.args.get("name")
        if name_from_url:
            goals = Goal.query.filter_by(name=name_from_url).all()
            if not goals:
                goals = Goal.query.filter(Goal.name.contains(name_from_url))
        else:
            goals = Goal.query.all()
            
        goals_response = []
        for goal in goals:
            goals_response.append(goal.create_dict())
        
        if not goals_response:
            goals = Goal.query.all()
            for goal in goals:
                goals_response.append(goal.create_dict())
        
        return jsonify(goals_response)

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def goals_by_id(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return jsonify(None), 404
    
    if request.method == "GET":
        goal_response = {"goal": goal.create_dict()}
        return jsonify(goal_response), 200
    
    elif request.method == "PUT":
        form_data = request.get_json()

        goal.title = form_data["title"]

        db.session.commit()

        goal_response = {"goal": goal.create_dict()}
        return jsonify(goal_response), 200

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        
        delete_string = f'Goal {goal.goal_id} "{goal.title}" successfully deleted'
        delete_message = {"details": delete_string}
        
        return jsonify(delete_message), 200

@goals_bp.route("<goal_id>/tasks", methods=["GET"])
def handle_goals_with_tasks(goal_id):
    goal = Goal.query.get(goal_id)

    if not goal:
        return jsonify(None), 404

    if request.method == "GET":
        goal_response = []
        for task in goal.tasks:
            goal_response.append(task.create_dict())
                
        final_response = {"id": goal.goal_id,
                            "title": goal.title,
                            "tasks": goal_response}
        return jsonify(final_response), 200

@goals_bp.route("<goal_id>/tasks", methods=["POST"])
def handle_goals_with_tasks_2(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return jsonify(None), 404
    
    if request.method == "POST":
        form_data = request.get_json()
        task_ids = form_data["task_ids"]
        for id in task_ids:
            task = Task.query.get(id)
            if not task:
                continue
            task.goal = goal
            db.session.commit()

        response = {"id": goal.goal_id,
                    "task_ids": task_ids}

    return response
    