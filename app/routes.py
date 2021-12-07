from flask import Blueprint, jsonify, make_response,request
from app.models.task import Task
from app.models.goal import Goal
from sqlalchemy import asc, desc
from app import db
from datetime import datetime 

tasks_bp = Blueprint("tasks", __name__,url_prefix=("/tasks"))
goals_bp = Blueprint("goals", __name__, url_prefix=("/goals"))

@goals_bp.route("",methods=["POST", "GET"])
def handle_goal():
      if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body:
            return{
                "details": "Invalid data"
            },400

        new_goal = Goal (
            title=request_body["title"]
        )

        db.session.add(new_goal)
        db.session.commit()

        return {
            "goal": {
                "id":new_goal.goal_id,
                "title":new_goal.title
            }
        }, 201
        
      elif request.method == "GET":
        sorting_goals= request.args.get('sort') 
        task_list = None
        if sorting_goals== "desc":
            task_list = Goal.query.order_by(Goal.title.desc()) 
        elif sorting_goals == "asc":
            task_list = Goal.query.order_by(Goal.title.asc()) 
        else: 
            task_list = Goal.query.all()
        goals_response = []
        for goal in list:
            goals_response.append({
            "id": goal.goal_id,
            "title": goal.title,
            })

        return jsonify(goals_response)

@goals_bp.route("/<goal_id>", methods=["GET","PUT","DELETE"])
def handle_goal_get(goal_id):
    goal = Goal.query.get(goal_id)
    if goal == None:
        return ("", 404)

    if request.method == "GET":
        return {
            "goal": {
                "id":goal.goal_id,
                "title":goal.title,          
                }
        }
    if request.method == "PUT":
        form_data = request.get_json()

        goal.title = form_data["title"]
        
        db.session.commit()

        return jsonify({
            "goal":{
                "id":goal.goal_id,
                "title":goal.title,
            }
        }),200

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()

        return jsonify({
            "details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'
        }),200
        

@goals_bp.route("/<goal_id>/tasks", methods=["POST","GET"])
def post_tasked_goal(goal_id):

        goal = Goal.query.get(goal_id)

        if goal == None:
            return (""), 404

        if request.method == "POST":
            request_body = request.get_json()
          
            tasks_instances= []
            for task_id in request_body["task_ids"]:
                tasks_instances.append(Task.query.get(task_id))
            
            goal.tasks = tasks_instances
            
            db.session.commit()

            task_ids = []
            for task in goal.tasks:
                task_ids.append(task.task_id)
             
            response_body = {
                        "id": goal.goal_id,
                        "task_ids": task_ids
                    }
                    
            return jsonify(response_body), 200

        if request.method == "GET":
            tasks_response =[]
            for task in goal.tasks:
                tasks_response.append({
                    "id": task.task_id,
                    "goal_id": task.goal_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": bool(task.completed_at)
                })
            response_body = {
                "id": goal.goal_id,
                "title": goal.title,
                "tasks" : tasks_response
            }
            return jsonify(response_body), 200


@tasks_bp.route("",methods=["GET","POST"])
def handle_task():
    if request.method == "GET": 

        sorting_task = request.args.get('sort') 
        list = None
        if sorting_task == "desc":
            list = Task.query.order_by(Task.title.desc()) # descending method
        elif sorting_task == "asc":
            list = Task.query.order_by(Task.title.asc()) # ascending method
        else: 
            list = Task.query.all()
        tasks_response = []
        for task in list:
            tasks_response.append({
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete" : False
            if task.completed_at == None else True
            })

        return jsonify(tasks_response)

    elif request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return{
                "details": "Invalid data"
            },400

        new_task = Task (
            title=request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"]
        )

        db.session.add(new_task)
        db.session.commit()

        return {
            "task":new_task.task_dict()
        }, 201

def update_completion(task_id, value):
    task = Task.query.get(task_id)
    
    if not task:
        return("Task not found",404)
    
    task.completed_at = value 

    return {
        "task":task.task_dict()
    }, 200 

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):
    return update_completion(task_id, datetime.now())

@tasks_bp.route("/<task_id>/mark_incomplete", methods =["PATCH"])
def mark_incomplete(task_id):
    return update_completion(task_id,None)


@tasks_bp.route("/<task_id>", methods=["GET","PUT","DELETE"])
def handle_task_get(task_id):
    task = Task.query.get(task_id)
    if task == None:
        return ("", 404)

    if request.method == "GET":
        response_body = {}
        response_body["task"] = task.task_dict()

        return jsonify(response_body)

    if request.method == "PUT":
        form_data = request.get_json()

        task.title = form_data["title"]
        task.description = form_data["description"]

        db.session.commit()

        return jsonify({
            "task":{
                "id":task.task_id,
                "title":task.title,
                "description":task.description,
                "is_complete":False if task.completed_at
                == None else True 
            }
        }),200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()

        return jsonify({
            "details": f'Task {task.task_id} "{task.title}" successfully deleted'
        }),200


















