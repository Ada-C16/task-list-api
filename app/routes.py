# from sqlalchemy.orm import query
from app import db
from app.models.task import Task 
from flask import Blueprint, jsonify,request 
from app.models.goal import Goal
from datetime import datetime
import requests
import os

tasks_bp = Blueprint("tasks",__name__, url_prefix=("/tasks" ))
goals_bp = Blueprint("goals",__name__, url_prefix=("/goals"))

@tasks_bp.route("", methods=["GET"])
def get_task():
    sort_query = request.args.get("sort")
    if sort_query == "desc": 
        task = Task.query.order_by(Task.title.desc())
    elif sort_query == "asc":
        task = Task.query.order_by(Task.title.asc())
    else: 
        task = Task.query.all()
    task_response = [task.to_dict()for task in task]
    # task_response = {"task":(task.to_dict())}

    return jsonify(task_response),200


@tasks_bp.route("", methods=[ "POST"])
def handle_task_post():
    if request.method == "POST":
        request_body = request.get_json()
        
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
                    
                    return{
                        "details":"Invalid data"
                    },400


        new_task = Task(
        title=request_body["title"],
        description=request_body["description"],
        completed_at = request_body["completed_at"]
        )

        db.session.add(new_task)
        db.session.commit()

        return {
            "task":{
                "id":new_task.task_id,
                "title":new_task.title,
                "description": new_task.description,
                "is_complete":False if new_task.completed_at == None else True
            }
        },201
       
 
@tasks_bp.route("/<task_id>",methods=["GET","PUT","DELETE"])
def handle_task_id(task_id):
    task = Task.query.get(task_id)
    if task == None:
        return ("", 404)

    if request.method == "GET":
        task_response = {"task":(task.to_dict())}
        return jsonify(task_response),200
       
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
                "is_complete":False if task.completed_at == None else True
            }
        }),200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()   
        return jsonify({
            "details": f'Task {task.task_id} "{task.title}" successfully deleted'
            }),200

#wave 3 
def slack_bot(title):
    slack_post = (f"Someone just completed the task {title}")
    url_slack ="https://slack.com/api/chat.postMessage"
    
    authenticaton=os.environ.get("SLACK_API_KEY")
    query_params={ 
        "channel":'C02J08B9S0N',
        "text":slack_post
    }
    header = {
        "Authorization": authenticaton
    }
    message=requests.post(url_slack,params=query_params,headers=header)
    return message.json()

    
@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_task_mark_complete(task_id):
    task = Task.query.get(task_id) 
   
    if task is not None: 
        
        task.completed_at = datetime.now()
        slack_bot(task.title)
        return jsonify({
            "task":{
                "id":task.task_id,
                "title":task.title,
                "description":task.description,
                "is_complete":bool(task.completed_at)
            }
        }),200

    else: 
        return (""), 404
    
   

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def handle_task_mark_incomplete(task_id):
    task = Task.query.get(task_id) 

    if task is not None:
        if request.method == "PATCH":
                task.completed_at = None
        return jsonify({
            "task":{
                "id":task.task_id,
                "title":task.title,
                "description":task.description,
                "is_complete":bool(task.completed_at)
            }
        }),200

    else: 
        return (""), 404



@goals_bp.route("", methods=["GET"])
def get_goal():
    if request.method == "GET": 
        goals = Goal.query.all()
        goal_response = []
        for goal in goals: 
            goal_response.append(
                {
                    "id":goal.goal_id,
                    "title":goal.title
                }
            ) 
    return jsonify(goal_response),200


@goals_bp.route("", methods=[ "POST"])
def handle_goal_post():
    if request.method == "POST":
        request_body = request.get_json()
        
        if "title" not in  request_body:
                    
            return  jsonify({
            "details":"Invalid data"
        }),400
        else:
            # goal = Goal.query.all()
            new_goal = Goal(
            title=request_body["title"]
            )

            db.session.add(new_goal)
            db.session.commit()

            return jsonify({
                "goal": {
                    "id": new_goal.goal_id,
                    "title":new_goal.title
                }
            }),201
    

@goals_bp.route("/<goal_id>",methods=["GET","PUT","DELETE"])
def handle_goal_id(goal_id):
    goal = Goal.query.get(goal_id)
    if goal == None:
        return ("404 not found"),404
    if request.method == "GET":
        return {
            "goal": {
                "id":goal.goal_id,
                "title": goal.title,
            }
        },200
    if request.method == "PUT":
        form_data = request.get_json()

        goal.title = form_data["title"]
   
        db.session.commit()
       
        return jsonify(
            {
             "goal": {
                "id": goal_id,
                "title": goal.title
            }
        }),200

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()   
        return jsonify({
            "details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'
            }),200


@goals_bp.route("/<goal_id>/tasks", methods=["GET","POST"])
def specific_goal_id(goal_id):
    goal = Goal.query.get(goal_id) 
    if goal == None: 
        return (""),404
    if request.method == "GET":
        tasks_response = [
            
        ]
        for task in goal.tasks:
            tasks_response.append({
                "id":task.task_id,
                "goal_id":task.goal_id,
                "title":task.title,
                "description":task.description,
                "is_complete":bool(task.completed_at)
            })  
        response_body = {
        "id": goal.goal_id,
        "title": goal.title,
        "tasks": tasks_response
        }
        return jsonify(response_body),200
          
    if request.method == "POST": 
        request_body = request.get_json()
        tasks_attributes = []
        for num in request_body["task_ids"]:
            task = Task.query.get(num)
            tasks_attributes.append(task)
        goal.tasks = tasks_attributes
        db.session.commit()
        tasks_ids = []
        for task in goal.tasks:
            tasks_ids.append(task.task_id)
        response_body = {
        "id": goal.goal_id,    
        "task_ids": tasks_ids
    }

        return jsonify(response_body),200 


  
    
