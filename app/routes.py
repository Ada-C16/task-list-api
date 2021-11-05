from flask import Blueprint, jsonify, request, make_response, abort
from app.models.task import Task
from app.models.goal import Goal
from app import db
from sqlalchemy import desc
from datetime import date, time, datetime
import requests
import os

# assign tasks_bp to the new Blueprint instance
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
# assign goals_bp to the new Blueprint instance
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")
# assign slack path for slack integration
slack_path = "https://slack.com/api/chat.postMessage"



@tasks_bp.route("", methods=["POST"])
def post_one_task():
# request_body will be the user's input, converted to json. it will be a new record 
# for the db, with all fields (a dict)
    request_body = request.get_json()
    if 'title' not in request_body or 'description' \
    not in request_body or 'completed_at' not in request_body:
        return make_response({"details": "Invalid data"}, 400)
    else:
# taking infor fr request_body and converting it to new Task object    
        new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        completed_at=request_body["completed_at"])
# committing changes to db
        db.session.add(new_task)
        db.session.commit()
        # using is_completed to hold Boolean value of datetime which is the data type
        # for new_task.completed_at, essentially converting from Null to False
        is_complete = new_task.completed_at is not None
        return make_response({"task": {"id": new_task.task_id,
                                        "title": new_task.title,
                                        "description": new_task.description,
                                        "is_complete": is_complete}}, 201)
                                    
@tasks_bp.route("", methods=["GET"])
def working_with_all_tasks():
    title_query = request.args.get('title') #query params for wave2
    order_by_query = request.args.get('sort')
    if title_query:
    # filter_by returns a list of objects/ records that match the query params
    
        tasks = Task.query.filter_by(title = title_query)
    # what part of the Task.query is actually accessing the DB?
    elif order_by_query == 'asc':
    # getting all tasks fr the db
        tasks = Task.query.order_by(Task.title).all()
    # query_all return list of objects. loop through objects and add to empt list, task_response
    # as requested formatted JSON objects
    elif order_by_query == 'desc':
        tasks = Task.query.order_by(desc(Task.title)).all()
    # this else covers any search for all tasks, without any query params
    else:
        tasks = Task.query.order_by(Task.title).all()
    
    task_response = []
    # looping through each task, converting to requested format (dict) and adding to
    # task_response which will be list of dicts
    for task in tasks:
        is_complete = task.completed_at is not None
        task_response.append({
        'id': task.task_id,
        'title': task.title,
        'description': task.description,
        'is_complete': is_complete})
    
    return jsonify(task_response), 200

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE", "PATCH"])
def CRUD_one_task(task_id):
    task = Task.query.get(task_id) #either get Task back or None
    if task is None:
# couldn't figure out another way to return no response body, researched abort
        abort(404) 
# returning the object's info in the desired data structure format
    is_complete = task.completed_at is not None
    if request.method == "GET":
        if task.goal_id:
            return make_response({"task": {"id": task.task_id,
                                    "title": task.title,
                                    "description": task.description,
                                    "goal_id": task.goal_id,
                                    "is_complete": is_complete}}, 200)
        else:
            return make_response({"task": {"id": task.task_id,
                        "title": task.title,
                        "description": task.description,
                        "is_complete": is_complete}}, 200)
    elif request.method == "PUT":
    # form data is a local variable to hold the body of the HTTP request
        form_data = request.get_json()
    # reassigning attributes of the task object using the dict values that came over 
    # in the request body
        task.title = form_data["title"]
        task.description = form_data["description"]
        task.completed_at = task.completed_at

        db.session.commit()

        return make_response({"task": {"id": task.task_id,
                                    "title": task.title,
                                    "description": task.description,
                                    "is_complete": is_complete}}, 200)
    # patch will change just one part of the record, not the whole record
    elif request.method == "PATCH":
        form_data = request.get_json()
        if "title" in form_data:
            task.title = form_data["title"]
        if "description" in form_data:
            task.description = form_data["description"]
        
        db.session.commit()
        return make_response({"task": {"id": task.task_id,
                                    "title": task.title,
                                    "description": task.description,
                                    "is_complete": is_complete}}, 200)
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return make_response({'details': 
        f'Task {task.task_id} "{task.title}" successfully deleted'}, 200)
        
@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_task_complete(task_id):
# setting current datetime to time_stamp to use to mark task.completed_at
    time_stamp = datetime.now()
    task = Task.query.get(task_id) #either get Task back or None
    if task is None:
        abort(404) 
    else:
        task.completed_at = time_stamp
