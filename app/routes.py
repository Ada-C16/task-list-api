from flask import Blueprint, jsonify, make_response, request
from app import db
import requests
import os
from app.models.task import Task
from app.models.goal import Goal
from datetime import datetime
tasks_bp = Blueprint("tasks", __name__, url_prefix = "/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")



@tasks_bp.route("",methods=["POST", "GET"])
def handle_tasks():
    
    # get response body inJSON
    if request.method == "POST":
        request_body = request.get_json()
        # return message if something ismissing
        if 'title' not in request_body or 'description' not in request_body or 'completed_at' not in request_body:
            response_body = {
                'details': 'Invalid data'
            }
            return make_response(jsonify(response_body), 400)
        # making an instance of task after entering info
        new_task = Task(title=request_body["title"],
            description=request_body["description"], 
            completed_at=request_body["completed_at"])

        # add andcommit newtask

        db.session.add(new_task)
        db.session.commit()
        # return task to user
        return {"task": {
            "id": new_task.task_id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete" : (False
            if new_task.completed_at == None else True)
            }},201
    # get all tasks
    elif request.method == "GET":
        title_query = request.args.get("title")
        if title_query:
            tasks = Task.query.filter_by(title=title_query)
        else:
            tasks = Task.query.all()


        sort_query = request.args.get("sort")
        # account for the asc/desc in wave 2(?)
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc())
        elif sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc()) 
        else:
            tasks = Task.query.all()

        # dd each task to be returned
        task_response = []
        for task in tasks:
            task_response.append({
                        "id": task.task_id,
                        "title": task.title,
                        "description": task.description,
                        "is_complete": (False
            if task.completed_at == None else True)})
        return jsonify(task_response)
            
        
        
@tasks_bp.route("/<task_id>",methods=["GET", "PUT","DELETE"])
def handle_one_task(task_id):
    task = Task.query.get(task_id)
    # if taskdoesnt exist, give 404
    if task is None:
        return make_response(f"Task {task_id} not found", 404)

    # acconting for the descrepancy in wave 6 where it was saying to implement goal_id in thisresponse body.
    # fixed this by essentially "if there is a goal id at this task, then return that, if not, then return it without the goal id
    elif request.method == "GET":
        if not task.goal_id:
            return {"task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete" : (False
                if task.completed_at == None else True)
                }},200
        else:
            return {"task": {
            "id": task.task_id,
            "goal_id": task.goal_id,
            "title": task.title,
            "description": task.description,
            "is_complete" : (False
            if task.completed_at == None else True)
            }},200

    elif request.method == "PUT":
        request_body = request.get_json()
        # returns error message ifnot all fields filled in
        if "title" not in request_body or "description" not in request_body:
            return { "message: Requires a title and description and completion status"}, 400
        task.title = request_body["title"]
        task.description = request_body["description"]
        

        # save action and return what you created
        db.session.add(task)
        db.session.commit()
        return {"task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete" : (False
            if task.completed_at == None else True)
            }},200
    # delete task
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return {"details":f'Task {task.task_id} "{task.title}" successfully deleted'}


@tasks_bp.route("/<task_id>/mark_complete", methods = ["PATCH"])
def complete_task(task_id):
    task = Task.query.get(task_id)
    
    # return error message if trying to complete task that doesnt exist
    if task is None:
            return make_response("", 404)
    
    
    if request.method == "PATCH":
        
        # wave 4 slack bot, since we are using GET and it has to do with completing task, put here
        task.completed_at = datetime.now()
        slack_url = 'https://slack.com/api/chat.postMessage'
        slack_params = {
            "channel": "slack-api-test-channel",
            "text": f"Someone just completed the task {task.title}"
        }
        slack_header = {
            "Authorization": f"Bearer {os.environ.get('SLACK_API_TOKEN')}"
        }
        requests.get(url = slack_url, params = slack_params, headers = slack_header)

        # going forward with PPATCh method
        db.session.commit()
        # hard coding the task to be true because this is complete task
        return {"task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete" : True
            }}
    
@tasks_bp.route("/<task_id>/mark_incomplete", methods = ["PATCH"])
def incomplete_task(task_id):
    task = Task.query.get(task_id)
    
    # if trying to mark task that doesnt exist, return none
    if task is None:
            return make_response("", 404)
    
    # hard coding the task to be none because this is incomplete task
    if request.method == "PATCH":
        task.completed_at = None 
        db.session.commit()
        return {"task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete" : False
            }}
    
    
@goals_bp.route("",methods=["POST", "GET"])
def handle_goals():
    
    # will be very similar to handle_tasks just change variable names and delete somefields
    
    # get response body inJSON
    if request.method == "POST":
        request_body = request.get_json()

        if 'title' not in request_body:
            response_body = {
                'details': 'Invalid data'
            }
            return make_response(jsonify(response_body), 400)
        new_goal = Goal(title=request_body["title"]
            )

    # add andcommit newtask

        db.session.add(new_goal)
        db.session.commit()

        return {"goal": {
            "id": new_goal.goal_id,
            "title": new_goal.title
            
            }},201
    elif request.method == "GET":
        title_query = request.args.get("title")
        if title_query:
            goals = Goal.query.filter_by(title=title_query)
        else:
            goals = Goal.query.all()

        # add each goal gotten to a list to be returned
        goal_response = []
        for goal in goals:
            goal_response.append({
                        "id": goal.goal_id,
                        "title": goal.title
                        })
        return jsonify(goal_response)


@goals_bp.route("/<goal_id>",methods=["GET", "PUT","DELETE"])
def handle_one_goal(goal_id):

    # will be very similar to getone task
    goal = Goal.query.get(goal_id)

    if goal is None:
        return make_response(f"Goal {goal_id} not found", 404)
    elif request.method == "GET":
        return {"goal": {
            "id": goal.goal_id,
            "title": goal.title
            
            }},200

            
    elif request.method == "PUT":
        request_body = request.get_json()

        if "title" not in request_body:
            return { "Message: Requires a title "}, 400
        goal.title = request_body["title"]
        
    
        # save action and return what you created
        db.session.add(goal)
        db.session.commit()
        return {"goal": {
            "id": goal.goal_id,
            "title": goal.title,
            
            }},200
    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return {"details":f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}


@goals_bp.route("/<goal_id>/tasks", methods = ["GET", "POST"])
def handle_goal_with_tasks(goal_id):

    goal = Goal.query.get(goal_id)
    
    if goal is None:
        return make_response(f"Goal {goal_id} not found", 404)

    if request.method == "POST":
        
        request_body = request.get_json()
        # linking a goal to tasks(one to many)
        for task_id in request_body["task_ids"]:
            task = Task.query.get(task_id)
            if task is None:
                return make_response("", 404)
            task.goal_id = goal_id
            db.session.commit()
        
        return make_response({
            "id": int(goal_id),
            "task_ids": request_body['task_ids'],
        }, 200)
    # GET method for tasks that have a goal id and the actual goal that goes along with it
    elif request.method == "GET":
        # list comprehension
        tasks = [{
            "id": task.task_id,
            "goal_id" :goal.goal_id,
            "title": task.title,
            "description": task.description,
            "is_complete" : False
            } for task in goal.tasks]

        goal_response = {
            "id": goal.goal_id,
            "title": goal.title,
            
            }
        goal_response["tasks"] = tasks
        return goal_response 