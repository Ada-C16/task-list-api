from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, request, make_response, jsonify
import requests
import os

def task_response(table):
    response = {
                "id": table.task_id,
                "title": table.title,
                "description": table.description,
                "is_complete": bool(table.completed_at)
            }
    if table.goal_id:
        response["goal_id"] = table.goal_id
    return response

def goal_response(table):
    response = {
            "id": table.goal_id,
            "title": table.title,
            } 
    return response

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        title_query = request.args.get("title")
        if title_query:
            tasks = Task.query.filter_by(title=title_query)
        else:
            tasks = Task.query.all()
        
        sort_query = request.args.get("sort")
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc())
        elif sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc()) 
        else:
            tasks = Task.query.all()
        
        tasks_response = [task_response(task) for task in tasks]
        return make_response(jsonify(tasks_response), 200)
    
    
    elif request.method == "POST":
        request_body = request.get_json()
        try: 
            new_task = Task(
                title = request_body["title"],
                description = request_body["description"],
                completed_at = request_body["completed_at"]
            )
        except:
            return make_response({"details": "Invalid data"}, 400)

        db.session.add(new_task)
        db.session.commit()

        return make_response({ "task": task_response(new_task) }, 201)


@tasks_bp.route("/<task_id>", methods = ["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
            return make_response("", 404)
    if request.method == "GET":
        task_return = task_response(task)
        return { "task" : task_return }

    
    elif request.method == "PUT":
        form_data = request.get_json()
        if form_data.get("title"):
            task.title = form_data["title"]
        if form_data.get("description"):
            task.description = form_data["description"]
        if form_data.get("completed_at"):
            task.completed_at = form_data["completed_at"] 
        db.session.commit()
        return { "task": task_response(task) }


    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()

        return make_response({
        "details": f'Task {task.task_id} "{task.title}" successfully deleted'
    })

@tasks_bp.route("/<task_id>/mark_complete", methods = ["PATCH"])
def complete_task(task_id):
    task = Task.query.get(task_id)
    
    
    if task is None:
            return make_response("", 404)
    
    
    if request.method == "PATCH":
        
        from datetime import datetime
        task.completed_at = datetime.now()
        
        slack_url = 'https://slack.com/api/chat.postMessage'
        slack_params = {
            "channel": "task-notifications",
            "text": f"Someone just completed the task {task.title}"
        }
        slack_header = {
            "Authorization": f"Bearer {os.environ.get('SLACK_API_TOKEN')}"
        }
        requests.get(url = slack_url, params = slack_params, headers = slack_header)

        db.session.commit()

        return make_response({ "task": task_response(task) })



@tasks_bp.route("/<task_id>/mark_incomplete", methods = ["PATCH"])
def incomplete_task(task_id):
    task = Task.query.get(task_id)
    
    
    if task is None:
            return make_response("", 404)
    
    
    if request.method == "PATCH":
        task.completed_at = None
        db.session.commit()
        return make_response({ "task": task_response(task) })


goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@goals_bp.route("", methods=["GET", "POST"])
def handle_goals():
    if request.method == "GET":
        title_query = request.args.get("title")
        if title_query:
            goals = Goal.query.filter_by(title=title_query)
        else:
            goals = Goal.query.all()

        goals_response = [goal_response(goal) for goal in goals]

        return make_response(jsonify(goals_response), 200)
    
    
    elif request.method == "POST":
        request_body = request.get_json()
        try: 
            new_goal = Goal(
                title = request_body["title"],
            )
        except:
            return make_response({"details": "Invalid data"}, 400)

        db.session.add(new_goal)
        db.session.commit()

        return make_response({"goal": goal_response(new_goal)}, 201)


@goals_bp.route("/<goal_id>", methods = ["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal = Goal.query.get(goal_id)
    
    
    if goal is None:
            return make_response("", 404)
    
    
    if request.method == "GET":
        return {"goal": goal_response(goal)}
    
    
    elif request.method == "PUT":
        form_data = request.get_json()
        if form_data.get("title"):
            goal.title = form_data["title"]
        db.session.commit()
        return make_response({"goal": goal_response(goal)})


    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()

        return make_response({
        "details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'
    })


@goals_bp.route("/<goal_id>/tasks", methods = ["GET", "POST"])
def handle_goal_with_tasks(goal_id):

    goal = Goal.query.get(goal_id)
    
    if goal is None:
        return make_response("", 404)

    if request.method == "POST":
        
        form_data = request.get_json()

        for task_id in form_data["task_ids"]:
            task = Task.query.get(task_id)
            if task is None:
                return make_response("", 404)
            task.goal_id = goal_id
            db.session.commit()
        
        return make_response({
            "id": int(goal_id),
            "task_ids": form_data["task_ids"]
        }, 200)
    
    elif request.method == "GET":
        tasks = [task_response(task) for task in goal.tasks]

        response = goal_response(goal)
        response["tasks"] = tasks
        return response 