# now db record shows timestamp for completed_at
    db.session.commit()
    is_complete = task.completed_at is not None
    
    try:
        query_params = {"channel": "slack-api-test-channel",
        "text": f"Someone just completed the task {task.title}"}
        header_param = {"Authorization": "Bearer "+ os.environ.get("slack_oauth_token")}
        slack_post_body = requests.post(slack_path, params=query_params, headers= header_param)
    except TypeError:
        pass
# response body doesn't want to show timestamp, just True, so changing is_complete to True
    return make_response({"task": {"id": task.task_id,
                                    "title": task.title,
                                    "description": task.description,
                                    "is_complete": is_complete}}, 200)

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_task_incomplete(task_id):
    task = Task.query.get(task_id) #either get Task back or None
    if task is None:
        abort(404) 
    else:
        task.completed_at = None
    db.session.commit()
    is_complete = task.completed_at is not None
    return make_response({"task": {"id": task.task_id,
                                    "title": task.title,
                                    "description": task.description,
                                    "is_complete": is_complete}}, 200)
# Here we are beginning the code for the Goal Model/ Table    
@goals_bp.route("", methods=["POST"])
def post_one_goal():
    request_body = request.get_json()
    if 'title' not in request_body :
        return make_response({"details": "Invalid data"}, 400)
    else:
        new_goal = Goal(title=request_body["title"])

        db.session.add(new_goal)
        db.session.commit()
        return make_response({"goal": {"id": new_goal.goal_id,
                                        "title": new_goal.title}}, 201)

@goals_bp.route("", methods=["GET"])
def working_with_all_goals():
    title_query = request.args.get('title') #query params
    order_by_query = request.args.get('sort')
    if title_query:
    # filter_by returns a list of objects/ records that match the query params
    
        goals = Goal.query.filter_by(title = title_query)
    # what part of the Goal.query is actually accessing the DB?
    elif order_by_query == 'asc':
        goals = Goal.query.order_by(Goal.title).all()
    # query_all return list of objects. loop through objects and add to empt list, task_response
    # as requested formatted JSON objects
    elif order_by_query == 'desc':
    # chaining methods of Goal together    
        goals = Goal.query.order_by(desc(Goal.title)).all()
    # this else covers any search for all goals, without any query params
    else:
        goals = Goal.query.order_by(Goal.title).all()
    
    goal_response = []
    for goal in goals:
        goal_response.append({
        'id': goal.goal_id,
        'title': goal.title})
    return jsonify(goal_response), 200    

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def CRUD_one_goal(goal_id):
    goal = Goal.query.get(goal_id) #either get Goal back or None
# this guard clause checks if the goal_id exists, if not, it will give 404
    if goal is None:
# couldn't figure out another way to return no response body, researched abort
        abort(404) 
# returning the object's info in the desired data structure format
    if request.method == "GET":
        return make_response({"goal": {"id": goal.goal_id,
                                    "title": goal.title}}, 200)
    elif request.method == "PUT":
    # form data is a local variable to hold the body of the HTTP request
        form_data = request.get_json()
    # reassigning attributes of the goal object using the dict values that came over 
    # in the request body
        goal.title = form_data["title"]
        db.session.commit()

        return make_response({"goal": {"id": goal.goal_id,
                                    "title": goal.title}}, 200)
    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return make_response({'details': 
        f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}, 200)
# given one goal id, find 3 task ids and associate them with the goal by changing
# their goal_id column(Foreign Key) from nullable to the goal_id of the goal to be associated    
@goals_bp.route("/<goal_id>/tasks", methods=["POST", "GET"]) 
def associate_tasks_with_goal(goal_id):
    request_body = request.get_json()
    tasks = Task.query.all()
    goal = Goal.query.get(goal_id) #either get Goal back or None
# this guard clause checks if the goal_id exists, if not, it will give 404
    if goal is None:
        abort(404) 
    if request.method == "POST":
# checking all tasks, if that task_id is in the list which came from Request_body, reassign value
# of task.goal_id (need to convert to int bc goal_id is user input and is a string)
        for task in tasks:
            if task.task_id in request_body["task_ids"]:
                task.goal_id = int(goal_id)
            db.session.commit()
        return make_response({"id": int(goal_id), "task_ids": request_body["task_ids"]}, 200)   
    elif request.method == "GET":
    # getting all tasks (attribute of Goal object) associated with given goal_id
        goals_tasks = Goal.query.get(goal_id).tasks
        
        task_response = []
        for task in goals_tasks:
            is_complete = task.completed_at is not None
            task_response.append({
            'id': task.task_id,
            'goal_id': task.goal_id,
            'title': task.title,
            'description': task.description,
            'is_complete': is_complete})
    
        return make_response({"id": goal.goal_id, "title": goal.title, "tasks": task_response}, 200)


