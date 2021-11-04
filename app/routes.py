from flask import Blueprint, jsonify, request, make_response
from app import db
from app.models.task import Task
from app.models.goal import Goal
import datetime
import requests
import os 

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

def make_task_dict(task):
    if task.completed_at:
        completed = True
    else:
        completed = False 

    if task.goal_id:
        return {
                "id" : task.task_id,
                "title" : task.title,
                "description" : task.description,
                "is_complete" : completed,
                "goal_id": task.goal_id
            } 
    else:  
        return {
                "id" : task.task_id,
                "title" : task.title,
                "description" : task.description,
                "is_complete" : completed,
            }

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        # gets task by title
        task_title_query = request.args.get("title")
        sort_query = request.args.get("sort")
        # sorts tasks by asc and desc title name
        if sort_query:
            if sort_query == "desc":
                tasks = Task.query.order_by(Task.title.desc())
            elif sort_query == "asc":
                tasks = Task.query.order_by(Task.title.asc())
        
        # gets task by title
        elif task_title_query: 
            tasks = Task.query.filter(title=task_title_query)
        # gets all tasks
        else: 
            tasks = Task.query.all()

        tasks_response = []
        for task in tasks:
            current_task = make_task_dict(task)
            tasks_response.append(current_task)
            
        return jsonify(tasks_response), 200
    # POST
    else: 
        request_body = request.get_json()
        # if post is missing title, desciption, or completed at, do not post and return 400
        if "description" not in request_body or "title" not in request_body or "completed_at" not in request_body:
            return {"details": "Invalid data"}, 400
        # if all required values are given in the request body, return the task info with 201
        else: 
            new_task = Task(
            title=request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"],
        )
        db.session.add(new_task)
        db.session.commit()

        return {"task": make_task_dict(new_task)}, 201

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_one_task(task_id):
    task = Task.query.get(task_id)
    
    # Guard clause 
    if task is None:
        return make_response("", 404)
    
    if request.method == "GET": 
        return {"task": make_task_dict(task)}, 200
        
    elif request.method == "PUT":
        form_data = request.get_json()
        task.title = form_data["title"]
        task.description = form_data["description"]

        db.session.commit()
        return jsonify({"task": make_task_dict(task)}), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()

        return jsonify({"details": (f'Task {task.task_id} "{task.title}" successfully deleted')}), 200

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_mark_complete(task_id):
    task = Task.query.get(task_id)
    # guard clause
    if task is None:
        return make_response("", 404)
    else: 
        task.completed_at = datetime.datetime.now()
        SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
        print(SLACK_BOT_TOKEN)
    
        data = {
                "channel": "task-notifications",
                "token": SLACK_BOT_TOKEN,
                "text": f"Someone just completed the task {task.title}"
               }

        requests.post('https://slack.com/api/chat.postMessage', data=data)
        
        db.session.commit()

    return jsonify({"task": make_task_dict(task)}), 200
    
@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def handle_mark_incomplete(task_id):
    task = Task.query.get(task_id)
    # guard clause
    if task is None:
        return make_response("", 404)

    task.completed_at = None

    return jsonify({"task": make_task_dict(task)}), 200

def make_goal_dict(goal):

    return {
                "id" : goal.goal_id,
                "title" : goal.title,
            }


@goals_bp.route("", methods=["GET", "POST"])
def handle_goals():
    if request.method == "GET":
        
        goals = Goal.query.all()

        goals_response = []
        for goal in goals:
            current_goal = make_goal_dict(goal)
            goals_response.append(current_goal)
            
        return jsonify(goals_response), 200
    # POST
    else: 
        request_body = request.get_json()
        # if post is missing title, do not post and return 400
        if "title" not in request_body:
            return {"details": "Invalid data"}, 400
        # if all required values are given in the request body, return the task info with 201
        else: 
            new_goal = Goal(
            title=request_body["title"],
        )
        db.session.add(new_goal)
        db.session.commit()

        return {"goal": make_goal_dict(new_goal)}, 201

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_one_goal(goal_id):
    goal = Goal.query.get(goal_id)
    
    # Guard clause 
    if goal is None:
        return make_response("", 404)
    
    if request.method == "GET": 
        return {"goal": make_goal_dict(goal)}, 200
        
    elif request.method == "PUT":
        form_data = request.get_json()
        goal.title = form_data["title"]
        

        db.session.commit()
        return jsonify({"goal": make_goal_dict(goal)}), 200

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()

        return jsonify({"details": (f'Goal {goal.goal_id} "{goal.title}" successfully deleted')}), 200
    
@goals_bp.route("/<goal_id>/tasks", methods=["POST", "GET"], strict_slashes=False)
def handle_tasks_related_to_goals(goal_id):
    ###### POST ######
    goal = Goal.query.get(goal_id)

    if goal is None:
        return make_response("", 404)

    if request.method == "POST":
        request_body = request.get_json()

        task_list = request_body["task_ids"]

        for task_id in task_list:
            task = Task.query.get(task_id)
            task.goal_id == goal_id
            goal.tasks.append(task)
   
        db.session.commit()

        return jsonify({"id": int(goal_id), "task_ids": task_list}), 200

    elif request.method == "GET":
        tasks = Task.query.filter(Task.goal_id == goal_id)

        task_list = []
        for task in tasks:
            one_task = make_task_dict(task)
            task_list.append(one_task)

        return jsonify({
                "id" : goal.goal_id,
                "title" : goal.title,
                "tasks": task_list 
            }), 200
        

        





    


    
