from flask import Blueprint, json, jsonify, request, make_response
from app.models.task import Task
from app.models.goal import Goal
from app import db
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST"])
def post_tasks():
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return make_response({"details":"Invalid data"}, 400)
    
    new_task = Task(
        title = request_body["title"],
        description = request_body["description"],
        completed_at = request_body["completed_at"]
        )

    db.session.add(new_task)
    db.session.commit()
    
    return {"task": {"id": new_task.id,
        "title": new_task.title,
        "description": new_task.description,
        "is_complete": bool(new_task.completed_at)}}, 201

@tasks_bp.route("", methods=["GET"])   
def get_tasks():
        sort_query = request.args.get("sort")
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc()).all()
        elif sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc()).all()
        else:
            tasks = Task.query.all()
    

        tasks_response = []
        for task in tasks: 
            tasks_response.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": bool(task.completed_at)
                })

        return jsonify(tasks_response)


@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])

def handle_task(task_id):
    task = Task.query.get_or_404(task_id)
    if not task:
        return make_response(f"Task {task_id} not found", 404)
        
    if request.method == "GET":
        if not task.goal_id:
            return {"task":
                {"id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": bool(task.completed_at)}}
        else:
            return {"task":
            {"id": task.id,
            "goal_id": task.goal_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)}}

    elif request.method == "PUT":
        request_body = request.get_json()
        task.title = request_body['title']
        task.description = request_body['description']
        if 'completed_at' in request_body:
            task.is_complete = True
        else:
            task.is_complete = False
        db.session.commit()
        
        return {"task": {"id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)}}

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return {"details":(f'Task {task.id} "{task.title}" successfully deleted')}, 200


def slack_bot(title):
    query_path = {'channel':'slack_api_test_channel', 'text': title}
    header = {'Authorization': os.environ.get('BOT')}
    response=requests.post('https://slack.com/api/chat.postMessage', params = query_path, headers= header)
    return response.json()

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_completed_task(task_id):
    task = Task.query.get_or_404(task_id)

    task.completed_at = datetime.utcnow()
    db.session.commit()
    
    slack_bot(task.title)
        
    return jsonify({"task": 
        {"id": task.id,
        "title": task.title,
        "description": task.description,
        "is_complete": bool(task.completed_at)}}), 200

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def handle_incompleted_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed_at = None
    db.session.commit()
        
    return jsonify({"task": 
        {"id": task.id,
        "title": task.title,
        "description": task.description,
        "is_complete": bool(task.completed_at)}}), 200
    

    #task.completed_at = request_body['completed_at']






goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@goals_bp.route("", methods=["POST"])
def post_goals():
    request_body = request.get_json()
    if "title" not in request_body:
        return make_response({"details":"Invalid data"}, 400)
    
    new_goal = Goal(
        title = request_body["title"],
        )

    db.session.add(new_goal)
    db.session.commit()
    
    return {"goal": {"id": new_goal.id,
        "title": new_goal.title}}, 201


@goals_bp.route("", methods=["GET"])   
def get_goals():
        # sort_query = request.args.get("sort")
        # if sort_query == "asc":
        #     goals = Goal.query.order_by(Goal.title.asc()).all()
        # elif sort_query == "desc":
        #     tasks = Task.query.order_by(Task.title.desc()).all()
        # else:
        goals = Goal.query.all()
    
        goals_response = []
        for goal in goals: 
            goals_response.append({
                "id": goal.id,
                "title": goal.title
                })

        return jsonify(goals_response)


@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])

def handle_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if not goal:
        return make_response(f"Goal {goal_id} not found", 404)
        
    if request.method == "GET":
        return {"goal":
            {"id": goal.id,
            "title": goal.title,
            }}

    elif request.method == "PUT":
        request_body = request.get_json()
        goal.title = request_body['title']
        db.session.commit()
        
        return {"goal": {"id": goal.id,
            "title": goal.title,
            }}

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()

        return {"details":(f'Goal {goal.id} "{goal.title}" successfully deleted')}, 200


@goals_bp.route("/<goal_id>/tasks", methods=["GET", "POST"])
def handle_goals_tasks(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if not goal: 
        return make_response ("Goal not found", 404)

    if request.method == "POST":
        request_body = request.get_json()

        all_ids = []
        for task_id in request_body['task_ids']: 
            all_ids.append(Task.query.get(task_id))
        goal.tasks = all_ids

        db.session.commit()

        return {"id": goal.id, "task_ids": request_body['task_ids']}, 200

    elif request.method == "GET":
            tasks_response = []
            for tasks in goal.tasks: 
                tasks_response.append({
                    "id": tasks.id,
                    "goal_id": tasks.goal_id,
                    "title": tasks.title,
                    "description": tasks.description,
                    "is_complete": bool(tasks.completed_at)})
            return jsonify({"id": goal.id,
                "title": goal.title,
                "tasks": tasks_response}), 200


            # "tasks": [{"id": goal.tasks.id,
            #         "goal_id": goal.tasks.goal_id,
            #         "title": goal.tasks.title,
            #         "description": goal.tasks.description,
            #         "is_complete": bool(goal.task.completed_at)}]}



    # return {"task": {"id": new_task.id,
    #     "title": new_task.title,