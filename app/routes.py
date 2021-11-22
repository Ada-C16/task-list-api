from flask.wrappers import Request
from app import db
from app.models.task import Task
from app.models.goal import Goal  
from functools import wraps 
from flask import Blueprint, jsonify, make_response, request
from datetime import datetime

#task_list_bp = Blueprint("task_list_bp", __name__)
tasks_bp = Blueprint("tasks", __name__, url_prefix = "/tasks")

# def require_task(endpoint):
#     @wraps(endpoint)
#     def fn(*args, task_id, **kwargs): 
#         task = Task.query.get(task_id)
#         if not task:
#             return jsonify(None), 404
#         return endpoint(*args, task_id, **kwargs)
#     return fn

@tasks_bp.route("", methods = ["GET"])
def manage_tasks():
    #if request.method == "GET":
    sort_query = request.args.get("sort")
    if sort_query == "desc":
        task = Task.query.order_by(Task.title.desc())
    elif sort_query == "asc":
        task = Task.query.order_by(Task.title.asc())
    else:
        task = Task.query.all()
    tasks_response = []
    for task in task: 
        tasks_response.append(
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.completed_at is not None
            }
        )
    return jsonify(tasks_response), 200

@tasks_bp.route("", methods = ["POST"])
def post_tasks():
    request_body = request.get_json()
    if "title" not in request_body: 
        return{
            "details": "Invalid data"
        }, 400
    if "description" not in request_body:
        return jsonify({"details": "Invalid data"}), 400
    if "completed_at" not in request_body:
        return jsonify({"details": "Invalid data"}), 400
    new_task = Task(
        title = request_body["title"],
        description = request_body["description"],
        completed_at = request_body["completed_at"]
    )
    db.session.add(new_task)
    db.session.commit()

    response_body = {
        "task":{
            "id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": new_task.completed_at is not None
        }
    }
    return jsonify(response_body), 201

@tasks_bp.route("/<task_id>", methods = ["GET", "PUT", "DELETE"])
def manage_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify(None), 404
    elif request.method == "GET":
        if task.goal_id: 
            response_body = {"task":(task.combo_dict())}
        else: 
            response_body = {
                "task":{
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": task.completed_at is not None
                }
            }
        return jsonify(response_body), 200
    elif request.method == "PUT":
        request_body = request.get_json()
        
        task.title = request_body["title"]
        task.description = request_body["description"]
        #task.completed_at = request_body["completed_at"]
        
        db.session.commit()
        response_body = {
            "task":{
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.completed_at is not None
            }
        }
        return jsonify(response_body), 200
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return jsonify(
            {
                "details":f'Task {task.id} "{task.title}" successfully deleted'
            }
        ), 200

@tasks_bp.route("/<task_id>/mark_complete", methods = ["PATCH"]) #datetime.now function
def patch_complete(task_id):
    task = Task.query.get(task_id)
    # request_body = request.get_json()  
    # if "title" not in request_body or "description" not in request_body: #or "completed_at" not in request_body:
    if not task:   
        return jsonify(None), 404
    task.completed_at = datetime.utcnow()
    db.session.commit()
    response_body = {
            "task":{
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": True #in the wild maybe don't hardcode True #if statement and then you don't need an opposite function
            }
    }
    return jsonify(response_body), 200

@tasks_bp.route("/<task_id>/mark_incomplete", methods = ["PATCH"]) #datetime.now function
def patch_incomplete(task_id):
    task = Task.query.get(task_id)
    #request_body = request.get_json() #test doesn't have 'request_body'
    # task_id.completed_at = False
    # if "title" not in request_body or "description" not in request_body: #or "completed_at" not in request_body:
    #     return{
    #         "details": "Invalid data"
    #     }, 400
    #db.session.add(task_id)
    if not task:
        return jsonify(None), 404
    task.completed_at = None
    db.session.commit()
    response_body = {
            "task":{
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": False
        }}
    return jsonify(response_body), 200



#wave 5
goals_bp = Blueprint("goals", __name__, url_prefix = "/goals")

@goals_bp.route("", methods = ["GET"])
def manage_goals():
    goal = Goal.query.all()
    goals_response = []
    for goal in goal: 
        goals_response.append(
            {
                "id": goal.goal_id, 
                "title": goal.title,
            }
        )
    return jsonify(goals_response), 200

@goals_bp.route("", methods = ["POST"])
def post_goals():
    request_body = request.get_json()
    if "title" not in request_body:
        return{
            "details": "Invalid data"
        }, 400
    new_goal = Goal(
        title = request_body["title"],
    )
    db.session.add(new_goal)
    db.session.commit()
    response_body = {
        "goal":{
            "id": new_goal.goal_id,
            "title": new_goal.title,
        }
    }
    return jsonify(response_body), 201

@goals_bp.route("/<goal_id>", methods = ["GET", "PUT", "DELETE"])
def whatever_goal(goal_id):
    goal = Goal.query.get(goal_id)
    request_body = request.get_json()
    if not goal: 
        return jsonify(None), 404 
    if request.method == "GET":
        response_body = {
            "goal":{
                "id": goal.goal_id,
                "title": goal.title,
            }
        }
        return jsonify(response_body), 200
    elif request.method == "PUT":
        request_body = request.get_json()
        goal.title = request_body["title"]
        db.session.commit()
        response_body = {
            "goal":{
                "id": goal.goal_id,
                "title": goal.title,
            }
        }
        return jsonify(response_body), 201
    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return jsonify(
            {
                "details":f'Goal {goal.goal_id} "{goal.title}" successfully deleted'
            }
        ), 200

@goals_bp.route("goals/<goal_id>/mark_complete", methods = ["PATCH"]) 
def goal_patch_complete(goal, goal_id):
    request_body = request.get_json()
    goal.completed_at = True
    if "title" not in request_body:
        return{
            "details": "Invalid data"
        }, 400
    db.session.add(goal)
    db.session.commit()
    response_body = {
            "goal":{
                "id": goal.goal_id,
                "title": goal.title,
        }}
    return jsonify(response_body), 201

#wave 6
@goals_bp.route("/<goal_id>/tasks", methods = ["GET", "POST"])
def task_list_to_goal(goal_id):
    goal = Goal.query.get(goal_id)
    request_body = request.get_json()
    if goal == None:
        return jsonify(None), 404
    elif request.method == "GET":
        return jsonify(goal.goal_with_tasks_dict()), 200
    elif request.method == "POST": 
        request_body = request.get_json()
        task_ids = request_body["task_ids"]
    for id in task_ids:
        task = Task.query.get(id)
        task.goal_id = goal_id
    db.session.commit()
    new_tasks = []
    for task in goal.tasks:
        new_tasks.append(task.id)
    response_body = {
        "id": int(goal_id),
        "task_ids": new_tasks
    }
    return jsonify(response_body), 200 







         




